import unittest
from scripts.blender_api import inspect_api,lookup,classify_api_error
from scripts.submission_guard import SubmissionGuard,budget_accounting
from pathlib import Path
import tempfile


CATALOG={'version':'5.2.3 LTS','build_hash':'fixture','errors':{},'extras':{},'bmesh_ops':['recalc_face_normals'],
    'types':{
        'Mesh':{'members':['update','validate','from_pydata','vertices','name'],'properties':{},'functions':{'update':{'calc_edges':{}}}},
        'Object':{'members':['data','type'],'properties':{},'functions':{}},
    },
    'data_collections':{'meshes':{'target':'Mesh','members':['new','get','remove']},'objects':{'target':'Object','members':['new','get','remove']}},
    'operators':{'bpy.ops.mesh.primitive_cube_add':{'parameters':{'size':{},'location':{}},'description':'Add a cube'}}}


class ApiTests(unittest.TestCase):
    def test_installed_names_and_keywords_reject_unknown_calls(self):
        for code in ["import bpy\nme=bpy.data.meshes.new('m')\nme.calc_normals_use_fit_sharp()",
                     "import bpy as b\nb.ops.mesh.fake_operator()",
                     "import bpy\nbpy.ops.mesh.primitive_cube_add(fake=1)",
                     "import bpy\nbpy.data.meshes.fake_factory('x')",
                     "import bmesh\nbmesh.ops.fake_operator()",
                     "from bpy.types import Mesh\ndef f(mesh: Mesh):\n    mesh.nonexistent()"]:
            with self.subTest(code=code):self.assertTrue(inspect_api(code,CATALOG))

    def test_supported_aliases_and_unknown_python_receivers_are_not_rejected(self):
        for code in ["import bpy as b\nmake=b.data.meshes.new\nm=make('m')\nm.update(calc_edges=True)",
                     'import bpy\nbpy.ops.mesh.primitive_cube_add.poll()',
                     "def f(x):\n    x.custom_user_method()",
                     "import bpy\nme=bpy.data.meshes.new('m')\nme={}\nme.clear()"]:
            self.assertEqual(inspect_api(code,CATALOG),[])

    def test_mesh_data_is_checked_only_with_explicit_narrowing(self):
        code="import bpy\nobj=bpy.data.objects.get('o')\nif obj is not None and obj.type == 'MESH':\n    me=obj.data\n    me.calc_normals_use_fit_sharp()"
        self.assertEqual(inspect_api(code,CATALOG)[0]['api'],'Mesh.calc_normals_use_fit_sharp')
        self.assertEqual(inspect_api("import bpy\nobj=bpy.data.objects.get('o')\nobj.data.some_polymorphic_member()",CATALOG),[])

    def test_lookup_and_strict_runtime_error_classification(self):
        self.assertFalse(lookup(CATALOG,'Mesh.calc_normals_use_fit_sharp')['available'])
        self.assertIn('size',lookup(CATALOG,'bpy.ops.mesh.primitive_cube_add')['operator']['parameters'])
        api="AttributeError: 'Mesh' object has no attribute 'calc_normals_use_fit_sharp'"
        classified=classify_api_error(CATALOG,{'logs':{'blender.log':{'text':api}}})
        assert classified is not None
        self.assertEqual(classified['category'],'api_correction')
        for text in ["AttributeError: 'Mesh' object has no attribute 'update'", "AttributeError: 'dict' object has no attribute 'invented'",api+'\nValueError: Empty or degenerate geometry: gutter',"ReferenceError: StructRNA of type Object has been removed"]:
            self.assertIsNone(classify_api_error(CATALOG,{'logs':{'log':{'text':text}}}))

    def test_api_accounting_preserves_failed_rows_and_hard_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            guard=SubmissionGuard(Path(folder)/'guard.sqlite')
            with guard.connect() as db:
                db.execute("INSERT INTO attempts VALUES('api','source','author','api-job','failed')")
                db.execute("INSERT INTO attempts VALUES('geometry','source','author','geo-job','failed')")
            guard.record_api_correction('api-job',{'category':'api_correction','message':'Verified missing API'})
            self.assertEqual(len(guard.rows()),2)
            self.assertEqual(guard.summary()['failed_count'],1)
            self.assertEqual(guard.summary()['historical_failed_count'],2)
            self.assertEqual(guard.summary()['api_correction_count'],1)
            self.assertEqual(budget_accounting(guard.path,guard.rows())['reset_id'],0)
