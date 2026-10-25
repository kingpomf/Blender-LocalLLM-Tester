import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('resume',Path(__file__).resolve().parents[1]/'scripts/check_resume.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
class ResumeTests(unittest.TestCase):
    def test_fresh_and_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); (p/'RUN_STATE.json').write_text(json.dumps(dict(phase='BUILD',status='NOT_STARTED',jobs=[])))
            self.assertEqual(m.errors(p),[])
            (p/'artifacts/blend').mkdir(parents=True); (p/'artifacts/blend/Kart01.blend').write_bytes(b'old')
            self.assertTrue(m.errors(p))
    def test_completion_requires_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); (p/'RUN_STATE.json').write_text(json.dumps(dict(phase='DELIVER',status='COMPLETE',jobs=[])))
            self.assertTrue(m.errors(p))
if __name__=='__main__': unittest.main()
