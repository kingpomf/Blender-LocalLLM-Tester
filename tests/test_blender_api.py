import unittest
import json
import hashlib
from scripts.blender_api import inspect_api,lookup,classify_api_error,load_catalog
from scripts.submission_guard import SubmissionGuard,budget_accounting
from pathlib import Path
import tempfile


CATALOG={'version':'5.2.3 LTS','build_hash':'fixture','errors':{},'extras':{},'bmesh_ops':['recalc_face_normals'],
    'types':{
        'Mesh':{'members':['update','validate','from_pydata','vertices','name'],'properties':{},'functions':{'update':{'calc_edges':{}}}},
        'Object':{'members':['data','type','children','children_recursive','users_collection','parent'],'properties':{},'functions':{}},
    },
    'data_collections':{'meshes':{'target':'Mesh','members':['new','get','remove']},'objects':{'target':'Object','members':['new','get','remove']}},
    'operators':{'bpy.ops.mesh.primitive_cube_add':{'parameters':{'size':{},'location':{}},'description':'Add a cube'}},
    'runtime_returns':{'Object.children':{'python_type':'tuple','members':['count','index'],'element_type':'Object','guidance':'Use obj.parent or remove(obj, do_unlink=True).'},
        'Object.users_collection':{'python_type':'tuple','members':['count','index'],'element_type':'Collection','guidance':'Unlink from each Collection.objects instead.'}}}


class ApiTests(unittest.TestCase):
    def test_legacy_or_tampered_catalog_cannot_silently_disable_return_type_checks(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);reports=root/'artifacts/reports';reports.mkdir(parents=True)
            catalog=reports/'blender-api-catalog.json';receipt=reports/'blender-api-catalog-receipt.json'
            catalog.write_text(json.dumps(CATALOG))
            receipt.write_text(json.dumps({'sha256':hashlib.sha256(catalog.read_bytes()).hexdigest()}))
            with self.assertRaisesRegex(ValueError,'return-type catalog missing'):load_catalog(root)
            catalog.write_text(json.dumps({**CATALOG,'schema_version':2}))
            with self.assertRaisesRegex(ValueError,'hash changed'):load_catalog(root)
            receipt.write_text(json.dumps({'sha256':hashlib.sha256(catalog.read_bytes()).hexdigest()}))
            self.assertIsNotNone(load_catalog(root))
    def test_blender_tuple_return_and_alias_are_checked_but_custom_python_tuple_is_not(self):
        prefix="import bpy\nroot=bpy.data.objects.get('root')\n"
        for suffix in ['root.children.unlink(obj)','children=root.children\nchildren.unlink(obj)',
                       'root.users_collection.unlink(obj)',
                       'def cleanup():\n    root.children.unlink(obj)']:
            with self.subTest(suffix=suffix):
                issues=inspect_api(prefix+suffix,CATALOG)
                self.assertEqual(issues[0]['code'],'unsupported_return_member')
                self.assertEqual(issues[0]['runtime_type'],'tuple')
        self.assertEqual(inspect_api('children=()\nchildren.unlink(obj)',CATALOG),[])
        self.assertEqual(lookup(CATALOG,'Object.children')['runtime_return']['python_type'],'tuple')

    def test_shadowed_or_rebound_receivers_do_not_keep_stale_blender_provenance(self):
        prefix="import bpy\nroot=bpy.data.objects.get('root')\n"
        for suffix in ['def custom(root):\n    root.children.unlink(obj)',
                       'root=custom_object\nroot.children.unlink(obj)',
                       'for root in user_objects:\n    root.children.unlink(obj)',
                       'if condition:\n    root=custom_object\nroot.children.unlink(obj)',
                       "if root.type == 'MESH':\n    root=custom_object\n    root.data.custom_method()"]:
            with self.subTest(suffix=suffix):self.assertEqual(inspect_api(prefix+suffix,CATALOG),[])

    def test_tuple_runtime_error_requires_matching_source_line_and_api_provenance(self):
        code="import bpy\nroot=bpy.data.objects.get('root')\nroot.children.unlink(obj)"
        def diagnostics(line=3,message="AttributeError: 'tuple' object has no attribute 'unlink'"):
            return {'logs':{'blender.log':{'text':f'  File "/job/submitted.py", line {line}, in cleanup\n'+message}}}
        result=classify_api_error(CATALOG,diagnostics(),code)
        assert result is not None
        self.assertEqual(result['origin'],'Object.children')
        self.assertEqual(result['source_line'],3)
        self.assertIsNone(classify_api_error(CATALOG,diagnostics()))
        self.assertIsNone(classify_api_error(CATALOG,diagnostics(2),code))
        self.assertIsNone(classify_api_error(CATALOG,diagnostics(),"children=()\npass\nchildren.unlink(obj)"))
        self.assertIsNone(classify_api_error(CATALOG,diagnostics(message="ValueError: Empty or degenerate geometry: Gutter"),code))

    def test_keyword_runtime_error_requires_catalog_source_and_terminal_keyword_match(self):
        code='import bpy\nbpy.ops.mesh.primitive_cube_add(invented=1)'
        log='  File "/job/submitted.py", line 2, in f\nTypeError: keyword "invented" unrecognized'
        self.assertIsNotNone(classify_api_error(CATALOG,{'logs':{'blender.log':{'text':log}}},code))
        self.assertIsNone(classify_api_error(CATALOG,{'logs':{'blender.log':{'text':log}}}))
        self.assertIsNone(classify_api_error(CATALOG,{'logs':{'blender.log':{'text':log.replace('invented','size')}}},code))

    def test_final_worker_exception_wins_over_stale_python_log(self):
        api="AttributeError: 'Mesh' object has no attribute 'nonexistent'"
        diagnostics={'logs':{'blender.log':{'text':api+'\nValueError: Empty or degenerate geometry: Gutter'},'python-output.txt':{'text':api}}}
        self.assertIsNone(classify_api_error(CATALOG,diagnostics))
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
            rows=guard.rows()
            with guard.connect() as db:
                db.execute("INSERT INTO failure_budget_resets(cutoff_rowid,reason,created) VALUES(2,'explicit test reset',1)")
            summary=guard.summary()
            self.assertEqual(summary['failed_count'],0)
            self.assertEqual(summary['api_correction_count'],0)
            self.assertEqual(summary['historical_failed_count'],2)
            self.assertEqual(guard.rows(),rows)
            self.assertIsNotNone(guard.api_correction('api-job'))
