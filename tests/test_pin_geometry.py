import ast
from collections import Counter
from math import cos, sin, pi
from pathlib import Path
import unittest

from scripts.pin_geometry import build_pin


class PinGeometryTests(unittest.TestCase):
    def test_profile_dimensions_and_closed_consistent_edges(self):
        vertices,faces,_=build_pin()
        self.assertAlmostEqual(max(v[2] for v in vertices)-min(v[2] for v in vertices),.381)
        self.assertAlmostEqual(max(v[0] for v in vertices)-min(v[0] for v in vertices),.121)
        edges=Counter(tuple(sorted((a,b))) for face in faces for a,b in zip(face,face[1:]+face[:1]))
        self.assertTrue(all(count==2 for count in edges.values()))
        self.assertLessEqual(sum(len(face)-2 for face in faces),2500)
        for face in faces:
            origin=vertices[face[0]]
            for i in range(1,len(face)-1):
                a=[vertices[face[i]][j]-origin[j] for j in range(3)]
                b=[vertices[face[i+1]][j]-origin[j] for j in range(3)]
                cross=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
                self.assertGreater(sum(v*v for v in cross),4e-24)

    def test_two_separated_red_neck_bands(self):
        vertices,faces,indices=build_pin()
        intervals=sorted({(min(vertices[i][2] for i in face),max(vertices[i][2] for i in face))
                          for face,index in zip(faces,indices) if index==1})
        self.assertEqual(intervals,[(.270,.276),(.288,.294)])

    def test_actual_worker_payload_matches_tested_geometry(self):
        root=Path(__file__).resolve().parents[1]
        tree=ast.parse((root/'artifacts/scripts/stage03_pins_corrected.py').read_text())
        function=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='run_stage')
        def assigns(node,name):
            return isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets)
        start=next(i for i,node in enumerate(function.body) if assigns(node,'profile'))
        stop=next(i for i,node in enumerate(function.body) if assigns(node,'mesh'))
        namespace={'cos':cos,'sin':sin,'pi':pi}
        exec(compile(ast.Module(body=function.body[start:stop],type_ignores=[]),'<pure geometry fixture>','exec'),namespace)
        self.assertEqual((namespace['vertices'],namespace['faces'],namespace['material_indices']),build_pin())
