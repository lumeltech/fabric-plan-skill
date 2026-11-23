"""Catalog alias compatibility, strict validation, and duplicate-safe resumes."""
import copy,json,os,tempfile,unittest
from unittest.mock import patch
from runtime.builder_api import column_matches


def payload():
    return {'measureGuid':'123','columnType':6,'name':'Linked estimate',
            'columnMeta':{'id':'123','data_type':'Number','name':'Linked estimate',
                          'measure_type':{'Native':{'measure_role':'ACMeasure'}}},
            'boundToFilterContext':10}


def saved_record(request,alias='dataInputType'):
    saved=copy.deepcopy(request)
    if alias=='dataInputType':saved['dataInputType']=saved.pop('columnType')
    elif alias=='both':saved['dataInputType']=saved['columnType']
    return saved


class NativeColumnTypeReadback(unittest.TestCase):
    def setUp(self):self.request=payload()

    def test_sql_catalog_shape(self):column_matches(saved_record(self.request,'columnType'),self.request)

    def test_onelake_catalog_shape(self):column_matches(saved_record(self.request),self.request)

    def test_agreeing_aliases(self):column_matches(saved_record(self.request,'both'),self.request)

    def test_conflicting_aliases_are_rejected(self):
        saved=saved_record(self.request,'both');saved['dataInputType']=7
        with self.assertRaisesRegex(ValueError,'Conflicting'):column_matches(saved,self.request)

    def test_missing_wrong_null_and_string_types_are_rejected(self):
        for value in (None,7,'6'):
            for alias in ('columnType','dataInputType'):
                with self.subTest(value=value,alias=alias):
                    saved=saved_record(self.request,alias);saved[alias]=value
                    with self.assertRaisesRegex(ValueError,'columnType'):column_matches(saved,self.request)
        saved=copy.deepcopy(self.request);del saved['columnType']
        with self.assertRaisesRegex(ValueError,'columnType'):column_matches(saved,self.request)

    def test_identity_name_and_context_checks_remain_strict(self):
        for key,value in (('measureGuid','999'),('name','Wrong name'),('boundToFilterContext',20)):
            with self.subTest(key=key):
                saved=saved_record(self.request);saved[key]=value
                with self.assertRaisesRegex(ValueError,key):column_matches(saved,self.request)

    def test_metadata_checks_remain_strict(self):
        for key,value in (('id','999'),('data_type','Text'),('measure_type',{})):
            with self.subTest(key=key):
                saved=saved_record(self.request);saved['columnMeta'][key]=value
                with self.assertRaises((ValueError,KeyError)):column_matches(saved,self.request)


if __name__=='__main__':unittest.main()
