"""Local Plan visibility constructor."""
import copy

def set_home_visibility(workload,show):
    if not isinstance(show,bool): raise ValueError('Home visibility must be Boolean')
    out=copy.deepcopy(workload)
    out.setdefault('properties',{}).setdefault('homeLayout',{})['show']=show
    return out
