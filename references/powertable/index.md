# PowerTable reference index

Choose exactly one mode from the user's requested source state, announce it and
read every reference in its row before issuing a command. This index belongs to
the `POWERTABLE` route in [SKILL.md](../../SKILL.md) and
[module routing](../module-routing.md#powertable-powertable-creation-and-analysis).

| Mode | Source state / result | Required references |
|---|---|---|
| `powertable-existing` | Connect 1-5 existing Fabric SQL Database tables to a new Plan | [Connect existing tables](connect-existing-tables.md), [column mappings](column-mappings.md) |
| `powertable-from-scratch` | Design, approve and create 1-5 SQL tables, then create a Plan | [Modeling](modeling.md), [create from scratch](create-from-scratch.md), [column mappings](column-mappings.md) |
| `powertable-analysis` | Read-only natural-language question against one existing PowerTable sheet | [Analyze PowerTable data](analyze-data.md), [column mappings](column-mappings.md) |
| `powertable-cross-analysis` | Read-only comparison of 2-3 existing PowerTable sheets | [Analyze across sheets](analyze-across-sheets.md), [analyze PowerTable data](analyze-data.md), [column mappings](column-mappings.md) |

## External SQL companion

The [`sqldb-cli`](https://github.com/gim-home/skills-for-fabric/tree/main/skills/sqldb-cli)
skill is an external companion and is not included in this bundle. Use its
[authoring guide](https://github.com/gim-home/skills-for-fabric/tree/main/skills/sqldb-cli/references/authoring.md)
for Fabric SQL Database discovery and DDL/DML procedures, and its
[consumption guide](https://github.com/gim-home/skills-for-fabric/tree/main/skills/sqldb-cli/references/consumption.md)
for read-only T-SQL. If that external skill is unavailable, stop the dependent
SQL phase rather than inventing commands or a local path.

## Shared contracts

- Plan payload generation:
  [New-PowerTablePayload.ps1](resources/New-PowerTablePayload.ps1)
- Complete ALM part contract:
  [PowerTable ALM construction](../powertable-alm-construction.md)
- SQL/PowerTable column contract:
  [column mappings](column-mappings.md)
- Current runtime constructors:
  `runtime.powertable_factory`, `runtime.table_columns` and
  `plan.py construct-native ...`
- Deferred uninitialized sheet:
  [maintenance connection fallback](../maintenance-deferred-connection.md)

Planning, payload preview or definition generation alone does not persist
anything. Creation and analysis have separate confirmation and terminal-write
contracts described by the selected mode.
