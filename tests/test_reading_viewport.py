import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))  # runtime/ importable under unittest and pytest
import unittest
from runtime.intelligence import rectangles

class ReadingViewportTests(unittest.TestCase):
    def test_template_counts_and_viewports(self):
        for preset in ('left-rail','stacked'):
            for width,vw,vh in [(1200,1600,900),(1920,1200,1080),(2240,2523,1491),(1600,900,1400)]:
                for filters,cards,charts,pages in [(0,0,0,1),(1,2,1,3),(3,3,4,10),(12,9,5,24)]:
                    with self.subTest(preset=preset,width=width,counts=(filters,cards,charts,pages)):
                        layout=rectangles(filters,cards,width=width,charts=charts,pages=pages,layout=preset,
                                          viewport={'width':vw,'height':vh})
                        self.assertGreaterEqual(layout['height'],width*vh//vw)
                        self.assertGreaterEqual(layout['rectangles']['grid']['height'],450)
                        self.assertEqual(max(r['y']+r['height'] for r in layout['rectangles'].values()),layout['height']-24)
    def test_fixed_and_flexible_custom_geometry(self):
        viewport={'width':1400,'height':1250}
        fixed=rectangles(3,0,width=1400,charts=2,pages=10)
        self.assertEqual(rectangles(3,0,charts=2,layout=fixed,viewport=viewport),fixed)
        flexible={**fixed,'fitColumns':[
          {'rows':['slicer:0','slicer:1','slicer:2'],'weights':[1,1,2]},
          {'rows':['note','grid',['chart:0','chart:1']],'weights':[0,2,1]}]}
        result=rectangles(3,0,charts=2,layout=flexible,viewport=viewport)
        baseline=result['height']-24
        for key in ['slicer:2','chart:0','chart:1']:
            r=result['rectangles'][key]
            self.assertEqual(r['y']+r['height'],baseline)
        for key in ('header','note','navigator'):
            self.assertEqual(result['rectangles'][key],fixed['rectangles'][key])
        self.assertEqual(result['rectangles']['chart:0']['height'],result['rectangles']['chart:1']['height'])
        self.assertGreater(result['rectangles']['grid']['height'],fixed['rectangles']['grid']['height'])
        self.assertEqual(result['rectangles']['chart:1']['x'],fixed['rectangles']['chart:1']['x'])
    def test_invalid_columns_and_viewport(self):
        fixed=rectangles(1,0)
        for rows,weights in [(['grid','grid'],[1,1]),(['missing'],[1]),(['grid'],[0]),(['grid','note'],[1,1])]:
            with self.assertRaises(ValueError):
                rectangles(1,0,layout={**fixed,'fitColumns':[{'rows':rows,'weights':weights}]})
        with self.assertRaises(ValueError):rectangles(1,0,viewport={'width':0,'height':800})

    def test_application_uses_viewport_for_saved_visuals(self):
        from pathlib import Path
        from runtime.codec import load
        from runtime.public_alignment import check_placements
        from runtime.planning_presentation import build_application
        fixture=Path(__file__).resolve().parents[1]/'assets/fixtures'
        spec=load(fixture/'context-dashboard-spec.json')
        for d in spec['dashboards']:
            d['viewport']={'width':1600,'height':1600}
        app=build_application(load(fixture/'context-dashboard-model.json'),spec)
        for d in app['dashboardIdentities']:
            self.assertGreaterEqual(d['layout']['height'],d['layout']['width'])
            self.assertEqual(check_placements(app['raw'],d)['visualCount'],len(d['placements']))

    def test_fractional_bottom_and_fixed_footer(self):
        from decimal import Decimal
        from runtime.stack_layout import fill_columns
        rects={'matrix':{'y':10,'height':Decimal('399.5')},'footer':{'y':Decimal('425.5'),'height':40}}
        fill_columns(rects,[{'rows':['matrix','footer'],'weights':[1,0]}],600)
        self.assertEqual(rects['footer']['y']+40,600)
        self.assertEqual(rects['matrix']['y']+rects['matrix']['height']+16,rects['footer']['y'])
