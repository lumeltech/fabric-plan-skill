"""Cube partitions, partition measures and their mappings as ``cube/cube.json`` records.

The cube part sits at the definition root. This constructor appends new records
to a fresh export and links them by recordGuid, the ``_RefId`` reference form;
it never writes a numeric service ID. Records already in the export keep their
content and reference form. Saving the part provisions, refreshes and
allocates nothing.
"""
import copy
from .construct import schema,guid
from .codec import parts,unpack,scoped_candidate
from .cube_contract import dimension_record,reference_measure
from .planning_features import request_items

PATH='cube/cube.json'
ARRAYS=('cubePartitions','cubePartitionMeasures','cubePartitionMeasureMappings','cubePartitionMeasureDataInputColumnMappings')
MEASURE_TYPES=('FORECAST','NUMBER','FORMULA')
PARTITION_REQUEST={'name','dimensions','time_dimensions','measures'}
MEASURE_REQUEST={'name','type','config'}
MAPPING_REQUEST={'partition','measure'}
INPUT_REQUEST={'measure','partition','sheet_guid','visual_id','measure_guid'}
NUMERIC_REFERENCES=('cubePartitionId','cubePartitionMeasureId','dataInputColumnId','visualId')

def _name(value,label):
    if not isinstance(value,str) or not value.strip():raise ValueError(label+' name must be non-empty text')
    return value.strip()

def cube_partition(name=None,dimensions=None,time_dimensions=None,measures=None):
    """One cubePartitions record from resolved model identities; a new partition holds no rows yet."""
    name=_name(name,'Cube partition')
    if not all(isinstance(v,list) for v in (dimensions,time_dimensions,measures)):
        raise ValueError('Cube partition dimensions, time_dimensions and measures must be arrays')
    if not dimensions and not time_dimensions:raise ValueError('A cube partition needs at least one dimension or time dimension')
    dims=[dimension_record(d,'dimensions/'+str(i),lookup=True) for i,d in enumerate(dimensions)]
    times=[dimension_record(d,'time_dimensions/'+str(i),lookup=True) for i,d in enumerate(time_dimensions)]
    ids=[d['id'] for d in dims+times]
    if len(set(ids))!=len(ids):raise ValueError('Duplicate dimension in cube partition '+name)
    return {'recordGuid':guid(),'name':name,'dimensions':dims,'timeDimensions':times,
            'measures':[reference_measure(m,'measures/'+str(i)) for i,m in enumerate(measures)],'rowCount':0}

def partition_measure(name=None,type=None,config=None):
    """One cubePartitionMeasures record; config is copied as given and checked against the published schema."""
    name=_name(name,'Partition measure')
    if type is None:raise ValueError('Partition measure type required; it has no default')
    if type not in MEASURE_TYPES:raise ValueError('Partition measure type must be FORECAST, NUMBER or FORMULA')
    if not isinstance(config,dict):raise ValueError('Partition measure config must be an object')
    return {'recordGuid':guid(),'name':name,'type':type,'config':copy.deepcopy(config)}

def _find(records,name,label):
    wanted=name.strip().casefold() if isinstance(name,str) else None
    found=[r for r in records if isinstance(r,dict) and isinstance(r.get('name'),str) and r['name'].strip().casefold()==wanted]
    if len(found)!=1:raise ValueError(('Several '+label+'s are named ' if found else 'No '+label+' named ')+str(name))
    return found[0]

def cube_records(raw,current,*,partitions=None,measures=None,measure_mappings=None,input_mappings=None):
    """New records for the four cube arrays, linked to new or existing records by name."""
    from .planning_features import planning_prefix
    from .validate import Schemas,public_schema_view
    new={key:[] for key in ARRAYS}
    for items,label,allowed,key,build,existing in (
            (partitions,'partition',PARTITION_REQUEST,'cubePartitions',cube_partition,'cube partition'),
            (measures,'measure',MEASURE_REQUEST,'cubePartitionMeasures',partition_measure,'partition measure')):
        if items is None:continue
        names={str(r.get('name','')).strip().casefold() for r in current[key] if isinstance(r,dict)}
        for spec in request_items(items,label,allowed):
            record=build(**spec)
            if record['name'].casefold() in names:raise ValueError('A '+existing+' named '+record['name']+' already exists')
            names.add(record['name'].casefold());new[key].append(record)
    all_partitions=current['cubePartitions']+new['cubePartitions'];all_measures=current['cubePartitionMeasures']+new['cubePartitionMeasures']
    def numeric(records):return {r['id']:r.get('recordGuid') for r in records if isinstance(r,dict) and isinstance(r.get('id'),int)}
    partition_ids,measure_ids=numeric(current['cubePartitions']),numeric(current['cubePartitionMeasures'])
    linked={(m.get('cubePartition_RefId') or partition_ids.get(m.get('cubePartitionId')),
             m.get('cubePartitionMeasure_RefId') or measure_ids.get(m.get('cubePartitionMeasureId')))
            for m in current['cubePartitionMeasureMappings'] if isinstance(m,dict)}
    for spec in request_items(measure_mappings,'measure mapping',MAPPING_REQUEST) if measure_mappings is not None else []:
        partition=_find(all_partitions,spec.get('partition'),'cube partition');measure=_find(all_measures,spec.get('measure'),'partition measure')
        pair=(partition['recordGuid'],measure['recordGuid'])
        if pair in linked:raise ValueError('Partition measure '+measure['name']+' is already linked to cube partition '+partition['name'])
        linked.add(pair)
        new['cubePartitionMeasureMappings'].append({'recordGuid':guid(),'cubePartition_RefId':pair[0],'cubePartitionMeasure_RefId':pair[1]})
    mapped={(m.get('visual_RefId'),m.get('dataInputColumnMeasureGuid'),m.get('cubePartitionMeasure_RefId'))
            for m in current['cubePartitionMeasureDataInputColumnMappings'] if isinstance(m,dict)}
    for spec in request_items(input_mappings,'input mapping',INPUT_REQUEST) if input_mappings is not None else []:
        prefix,visual=planning_prefix(raw,spec.get('sheet_guid'),spec.get('visual_id'))
        column=spec.get('measure_guid')
        if column not in {c.get('measureGuid') for c in raw[prefix+'dataInput.json'].get('columns') or [] if isinstance(c,dict)}:
            raise ValueError('Input mapping measure_guid is not a measure of this visual: '+str(column))
        measure=_find(all_measures,spec.get('measure'),'partition measure')
        key=(visual,column,measure['recordGuid'])
        if key in mapped:raise ValueError('This input column is already mapped to partition measure '+measure['name'])
        mapped.add(key)
        record={'recordGuid':guid(),'dataInputColumnMeasureGuid':column,'cubePartitionMeasure_RefId':measure['recordGuid'],'visual_RefId':visual}
        if spec.get('partition') is not None:record['cubePartition_RefId']=_find(all_partitions,spec['partition'],'cube partition')['recordGuid']
        new['cubePartitionMeasureDataInputColumnMappings'].append(record)
    view,_=public_schema_view(PATH,{'$schema':schema('cube'),**new})
    Schemas().check(view,schema('cube'))
    return new

def add_cube_part(envelope,*,partitions=None,measures=None,measure_mappings=None,input_mappings=None):
    """Scoped candidate appending cube records; every other part keeps its bytes."""
    from .validate import schema_report
    if all(v is None for v in (partitions,measures,measure_mappings,input_mappings)):
        raise ValueError('Request at least one of partitions, measures, measure_mappings or input_mappings')
    raw=unpack(envelope)
    current=copy.deepcopy(raw.get(PATH) or {'$schema':schema('cube'),**{key:[] for key in ARRAYS}})
    for key in ARRAYS:
        if not isinstance(current.get(key),list):raise ValueError('Existing cube/cube.json has no '+key+' list')
    numeric=any(isinstance(r,dict) and any(k in r for k in NUMERIC_REFERENCES) for key in ARRAYS[2:] for r in current[key])
    new=cube_records(raw,current,partitions=partitions,measures=measures,measure_mappings=measure_mappings,input_mappings=input_mappings)
    for key in ARRAYS:current[key].extend(new[key])
    candidate,changed,added=scoped_candidate(envelope,{PATH:current})
    warnings=['Existing cube mappings use numeric service IDs; new records reference partitions and measures by recordGuid. '
              'Both forms are documented; confirm the mappings after publishing.'] if numeric else []
    return candidate,{'partitions':[r['name'] for r in new['cubePartitions']],'measures':[r['name'] for r in new['cubePartitionMeasures']],
        'measureMappings':len(new['cubePartitionMeasureMappings']),'inputMappings':len(new['cubePartitionMeasureDataInputColumnMappings']),
        'changedParts':changed,'addedParts':added,'preservedPartCount':len(parts(envelope))-len(changed),
        'publicSchema':{item['path']:item['status'] for item in schema_report({PATH:current})},'warnings':warnings,
        'deployment':'not run','runtimeValidation':'not run'}
