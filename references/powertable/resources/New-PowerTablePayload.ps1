[CmdletBinding(DefaultParameterSetName = 'SingleTable')]
param(
    [Parameter(Mandatory = $true)][string]$WorkspaceName,
    [Parameter(Mandatory = $true)][string]$DatabaseName,
    [Parameter(Mandatory = $true)][string]$PlanName,
    [Parameter(Mandatory = $true)][string]$ConnectionId,
    [Parameter(Mandatory = $true)][string]$OutputPath,
    [Parameter(Mandatory = $true, ParameterSetName = 'SingleTable')][string]$SchemaName,
    [Parameter(Mandatory = $true, ParameterSetName = 'SingleTable')][string]$TableName,
    [Parameter(Mandatory = $true, ParameterSetName = 'SingleTable')][string]$SheetName,
    [Parameter(Mandatory = $true, ParameterSetName = 'MultipleTables')][string]$TableSelectionsJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$fabricResource = 'https://api.fabric.microsoft.com'
$sqlcmd = Get-Command sqlcmd -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source
$powerTableColumnType = @{
    TEXT = 1
    SINGLE_SELECT = 2
    MULTI_SELECT = 3
    DATE = 4
    NUMBER = 6
    PERSON = 7
    TIME = 8
    LAST_UPDATED_BY = 9
    LAST_UPDATED_AT = 10
    CHECKBOX = 11
    DATETIME = 12
    DECIMAL = 13
    IMAGE = 14
    URL = 15
    EMAIL = 16
    FORMULA = 17
    BUTTON_COLUMN = 18
    CURRENCY = 19
    PHONE_NUMBER = 20
    RATING = 21
    ATTACHMENT = 22
    PERCENT_SLIDER = 23
    PERCENT = 24
}

if ($PSCmdlet.ParameterSetName -eq 'MultipleTables') {
    try {
        $tableSelections = @($TableSelectionsJson | ConvertFrom-Json -Depth 20 -ErrorAction Stop)
    } catch {
        throw "TableSelectionsJson is not valid JSON: $($_.Exception.Message)"
    }
} else {
    $tableSelections = @(
        [pscustomobject]@{
            schemaName = $SchemaName
            tableName = $TableName
            sheetName = $SheetName
        }
    )
}
if ($tableSelections.Count -eq 0) {
    throw 'Select at least one source table.'
}
if ($tableSelections.Count -gt 5) {
    throw "Select no more than five source tables; received $($tableSelections.Count)."
}

if ([string]::IsNullOrWhiteSpace($sqlcmd)) {
    throw 'Go sqlcmd was not found on PATH. Install Go sqlcmd and add its directory to PATH.'
}

function Invoke-FabricJson {
    param(
        [Parameter(Mandatory = $true)][string]$Method,
        [Parameter(Mandatory = $true)][string]$Url
    )

    $raw = & az rest `
        --method $Method `
        --resource $fabricResource `
        --url $Url `
        --headers 'x-ms-fabric-skill=fabric-plan-skill' `
        --output json
    if ($LASTEXITCODE -ne 0) {
        throw "Fabric request failed: $Method $Url"
    }
    return $raw | ConvertFrom-Json
}

function New-RecordGuid {
    return ([guid]::NewGuid().ToString()).ToUpperInvariant()
}

function Get-NormalizedColumnIntentName {
    param([Parameter(Mandatory = $true)][string]$Name)

    return (($Name -creplace '([a-z0-9])([A-Z])', '$1_$2') -replace '[^A-Za-z0-9]+', '_').Trim('_').ToLowerInvariant()
}

function Test-CurrencyIntentColumnName {
    param([Parameter(Mandatory = $true)][string]$Name)

    $intentName = Get-NormalizedColumnIntentName -Name $Name
    $lastToken = @($intentName -split '_')[-1]
    return $lastToken -in @(
        'amount', 'price', 'cost', 'salary', 'wage', 'revenue', 'income',
        'expense', 'fee', 'charge', 'budget', 'balance', 'cents', 'pennies'
    ) -or $intentName -match '(^|_)(money|currency)_(value|amount)$'
}

function Test-CheckboxCandidateColumn {
    param([Parameter(Mandatory = $true)][object]$Column)

    if ($Column.foreignKeyName) {
        return $false
    }
    $singleSelectProperty = $Column.PSObject.Properties['singleSelectConfigured']
    if ($singleSelectProperty -and [bool]$singleSelectProperty.Value) {
        return $false
    }
    return [string]$Column.dataType -match '^(bit|boolean|tinyint|smallint|int|bigint|char|nchar|varchar|nvarchar)$'
}

function Get-PowerTableColumnType {
    param([Parameter(Mandatory = $true)][object]$Column)

    if ($Column.foreignKeyName) {
        return $powerTableColumnType.SINGLE_SELECT
    }
    $singleSelectProperty = $Column.PSObject.Properties['singleSelectConfigured']
    if ($singleSelectProperty -and [bool]$singleSelectProperty.Value) {
        return $powerTableColumnType.SINGLE_SELECT
    }
    $checkboxProperty = $Column.PSObject.Properties['checkboxConfigured']
    if ($checkboxProperty -and [bool]$checkboxProperty.Value) {
        return $powerTableColumnType.CHECKBOX
    }

    switch -Regex ($Column.dataType) {
        '^date$' { return $powerTableColumnType.DATE }
        '^(datetime|datetime2|datetimeoffset|smalldatetime)$' { return $powerTableColumnType.DATETIME }
        '^time$' { return $powerTableColumnType.TIME }
        '^(bit|boolean)$' {
            throw "Boolean column '$($Column.name)' was not resolved to a valid checkbox mapping."
        }
        '^(decimal|numeric|float|real|double|double precision)$' {
            if (Test-CurrencyIntentColumnName -Name ([string]$Column.name)) {
                return $powerTableColumnType.CURRENCY
            }
            return $powerTableColumnType.DECIMAL
        }
        '^(money|smallmoney)$' { return $powerTableColumnType.CURRENCY }
        '^(tinyint|smallint|int|bigint)$' {
            $intentName = Get-NormalizedColumnIntentName -Name ([string]$Column.name)
            $lastToken = @($intentName -split '_')[-1]
            if ($lastToken -in @('rating', 'ratings', 'star', 'stars') -or
                $intentName -match '(^|_)(rating|ratings|star_rating)_(value|score)$') {
                return $powerTableColumnType.RATING
            }
            if (Test-CurrencyIntentColumnName -Name ([string]$Column.name)) {
                return $powerTableColumnType.CURRENCY
            }
            return $powerTableColumnType.NUMBER
        }
        default { return $powerTableColumnType.TEXT }
    }
}

function ConvertTo-PowerTableColumnConfig {
    param([Parameter(Mandatory = $true)][object]$Column)

    $type = Get-PowerTableColumnType -Column $Column
    $displayName = (($Column.name -split '_') | ForEach-Object {
        if ($_.Length -eq 0) { return $_ }
        $_.Substring(0, 1).ToUpperInvariant() + $_.Substring(1)
    }) -join ' '

    $meta = [ordered]@{
        dbMeta = [ordered]@{
            isCompositeUnique = $false
            isIdentity = [bool]$Column.identity
            isNullable = [bool]$Column.nullable
            isPrimaryKey = [bool]$Column.primaryKey
            isUnique = $false
            maxLength = [int]$Column.maxLength
            type = [string]$Column.dataType
            uniqueConstraintName = $null
        }
        defaultValue = ''
        defaultValueType = 'NONE'
        isPrimaryKey = [bool]$Column.primaryKey
        resetToDefaultOnRowModify = $false
        updateValueOnRowModify = $false
    }
    if ($type -in @(
        $powerTableColumnType.NUMBER,
        $powerTableColumnType.DECIMAL,
        $powerTableColumnType.CURRENCY,
        $powerTableColumnType.RATING
    )) {
        $meta.dbMeta['precision'] = [int]$Column.precision
        $meta.dbMeta['scale'] = [int]$Column.scale
    }
    if ($type -eq $powerTableColumnType.SINGLE_SELECT) {
        $meta['defaultValue'] = $null
        $meta['fcVisualIdColumnName'] = $null
        $meta['fcVisualLabelColumnName'] = $null
        $meta['fcVisualName'] = $null
        $meta['isFilterBasedOnAnotherValue'] = $false
        $meta['options'] = @()
        $meta['optionLinking'] = [ordered]@{
            filters = @()
            lookupConfig = @()
        }
        if ($Column.foreignKeyName) {
            $meta.optionLinking['lookupConfig'] = @(
                [ordered]@{
                    id = [string]$Column.referencedColumn
                    label = [string]$Column.lookupLabelColumn
                    linkingColumn = [string]$Column.referencedColumn
                    order = 0
                    schema = [string]$Column.referencedSchema
                    table = [string]$Column.referencedTable
                }
            )
            $meta['selectionMethod'] = 'LOAD_FROM_DATABASE'
        } else {
            $meta['selectionMethod'] = 'DISTINCT_VALUES'
        }
    } elseif ($type -eq $powerTableColumnType.TEXT) {
        $meta['maximumAllowedLength'] = ''
        $meta['textFieldColumnType'] = 'Any Value'
    } elseif ($type -eq $powerTableColumnType.DATE) {
        $meta['format'] = 'DEFAULT_LOCALE'
        $meta['max'] = ''
        $meta['min'] = ''
    } elseif ($type -eq $powerTableColumnType.DATETIME) {
        $meta['format'] = 'DEFAULT_LOCALE_TIME'
        $meta['max'] = ''
        $meta['min'] = ''
    } elseif ($type -eq $powerTableColumnType.TIME) {
        $meta['format'] = 'DEFAULT_LOCALE'
        $meta['max'] = ''
        $meta['min'] = ''
    } elseif ($type -eq $powerTableColumnType.CHECKBOX) {
        $meta['checkedValue'] = $Column.checkedValue
        $meta['sanitizedDefaultValue'] = $Column.unCheckedValue
        $meta['unCheckedValue'] = $Column.unCheckedValue
    } elseif ($type -in @(
        $powerTableColumnType.DECIMAL,
        $powerTableColumnType.CURRENCY
    )) {
        $meta['max'] = ''
        $meta['min'] = ''
        $meta['noOfDecimals'] = [string]$Column.scale
        $meta['prefix'] = ''
        $meta['suffix'] = ''
        $meta['thousandSeparator'] = ''
        if ($type -eq $powerTableColumnType.CURRENCY) {
            $meta['currency'] = [ordered]@{
                displayName = 'US Dollar ($ - USD)'
                value = 'USD'
            }
        }
    } else {
        $meta['max'] = ''
        $meta['min'] = ''
        $meta['prefix'] = ''
        $meta['suffix'] = ''
        $meta['thousandSeparator'] = ''
    }

    return [ordered]@{
        allowEdit = if ($Column.identity -or ($Column.PSObject.Properties['readOnly'] -and [bool]$Column.readOnly)) { 0 } else { 1 }
        columnGuid = [string]$Column.name
        columnMeta = $meta
        columnName = [string]$Column.name
        columnType = $type
        description = ''
        displayName = if ($Column.foreignKeyName) { $displayName -replace '\s+Key$', '' } else { $displayName }
        hideColumn = 0
        # Generated values (rowversion, computed) are never user-supplied, so they cannot be required.
        mandatory = if ($Column.nullable -or ($Column.PSObject.Properties['readOnly'] -and [bool]$Column.readOnly)) { 0 } else { 1 }
        recordGuid = New-RecordGuid
        visualColumnType = if ($type -eq $powerTableColumnType.SINGLE_SELECT) { 3 } else { 1 }
    }
}

function Get-UniqueSheetName {
    param(
        [Parameter(Mandatory = $true)][string]$RequestedName,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][System.Collections.Generic.HashSet[string]]$AllocatedNames
    )

    $baseName = $RequestedName.Trim()
    if ([string]::IsNullOrWhiteSpace($baseName)) {
        throw 'A sheet name cannot be empty.'
    }

    $candidate = $baseName
    $suffix = 2
    while (-not $AllocatedNames.Add($candidate)) {
        $candidate = "$baseName ($suffix)"
        $suffix++
    }
    return $candidate
}

function Get-TableColumns {
    param(
        [Parameter(Mandatory = $true)][string]$Server,
        [Parameter(Mandatory = $true)][string]$SqlDatabaseName,
        [Parameter(Mandatory = $true)][string]$SchemaName,
        [Parameter(Mandatory = $true)][string]$TableName
    )

    $escapedSchema = $SchemaName.Replace("'", "''")
    $escapedTable = $TableName.Replace("'", "''")
    $query = @"
SET NOCOUNT ON;
SELECT c.column_id, c.name, ty.name, c.max_length, c.precision, c.scale,
       c.is_nullable, c.is_identity,
       CASE WHEN pk.column_id IS NULL THEN 0 ELSE 1 END,
       fk.name,
       fkmeta.constraint_column_count,
       rsch.name,
       rt.name,
       rc.name,
       labelcol.name,
       CASE WHEN c.is_computed = 1 OR c.generated_always_type <> 0 OR ty.name IN ('timestamp', 'rowversion') THEN 1 ELSE 0 END
FROM sys.columns c
JOIN sys.types ty ON c.user_type_id = ty.user_type_id
LEFT JOIN (
    SELECT ic.object_id, ic.column_id
    FROM sys.indexes i
    JOIN sys.index_columns ic ON i.object_id=ic.object_id AND i.index_id=ic.index_id
    WHERE i.is_primary_key=1
) pk ON c.object_id=pk.object_id AND c.column_id=pk.column_id
LEFT JOIN sys.foreign_key_columns fkc
  ON fkc.parent_object_id=c.object_id AND fkc.parent_column_id=c.column_id
LEFT JOIN sys.foreign_keys fk ON fk.object_id=fkc.constraint_object_id
LEFT JOIN (
    SELECT constraint_object_id, COUNT(*) AS constraint_column_count
    FROM sys.foreign_key_columns
    GROUP BY constraint_object_id
) fkmeta ON fkmeta.constraint_object_id=fkc.constraint_object_id
LEFT JOIN sys.tables rt ON rt.object_id=fkc.referenced_object_id
LEFT JOIN sys.schemas rsch ON rsch.schema_id=rt.schema_id
LEFT JOIN sys.columns rc
  ON rc.object_id=fkc.referenced_object_id AND rc.column_id=fkc.referenced_column_id
OUTER APPLY (
    SELECT TOP (1) candidate.name
    FROM sys.columns candidate
    JOIN sys.types candidate_type ON candidate_type.user_type_id=candidate.user_type_id
    WHERE candidate.object_id=fkc.referenced_object_id
      AND candidate.column_id<>fkc.referenced_column_id
      AND candidate_type.name IN ('char','nchar','varchar','nvarchar')
    ORDER BY
      CASE
        WHEN candidate.name=CONCAT(
          CASE WHEN rt.name LIKE '%[_]%' THEN RIGHT(rt.name, LEN(rt.name)-CHARINDEX('_', rt.name)) ELSE rt.name END,
          '_name'
        ) THEN 0
        WHEN candidate.name IN ('name','display_name','title','label') THEN 1
        WHEN candidate.name='first_name' THEN 2
        WHEN candidate.name LIKE '%[_]name' THEN 3
        ELSE 4
      END,
      candidate.column_id
) labelcol
WHERE c.object_id=OBJECT_ID(N'$escapedSchema.$escapedTable')
ORDER BY c.column_id;
"@

    $rawColumns = & $sqlcmd -S $Server -d $SqlDatabaseName -G -Q $query -h -1 -W -s '|' -w 65535
    if ($LASTEXITCODE -ne 0) { throw "Could not inspect $SchemaName.$TableName." }

    $columns = @()
    foreach ($line in $rawColumns) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $fields = $line.Split('|')
        if ($fields.Count -ne 16) { throw "Unexpected schema row for $SchemaName.$TableName`: $line" }
        $columns += [pscustomobject]@{
            ordinal = [int]$fields[0].Trim()
            name = $fields[1].Trim()
            dataType = $fields[2].Trim()
            maxLength = [int]$fields[3].Trim()
            precision = [int]$fields[4].Trim()
            scale = [int]$fields[5].Trim()
            nullable = ([int]$fields[6].Trim() -eq 1)
            identity = ([int]$fields[7].Trim() -eq 1)
            primaryKey = ([int]$fields[8].Trim() -eq 1)
            foreignKeyName = if ($fields[9].Trim() -eq 'NULL') { '' } else { $fields[9].Trim() }
            foreignKeyColumnCount = if ($fields[10].Trim() -eq 'NULL') { 0 } else { [int]$fields[10].Trim() }
            referencedSchema = if ($fields[11].Trim() -eq 'NULL') { '' } else { $fields[11].Trim() }
            referencedTable = if ($fields[12].Trim() -eq 'NULL') { '' } else { $fields[12].Trim() }
            referencedColumn = if ($fields[13].Trim() -eq 'NULL') { '' } else { $fields[13].Trim() }
            lookupLabelColumn = if ($fields[14].Trim() -eq 'NULL') { '' } else { $fields[14].Trim() }
            readOnly = ([int]$fields[15].Trim() -eq 1)
        }
    }

    if ($columns.Count -eq 0) { throw "Table '$SchemaName.$TableName' was not found or has no columns." }
    if (@($columns | Where-Object primaryKey).Count -eq 0) {
        throw "Table '$SchemaName.$TableName' has no primary key. PowerTable authoring requires a stable row identity."
    }
    $compositeForeignKeys = @($columns | Where-Object { $_.foreignKeyName -and $_.foreignKeyColumnCount -gt 1 })
    if ($compositeForeignKeys.Count -gt 0) {
        throw "Composite foreign-key lookup generation is not proven for '$SchemaName.$TableName': $((@($compositeForeignKeys.foreignKeyName | Sort-Object -Unique)) -join ', ')."
    }
    $missingLookupLabels = @($columns | Where-Object { $_.foreignKeyName -and (-not $_.lookupLabelColumn -or $_.lookupLabelColumn -eq 'NULL') })
    if ($missingLookupLabels.Count -gt 0) {
        $missingDescriptions = @($missingLookupLabels | ForEach-Object {
            "$($_.name) -> $($_.referencedSchema).$($_.referencedTable)"
        })
        throw "No textual lookup label could be selected for '$SchemaName.$TableName': $($missingDescriptions -join ', ')."
    }

    return @($columns)
}

function Test-TableHasRows {
    param(
        [Parameter(Mandatory = $true)][string]$Server,
        [Parameter(Mandatory = $true)][string]$SqlDatabaseName,
        [Parameter(Mandatory = $true)][string]$SchemaName,
        [Parameter(Mandatory = $true)][string]$TableName
    )

    $quotedSchema = '[' + $SchemaName.Replace(']', ']]') + ']'
    $quotedTable = '[' + $TableName.Replace(']', ']]') + ']'
    $query = "SET NOCOUNT ON; SELECT CASE WHEN EXISTS (SELECT 1 FROM $quotedSchema.$quotedTable) THEN 1 ELSE 0 END;"
    $rawResult = & $sqlcmd -S $Server -d $SqlDatabaseName -G -Q $query -h -1 -W
    if ($LASTEXITCODE -ne 0) {
        throw "Could not check for rows in $SchemaName.$TableName."
    }
    $resultLines = @($rawResult | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    if ($resultLines.Count -ne 1 -or $resultLines[0] -notmatch '^[01]$') {
        throw "Unexpected existence-check result for $SchemaName.$TableName."
    }
    return $resultLines[0] -eq '1'
}

function ConvertFrom-CheckboxSqlText {
    param(
        [Parameter(Mandatory = $true)][string]$Value,
        [Parameter(Mandatory = $true)][string]$DataType
    )

    if ($DataType -match '^(bit|boolean)$') {
        return [int]$Value
    }
    if ($DataType -match '^(tinyint|smallint|int|bigint)$') {
        return [long]$Value
    }
    return $Value
}

function ConvertTo-CheckboxTypedValue {
    param(
        [AllowNull()][object]$Value,
        [Parameter(Mandatory = $true)][string]$DataType
    )

    if ($null -eq $Value) {
        return $null
    }
    if ($DataType -match '^(bit|boolean)$') {
        return [int]$Value
    }
    if ($DataType -match '^(tinyint|smallint|int|bigint)$') {
        return [long]$Value
    }
    return [string]$Value
}

function Test-CheckboxValueEqual {
    param(
        [AllowNull()][object]$Left,
        [AllowNull()][object]$Right,
        [Parameter(Mandatory = $true)][string]$DataType
    )

    if ($null -eq $Left -or $null -eq $Right) {
        return $null -eq $Left -and $null -eq $Right
    }
    if ($DataType -match '^(char|nchar|varchar|nvarchar)$') {
        return [string]::Equals([string]$Left, [string]$Right, [StringComparison]::Ordinal)
    }
    return [long]$Left -eq [long]$Right
}

function ConvertTo-InferredCheckboxText {
    param(
        [Parameter(Mandatory = $true)][string]$ObservedValue,
        [Parameter(Mandatory = $true)][string]$Counterpart
    )

    if ($ObservedValue -ceq $ObservedValue.ToUpperInvariant()) {
        return $Counterpart.ToUpperInvariant()
    }
    if ($ObservedValue -ceq $ObservedValue.ToLowerInvariant()) {
        return $Counterpart.ToLowerInvariant()
    }
    if ($ObservedValue.Length -gt 1 -and
        $ObservedValue.Substring(0, 1) -ceq $ObservedValue.Substring(0, 1).ToUpperInvariant() -and
        $ObservedValue.Substring(1) -ceq $ObservedValue.Substring(1).ToLowerInvariant()) {
        return $Counterpart.Substring(0, 1).ToUpperInvariant() + $Counterpart.Substring(1).ToLowerInvariant()
    }
    return $null
}

function Get-DistinctCheckboxValues {
    param(
        [Parameter(Mandatory = $true)][string]$Server,
        [Parameter(Mandatory = $true)][string]$SqlDatabaseName,
        [Parameter(Mandatory = $true)][string]$SchemaName,
        [Parameter(Mandatory = $true)][string]$TableName,
        [Parameter(Mandatory = $true)][object]$Column
    )

    $quotedSchema = '[' + $SchemaName.Replace(']', ']]') + ']'
    $quotedTable = '[' + $TableName.Replace(']', ']]') + ']'
    $quotedColumn = '[' + ([string]$Column.name).Replace(']', ']]') + ']'
    $distinctExpression = if ([string]$Column.dataType -match '^(char|nchar|varchar|nvarchar)$') {
        "$quotedColumn COLLATE Latin1_General_100_BIN2"
    } else {
        $quotedColumn
    }
    $query = @"
SET NOCOUNT ON;
SELECT TOP (3) CONCAT(
         CASE WHEN value IS NULL THEN '1' ELSE '0' END,
         '|',
         CASE
           WHEN value IS NULL THEN ''
           ELSE CONVERT(VARCHAR(MAX), CONVERT(VARBINARY(MAX), CONVERT(NVARCHAR(MAX), value)), 2)
         END
       )
FROM (
  SELECT DISTINCT $distinctExpression AS value
  FROM $quotedSchema.$quotedTable
) distinct_values;
"@

    $rawValues = & $sqlcmd -S $Server -d $SqlDatabaseName -G -Q $query -h -1 -y 0 -w 65535
    if ($LASTEXITCODE -ne 0) {
        throw "Could not inspect checkbox values for $SchemaName.$TableName.$($Column.name)."
    }

    $values = @()
    foreach ($line in $rawValues) {
        $encoded = $line.Trim()
        if ([string]::IsNullOrWhiteSpace($encoded)) { continue }
        $separator = $encoded.IndexOf('|')
        if ($separator -ne 1) {
            throw "Unexpected distinct-value row for $SchemaName.$TableName.$($Column.name): $line"
        }
        $isNull = $encoded.Substring(0, 1) -eq '1'
        if ($isNull) {
            $values += [pscustomobject]@{ isNull = $true; value = $null; displayValue = 'NULL' }
            continue
        }
        $hex = $encoded.Substring(2)
        $text = [Text.Encoding]::Unicode.GetString([Convert]::FromHexString($hex))
        $typedValue = ConvertFrom-CheckboxSqlText -Value $text -DataType ([string]$Column.dataType)
        $values += [pscustomobject]@{ isNull = $false; value = $typedValue; displayValue = $text }
    }
    return @($values)
}

function Get-AutomaticCheckboxMapping {
    param(
        [Parameter(Mandatory = $true)][object[]]$Values,
        [Parameter(Mandatory = $true)][string]$DataType
    )

    $recognizedPairs = @(
        [pscustomobject]@{ checked = '1'; unchecked = '0' },
        [pscustomobject]@{ checked = 'true'; unchecked = 'false' },
        [pscustomobject]@{ checked = 'yes'; unchecked = 'no' },
        [pscustomobject]@{ checked = 'y'; unchecked = 'n' }
    )
    foreach ($pair in $recognizedPairs) {
        $checked = @($Values | Where-Object { $_.displayValue.ToLowerInvariant() -ceq $pair.checked })
        $unchecked = @($Values | Where-Object { $_.displayValue.ToLowerInvariant() -ceq $pair.unchecked })
        if ($checked.Count -eq 1 -and $unchecked.Count -eq 1) {
            return [pscustomobject]@{
                checkedValue = $checked[0].value
                unCheckedValue = $unchecked[0].value
            }
        }
    }
    if ($Values.Count -ne 1) {
        return $null
    }

    $observed = $Values[0]
    $observedSemantic = $observed.displayValue.ToLowerInvariant()
    foreach ($pair in $recognizedPairs) {
        $observedIsChecked = $observedSemantic -ceq $pair.checked
        $observedIsUnchecked = $observedSemantic -ceq $pair.unchecked
        if (-not $observedIsChecked -and -not $observedIsUnchecked) {
            continue
        }

        $counterpartSemantic = if ($observedIsChecked) { $pair.unchecked } else { $pair.checked }
        $counterpart = if ($DataType -match '^(char|nchar|varchar|nvarchar)$') {
            if ($counterpartSemantic -match '^[01]$') {
                $counterpartSemantic
            } else {
                ConvertTo-InferredCheckboxText `
                    -ObservedValue ([string]$observed.displayValue) `
                    -Counterpart $counterpartSemantic
            }
        } else {
            ConvertTo-CheckboxTypedValue -Value $counterpartSemantic -DataType $DataType
        }
        if ($null -eq $counterpart) {
            return $null
        }

        if ($observedIsChecked) {
            return [pscustomobject]@{
                checkedValue = $observed.value
                unCheckedValue = $counterpart
            }
        }
        return [pscustomobject]@{
            checkedValue = $counterpart
            unCheckedValue = $observed.value
        }
    }
    return $null
}

function Get-CheckboxOverrideMap {
    param([Parameter(Mandatory = $true)][object]$Selection)

    $map = [System.Collections.Generic.Dictionary[string, object]]::new([StringComparer]::Ordinal)
    $property = $Selection.PSObject.Properties['checkboxMappings']
    if (-not $property) {
        return $map
    }
    foreach ($mapping in @($property.Value)) {
        $columnProperty = $mapping.PSObject.Properties['columnName']
        $checkedProperty = $mapping.PSObject.Properties['checkedValue']
        $uncheckedProperty = $mapping.PSObject.Properties['unCheckedValue']
        $columnName = if ($columnProperty) { [string]$columnProperty.Value } else { '' }
        if ([string]::IsNullOrWhiteSpace($columnName) -or -not $checkedProperty -or -not $uncheckedProperty) {
            throw 'Every checkboxMappings entry must include columnName, checkedValue, and unCheckedValue.'
        }
        if ($map.ContainsKey($columnName)) {
            throw "Duplicate checkbox mapping for column '$columnName'."
        }
        $map.Add($columnName, $mapping)
    }
    return $map
}

function Get-SingleSelectColumnSet {
    param([Parameter(Mandatory = $true)][object]$Selection)

    $set = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $property = $Selection.PSObject.Properties['singleSelectColumns']
    if (-not $property) {
        return ,$set
    }
    foreach ($columnNameValue in @($property.Value)) {
        $columnName = [string]$columnNameValue
        if ([string]::IsNullOrWhiteSpace($columnName)) {
            throw 'Every singleSelectColumns entry must be a non-empty column name.'
        }
        if (-not $set.Add($columnName)) {
            throw "Duplicate single-select column '$columnName'."
        }
    }
    return ,$set
}

function Set-TableSingleSelectMappings {
    param(
        [Parameter(Mandatory = $true)][object[]]$Columns,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][System.Collections.Generic.HashSet[string]]$SingleSelectColumns,
        [Parameter(Mandatory = $true)][string]$SchemaName,
        [Parameter(Mandatory = $true)][string]$TableName,
        [bool]$HasRows = $true
    )

    foreach ($columnName in $SingleSelectColumns) {
        $matches = @($Columns | Where-Object { [string]$_.name -ceq $columnName })
        if ($matches.Count -ne 1) {
            throw "Single-select column '$SchemaName.$TableName.$columnName' expected once; found $($matches.Count)."
        }
        $column = $matches[0]
        if ($column.foreignKeyName) {
            throw "Single-select column '$SchemaName.$TableName.$columnName' is already a foreign-key selector."
        }
        if ([string]$column.dataType -notmatch '^(char|nchar|varchar|nvarchar)$') {
            throw "DISTINCT_VALUES single-select is supported only for character columns; '$SchemaName.$TableName.$columnName' is $($column.dataType)."
        }
        if (-not $HasRows) {
            # DISTINCT_VALUES builds its options from existing rows, so an empty table would
            # leave the first row without any choices. Keep the editable text input instead.
            Write-Warning "Single-select column '$SchemaName.$TableName.$columnName' kept as text: DISTINCT_VALUES has no existing values in an empty table. Configure manual options after creation."
            $column | Add-Member -NotePropertyName singleSelectDeferred -NotePropertyValue $true
            continue
        }
        $column | Add-Member -NotePropertyName singleSelectConfigured -NotePropertyValue $true
    }
    return @($Columns)
}

function Set-TableCheckboxMappings {
    param(
        [Parameter(Mandatory = $true)][object[]]$Columns,
        [Parameter(Mandatory = $true)][bool]$HasRows,
        [Parameter(Mandatory = $true)][System.Collections.Generic.Dictionary[string, object]]$CheckboxOverrides,
        [Parameter(Mandatory = $true)][string]$Server,
        [Parameter(Mandatory = $true)][string]$SqlDatabaseName,
        [Parameter(Mandatory = $true)][string]$SchemaName,
        [Parameter(Mandatory = $true)][string]$TableName
    )

    $usedCheckboxOverrides = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    foreach ($checkboxColumn in @($Columns | Where-Object { Test-CheckboxCandidateColumn -Column $_ })) {
        $isBooleanType = [string]$checkboxColumn.dataType -match '^(bit|boolean)$'
        if (-not $HasRows) {
            if ($isBooleanType) {
                $checkboxColumn | Add-Member -NotePropertyName checkboxConfigured -NotePropertyValue $true
                $checkboxColumn | Add-Member -NotePropertyName checkedValue -NotePropertyValue 1
                $checkboxColumn | Add-Member -NotePropertyName unCheckedValue -NotePropertyValue 0
            }
            continue
        }

        $distinctValues = @(Get-DistinctCheckboxValues `
            -Server $Server `
            -SqlDatabaseName $SqlDatabaseName `
            -SchemaName $SchemaName `
            -TableName $TableName `
            -Column $checkboxColumn)
        $hasNull = @($distinctValues | Where-Object isNull).Count -gt 0
        if ($hasNull -or $distinctValues.Count -eq 0 -or $distinctValues.Count -gt 2) {
            if ($isBooleanType -or $CheckboxOverrides.ContainsKey([string]$checkboxColumn.name)) {
                $displayValues = @($distinctValues | ForEach-Object displayValue)
                throw "Checkbox column '$SchemaName.$TableName.$($checkboxColumn.name)' must contain one recognized boolean value or exactly two distinct non-null values; found $($distinctValues.Count): $($displayValues -join ', ')."
            }
            continue
        }

        $automaticMapping = Get-AutomaticCheckboxMapping `
            -Values $distinctValues `
            -DataType ([string]$checkboxColumn.dataType)
        $mapping = $null
        if ($distinctValues.Count -eq 2 -and $CheckboxOverrides.ContainsKey([string]$checkboxColumn.name)) {
            if (-not $automaticMapping) {
                $observed = @($distinctValues | ForEach-Object displayValue)
                throw "Checkbox mapping for '$SchemaName.$TableName.$($checkboxColumn.name)' is not a recognized boolean pair. Observed: $($observed -join ', '). Use singleSelectColumns for a closed category."
            }
            $override = $CheckboxOverrides[[string]$checkboxColumn.name]
            $checkedValue = ConvertTo-CheckboxTypedValue -Value $override.checkedValue -DataType ([string]$checkboxColumn.dataType)
            $unCheckedValue = ConvertTo-CheckboxTypedValue -Value $override.unCheckedValue -DataType ([string]$checkboxColumn.dataType)
            $checkedMatches = @($distinctValues | Where-Object {
                Test-CheckboxValueEqual -Left $_.value -Right $checkedValue -DataType ([string]$checkboxColumn.dataType)
            })
            $uncheckedMatches = @($distinctValues | Where-Object {
                Test-CheckboxValueEqual -Left $_.value -Right $unCheckedValue -DataType ([string]$checkboxColumn.dataType)
            })
            if ($checkedMatches.Count -ne 1 -or $uncheckedMatches.Count -ne 1 -or
                (Test-CheckboxValueEqual -Left $checkedValue -Right $unCheckedValue -DataType ([string]$checkboxColumn.dataType))) {
                $observed = @($distinctValues | ForEach-Object displayValue)
                throw "Checkbox mapping for '$SchemaName.$TableName.$($checkboxColumn.name)' must assign its two exact case-sensitive source values. Observed: $($observed -join ', ')."
            }
            if (-not (Test-CheckboxValueEqual -Left $checkedValue -Right $automaticMapping.checkedValue -DataType ([string]$checkboxColumn.dataType)) -or
                -not (Test-CheckboxValueEqual -Left $unCheckedValue -Right $automaticMapping.unCheckedValue -DataType ([string]$checkboxColumn.dataType))) {
                throw "Checkbox mapping for '$SchemaName.$TableName.$($checkboxColumn.name)' must preserve the recognized positive/negative boolean semantics."
            }
            $mapping = [pscustomobject]@{
                checkedValue = $checkedMatches[0].value
                unCheckedValue = $uncheckedMatches[0].value
            }
            $null = $usedCheckboxOverrides.Add([string]$checkboxColumn.name)
        } else {
            $mapping = $automaticMapping
        }
        if (-not $mapping) {
            $observed = @($distinctValues | ForEach-Object displayValue)
            if ($distinctValues.Count -eq 1) {
                if ($isBooleanType) {
                    throw "Boolean column '$SchemaName.$TableName.$($checkboxColumn.name)' has one value that is not a recognized boolean token: $($observed -join ', ')."
                }
                continue
            }
            continue
        }

        $checkboxColumn | Add-Member -NotePropertyName checkboxConfigured -NotePropertyValue $true
        $checkboxColumn | Add-Member -NotePropertyName checkedValue -NotePropertyValue $mapping.checkedValue
        $checkboxColumn | Add-Member -NotePropertyName unCheckedValue -NotePropertyValue $mapping.unCheckedValue
    }
    $unusedCheckboxOverrides = @($CheckboxOverrides.Keys | Where-Object { -not $usedCheckboxOverrides.Contains($_) })
    if ($unusedCheckboxOverrides.Count -gt 0) {
        throw "Checkbox mappings were not applied because the columns were empty, unsupported, missing, inferred from one recognized value, or did not contain exactly two values: $($unusedCheckboxOverrides -join ', ')."
    }

    return @($Columns)
}

$account = & az account show --query '{tenant:tenantId,user:user.name}' --output json | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Azure CLI login is unavailable.' }

$workspaces = Invoke-FabricJson -Method get -Url "$fabricResource/v1/workspaces"
$workspaceMatches = @($workspaces.value | Where-Object { $_.displayName -ceq $WorkspaceName })
if ($workspaceMatches.Count -ne 1) {
    throw "Expected exactly one workspace named '$WorkspaceName'; found $($workspaceMatches.Count)."
}
$workspace = $workspaceMatches[0]

$databases = Invoke-FabricJson -Method get -Url "$fabricResource/v1/workspaces/$($workspace.id)/sqlDatabases"
$databaseMatches = @($databases.value | Where-Object { $_.displayName -ceq $DatabaseName })
if ($databaseMatches.Count -ne 1) {
    throw "Expected exactly one SQL Database named '$DatabaseName'; found $($databaseMatches.Count)."
}
$database = $databaseMatches[0]
$databaseDetail = Invoke-FabricJson -Method get -Url "$fabricResource/v1/workspaces/$($workspace.id)/sqlDatabases/$($database.id)"

$allConnections = @()
$connectionUrl = "$fabricResource/v1/connections"
while ($connectionUrl) {
    $page = Invoke-FabricJson -Method get -Url $connectionUrl
    $allConnections += @($page.value)
    $continuationProperty = $page.PSObject.Properties['continuationUri']
    $connectionUrl = if ($continuationProperty) { [string]$continuationProperty.Value } else { '' }
}
$fabricSqlConnections = @($allConnections | Where-Object { $_.connectionDetails.type -ceq 'FabricSql' })
if ($fabricSqlConnections.Count -eq 0) {
    throw 'No accessible FabricSql connections were found.'
}
$connectionMatches = @($fabricSqlConnections | Where-Object { [string]$_.id -ceq $ConnectionId })
if ($connectionMatches.Count -ne 1) {
    $names = @($fabricSqlConnections | ForEach-Object { "$($_.displayName) [$($_.id)]" })
    throw "Confirmed connection '$ConnectionId' is not one accessible FabricSql connection. Available: $($names -join ', ')."
}
$connection = $connectionMatches[0]

$server = [string]$databaseDetail.properties.serverFqdn
$sqlDatabaseName = [string]$databaseDetail.properties.databaseName

$allocatedSheetNames = [System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
$sheetSpecs = @()
foreach ($selection in $tableSelections) {
    $schemaProperty = $selection.PSObject.Properties['schemaName']
    $tableProperty = $selection.PSObject.Properties['tableName']
    $sheetProperty = $selection.PSObject.Properties['sheetName']
    $selectionSchema = if ($schemaProperty) { [string]$schemaProperty.Value } else { '' }
    $selectionTable = if ($tableProperty) { [string]$tableProperty.Value } else { '' }
    if ([string]::IsNullOrWhiteSpace($selectionSchema) -or [string]::IsNullOrWhiteSpace($selectionTable)) {
        throw 'Every table selection must include non-empty schemaName and tableName values.'
    }
    $requestedSheetName = if ($sheetProperty) { [string]$sheetProperty.Value } else { '' }
    if ([string]::IsNullOrWhiteSpace($requestedSheetName)) {
        $requestedSheetName = $selectionTable
    }
    $uniqueSheetName = Get-UniqueSheetName -RequestedName $requestedSheetName -AllocatedNames $allocatedSheetNames
    $columns = @(Get-TableColumns -Server $server -SqlDatabaseName $sqlDatabaseName -SchemaName $selectionSchema -TableName $selectionTable)
    $hasRows = Test-TableHasRows -Server $server -SqlDatabaseName $sqlDatabaseName -SchemaName $selectionSchema -TableName $selectionTable
    $singleSelectColumns = Get-SingleSelectColumnSet -Selection $selection
    $columns = @(Set-TableSingleSelectMappings `
        -Columns $columns `
        -SingleSelectColumns $singleSelectColumns `
        -SchemaName $selectionSchema `
        -TableName $selectionTable `
        -HasRows $hasRows)
    $checkboxOverrides = Get-CheckboxOverrideMap -Selection $selection
    $columns = @(Set-TableCheckboxMappings `
        -Columns $columns `
        -HasRows $hasRows `
        -CheckboxOverrides $checkboxOverrides `
        -Server $server `
        -SqlDatabaseName $sqlDatabaseName `
        -SchemaName $selectionSchema `
        -TableName $selectionTable)
    $sheetSpecs += [pscustomobject]@{
        schemaName = $selectionSchema
        tableName = $selectionTable
        requestedSheetName = $requestedSheetName
        sheetName = $uniqueSheetName
        sheetNameAdjusted = -not [string]::Equals($requestedSheetName, $uniqueSheetName, [StringComparison]::Ordinal)
        columns = $columns
        sheetId = New-RecordGuid
        visualId = New-RecordGuid
        sourceId = New-RecordGuid
    }
}

$logicalId = [guid]::NewGuid().ToString()

$root = [ordered]@{
    '$schema' = 'https://developer.microsoft.com/json-schemas/fabric/item/plan/definition/Definition/1.0.0/schema.json'
    cube = [ordered]@{ partitionRefIds = @() }
    sheets = @($sheetSpecs | ForEach-Object {
        [ordered]@{
            displayName = $_.sheetName
            isHidden = $false
            recordGuid = $_.sheetId
            sheetType = 'POWERTABLE'
            workloadItemEntityVisuals = @(
                [ordered]@{
                    isEmbedded = $false
                    visualId = $_.visualId
                    visualType = 'POWERTABLE'
                }
            )
        }
    })
    workloadItemName = $PlanName
}

$planProperties = [ordered]@{
    '$schema' = 'https://developer.microsoft.com/json-schemas/fabric/item/plan/definition/PlanProperties/1.0.0/schema.json'
    properties = [ordered]@{
        dataStreamerConfig = [ordered]@{ enabled = $false }
        pageGroupingMeta = [ordered]@{ pageGroupMapping = @{}; pageGroups = @() }
        theme = [ordered]@{ type = 3 }
        workloadLevelFilterAssignments = @()
        workloadLevelQueryFilterAssignments = @()
        workloadLevelVariables = @()
        workloadModeConfig = [ordered]@{
            EDIT = [ordered]@{
                showBookmarksPane = $false
                showCommentsPane = $false
                showDataPane = $true
                showElementsPane = $true
                showFieldsPane = $true
                showFilterPane = $true
                showPersonalizePane = $false
                showVariablesPane = $false
            }
            READ = [ordered]@{
                showBookmarksPane = $false
                showCommentsPane = $false
                showDataPane = $false
                showFilterPane = $true
                showPersonalizePane = $false
                showVariablesPane = $false
            }
        }
    }
}

$canvasStyle = [ordered]@{
    background = [ordered]@{ color = '#ffffff'; fillMode = 'cover'; imageUrl = ''; isEnabled = $true; opacity = 1; type = 'color'; value = '#ffffff' }
    border = [ordered]@{ color = '#d0d0d0'; isEnabled = $true; side = 'all'; width = 0 }
    cornerRadius = [ordered]@{ isCustomCornerRadius = $false; isEnabled = $true; radiusBottomLeft = 0; radiusBottomRight = 0; radiusTopLeft = 0; radiusTopRight = 0 }
    dimension = [ordered]@{ elementScalingUnit = 'percentage'; height = 900; type = 'DEFAULT_16_9'; width = 1600 }
    gridLineSettings = [ordered]@{ gridColumns = $null; gridLayoutType = 'auto'; gridRows = $null; showGridLines = $false; snapToGrid = $false }
    isLocked = $false
    mobileCanvas = [ordered]@{ editModeDimension = [ordered]@{ height = 3200; width = 324 }; runtimeDimension = [ordered]@{ height = 3200; width = 324 } }
    scrollToZoom = $true
    shadow = [ordered]@{ angle = 135; blur = 8; color = '#000000'; distance = 10; isEnabled = $false; opacity = 100; placement = 'outer'; side = 'bottom'; width = 0 }
    showSmartGuide = $true
    showVisualGuide = $false
    verticalAlign = 'top'
    wallpaper = [ordered]@{ fillMode = 'cover'; isEnabled = $true; opacity = 1; value = [ordered]@{ color = '#ffffff'; imageUrl = ''; type = 'color' } }
}

$platform = [ordered]@{
    '$schema' = 'https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json'
    metadata = [ordered]@{ type = 'Plan'; displayName = $PlanName }
    config = [ordered]@{ version = '2.0'; logicalId = $logicalId }
}

$infobridge = [ordered]@{
    '$schema' = 'https://developer.microsoft.com/json-schemas/fabric/item/plan/definition/ConnectedPlanning/Infobridge/1.0.0/schema.json'
    linkedQueries = @()
    queryGroups = @()
    sources = @()
}

$documents = [ordered]@{
    '.platform' = $platform
    'connectedPlanning/infobridge.json' = $infobridge
    'definition.json' = $root
    'planProperties.json' = $planProperties
}
foreach ($sheetSpec in $sheetSpecs) {
    $sheet = [ordered]@{
        '$schema' = 'https://developer.microsoft.com/json-schemas/fabric/item/plan/definition/Sheets/Sheet/1.0.0/schema.json'
        properties = [ordered]@{
            assignmentColumnMap = @{}
            canvasStyle = $canvasStyle
            controlPanePosition = 'right'
            entityLevelVariables = @()
            filterPanePosition = 'RIGHT'
            sourceVisualsMeta = @{}
            topPositionFilterExpandConfig = [ordered]@{ expandedHeight = 250; isFilterPaneCollapsed = $true }
            visualGroupMap = @{}
        }
    }
    $columnConfigs = [ordered]@{
        '$schema' = 'https://developer.microsoft.com/json-schemas/fabric/item/plan/definition/PowerTable/ColumnConfigs/1.0.0/schema.json'
        columnConfigs = @($sheetSpec.columns | ForEach-Object { ConvertTo-PowerTableColumnConfig -Column $_ })
    }
    $visualProperties = [ordered]@{
        '$schema' = 'https://developer.microsoft.com/json-schemas/fabric/item/plan/definition/PowerTable/Properties/1.0.0/schema.json'
        properties = @{}
    }
    $source = [ordered]@{
        '$schema' = 'https://developer.microsoft.com/json-schemas/fabric/item/plan/definition/PowerTable/Source/1.0.0/schema.json'
        source = [ordered]@{
            connectionId = [string]$connection.id
            connectionIdVariable = $null
            creationMode = 5
            databaseVariable = $null
            dbHost = $server.Split(',')[0]
            dbName = $sqlDatabaseName
            fileImportType = $null
            meta = [ordered]@{
                connectionName = [string]$connection.displayName
                databaseId = [string]$database.id
                dbDisplayName = [string]$database.displayName
                workspaceId = [string]$workspace.id
                workspaceName = [string]$workspace.displayName
            }
            recordGuid = $sheetSpec.sourceId
            schemaName = $sheetSpec.schemaName
            sqlTargetArtifact = $null
            tableName = $sheetSpec.tableName
            tableType = 1
        }
    }
    $sourceSettings = [ordered]@{
        '$schema' = 'https://developer.microsoft.com/json-schemas/fabric/item/plan/definition/PowerTable/Settings/1.0.0/schema.json'
        sourceSettings = @(
            [ordered]@{ name = 'SCD'; recordGuid = New-RecordGuid; settings = [ordered]@{ config = [ordered]@{ businessKey = ''; identifierKeys = [ordered]@{ activeFlag = ''; effectiveDate = ''; endDate = ''; startDate = '' } }; enabled = $false; type = 2 }; sourceId = $sheetSpec.sourceId },
            [ordered]@{ name = 'COMMENT_SETTINGS'; recordGuid = New-RecordGuid; settings = [ordered]@{ displayComment = $true; notification = $true; rowLevelComments = $false; toggleAddonColumns = $false }; sourceId = $sheetSpec.sourceId },
            [ordered]@{ name = 'ROW_DELETE'; recordGuid = New-RecordGuid; settings = [ordered]@{ enabled = $false }; sourceId = $sheetSpec.sourceId },
            [ordered]@{ filters = @([ordered]@{ filter = @{}; filterType = 1; name = 'all_users'; recordGuid = New-RecordGuid }); name = 'ROW_UPDATE'; recordGuid = New-RecordGuid; settings = [ordered]@{ enabled = $true }; sourceId = $sheetSpec.sourceId },
            [ordered]@{ filters = @([ordered]@{ filter = @{}; filterType = 1; name = 'all_users'; recordGuid = New-RecordGuid }); name = 'ROW_ADD'; recordGuid = New-RecordGuid; settings = [ordered]@{ enabled = $true }; sourceId = $sheetSpec.sourceId }
        )
    }
    $basePath = "sheets/$($sheetSpec.sheetId)/visuals/$($sheetSpec.visualId)"
    $documents["sheets/$($sheetSpec.sheetId)/sheet.json"] = $sheet
    $documents["$basePath/columnConfigs.json"] = $columnConfigs
    $documents["$basePath/properties.json"] = $visualProperties
    $documents["$basePath/source.json"] = $source
    $documents["$basePath/sourceSettings.json"] = $sourceSettings
}

$parts = foreach ($entry in $documents.GetEnumerator()) {
    $json = $entry.Value | ConvertTo-Json -Depth 100
    [ordered]@{
        path = $entry.Key
        payload = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($json))
        payloadType = 'InlineBase64'
    }
}

$payload = [ordered]@{
    displayName = $PlanName
    description = "PowerTable generated from $WorkspaceName.$DatabaseName with $($sheetSpecs.Count) sheet(s)"
    definition = [ordered]@{ parts = @($parts) }
}

$outputFullPath = [IO.Path]::GetFullPath($OutputPath)
$outputDirectory = Split-Path -Parent $outputFullPath
New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
[IO.File]::WriteAllText(
    $outputFullPath,
    ($payload | ConvertTo-Json -Depth 100),
    [Text.UTF8Encoding]::new($false)
)

$summary = [ordered]@{
    azureUser = $account.user
    workspace = $workspace.displayName
    database = $database.displayName
    selectedConnection = $connection.displayName
    selectedConnectionId = $connection.id
    planName = $PlanName
    sheetCount = $sheetSpecs.Count
    sheets = @($sheetSpecs | ForEach-Object {
        $sheetColumns = @($_.columns)
        [ordered]@{
            sheetName = $_.sheetName
            requestedSheetName = $_.requestedSheetName
            sheetNameAdjusted = $_.sheetNameAdjusted
            schema = $_.schemaName
            table = $_.tableName
            columns = $sheetColumns.Count
            primaryKeyColumns = @($sheetColumns | Where-Object primaryKey | ForEach-Object name)
            dateColumns = @($sheetColumns | Where-Object dataType -CEQ 'date' | ForEach-Object name)
            dateTimeColumns = @($sheetColumns | Where-Object dataType -Match '^(datetime|datetime2|datetimeoffset|smalldatetime)$' | ForEach-Object name)
            timeColumns = @($sheetColumns | Where-Object dataType -CEQ 'time' | ForEach-Object name)
            checkboxColumns = @($sheetColumns | Where-Object { (Get-PowerTableColumnType -Column $_) -eq $powerTableColumnType.CHECKBOX } | ForEach-Object name)
            checkboxMappings = @($sheetColumns | Where-Object {
                (Get-PowerTableColumnType -Column $_) -eq $powerTableColumnType.CHECKBOX
            } | ForEach-Object {
                [ordered]@{
                    column = $_.name
                    checkedValue = $_.checkedValue
                    unCheckedValue = $_.unCheckedValue
                }
            })
            singleSelectColumns = @($sheetColumns | Where-Object {
                $_.PSObject.Properties['singleSelectConfigured'] -and [bool]$_.singleSelectConfigured
            } | ForEach-Object name)
            postCreateSingleSelectColumns = @($sheetColumns | Where-Object {
                $_.PSObject.Properties['singleSelectDeferred'] -and [bool]$_.singleSelectDeferred
            } | ForEach-Object name)
            readOnlyColumns = @($sheetColumns | Where-Object { $_.identity -or $_.readOnly } | ForEach-Object name)
            decimalColumns = @($sheetColumns | Where-Object { (Get-PowerTableColumnType -Column $_) -eq $powerTableColumnType.DECIMAL } | ForEach-Object name)
            currencyColumns = @($sheetColumns | Where-Object { (Get-PowerTableColumnType -Column $_) -eq $powerTableColumnType.CURRENCY } | ForEach-Object name)
            numberColumns = @($sheetColumns | Where-Object { (Get-PowerTableColumnType -Column $_) -eq $powerTableColumnType.NUMBER } | ForEach-Object name)
            ratingColumns = @($sheetColumns | Where-Object { (Get-PowerTableColumnType -Column $_) -eq $powerTableColumnType.RATING } | ForEach-Object name)
            lookups = @($sheetColumns | Where-Object foreignKeyName | ForEach-Object {
                "$($_.name) -> $($_.referencedSchema).$($_.referencedTable).$($_.referencedColumn) shown as $($_.lookupLabelColumn)"
            })
        }
    })
    partCount = $parts.Count
    outputPath = $outputFullPath
}
if ($sheetSpecs.Count -eq 1) {
    $onlySheet = $summary.sheets[0]
    foreach ($property in @(
        'schema', 'table', 'columns', 'primaryKeyColumns', 'dateColumns',
        'dateTimeColumns', 'timeColumns', 'checkboxColumns', 'checkboxMappings', 'singleSelectColumns', 'postCreateSingleSelectColumns', 'readOnlyColumns', 'decimalColumns',
        'currencyColumns', 'numberColumns', 'ratingColumns', 'lookups', 'sheetName'
    )) {
        $summary[$property] = $onlySheet[$property]
    }
}
[pscustomobject]$summary | ConvertTo-Json -Depth 8
