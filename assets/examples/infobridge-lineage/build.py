"""Offline example: construct a fresh Planning source, pivot query and ALM graph.

Run from any directory: python /path/to/skill/examples/infobridge-lineage/build.py OUT
Uses only this package and synthetic request data. No live API calls.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from runtime.codec import load,save
from runtime.bridge import planning_source,Query,portable
from runtime.bridge_identity import check_planning_graph,resolve_planning_output

def build(destination):
    request=load(Path(__file__).with_name('planning-source.request.json'))
    source=planning_source(**request)
    # Use the enriched source catalog for every query on that owner.
    query=Query('Regional Revenue',source['sourceGuid'],source['meta'],visual_id=request['visual_id']).load_planning()
    query.pivot(['Region'],['Month'],{'Unit Forecast':'sum','Revenue Plan':'sum'})
    source['queries']=[query.record]
    graph=portable([source],[])
    save(destination/'infobridge.json',graph)
    save(destination/'identity-check.json',check_planning_graph(graph))
    # Illustrative destination readback has native query/output IDs that differ.
    field=resolve_planning_output(**load(Path(__file__).with_name('resolve-output.request.json')))
    save(destination/'resolved-field.json',field)
    return graph,field

if __name__=='__main__':
    build(Path(sys.argv[1]));print('Built synthetic graph and resolved illustrative output; no live deployment.')
