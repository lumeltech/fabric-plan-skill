import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import unittest,copy
from decimal import Decimal
from test_context_intelligence import example
from runtime.construct import build
from runtime.readback import verify_authored
from runtime.layout import overlap

class LiveReadbackRegressions(unittest.TestCase):
    def test_decimal_coordinates_float_gap(self):
        a={'x':Decimal('24'),'y':Decimal('306'),'width':Decimal('506.6666666666667'),'height':Decimal('132')}
        b={'x':Decimal('546.6666666666667'),'y':Decimal('306'),'width':Decimal('506.6666666666667'),'height':Decimal('132')}
        self.assertFalse(overlap(a,b,15.999999))
        b['x']=Decimal('530')
        self.assertTrue(overlap(a,b,15.999999))

    def test_embedded_first_export_retains_identity(self):
        m,s=example();built=build(m,s);actual=copy.deepcopy(built['raw'])
        sheet=actual['definition.json']['sheets'][-1]
        sheet['workloadItemEntityVisuals'].sort(key=lambda v:not v['isEmbedded'])
        verify_authored(actual,built['raw'])
        sheet['workloadItemEntityVisuals'][0]['isEmbedded']=False
        with self.assertRaises(ValueError):verify_authored(actual,built['raw'])

    def test_duplicate_exported_visual_is_rejected(self):
        m,s=example();built=build(m,s);actual=copy.deepcopy(built['raw'])
        vs=actual['definition.json']['sheets'][-1]['workloadItemEntityVisuals']
        vs.append(copy.deepcopy(vs[0]))
        with self.assertRaises(ValueError):verify_authored(actual,built['raw'])
