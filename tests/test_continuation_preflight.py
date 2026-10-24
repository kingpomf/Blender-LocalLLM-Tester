import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from contextlib import closing

from scripts import continuation_preflight as preflight
from scripts.trial_settings import MODEL, TRIAL


class ContinuationPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.source='a'*32
        self.database=self.root/'.runtime/blender52/submissions.sqlite'
        self.database.parent.mkdir(parents=True)
        with closing(sqlite3.connect(self.database)) as db, db:
            db.execute('CREATE TABLE attempts(fingerprint TEXT,source TEXT,operation TEXT,job TEXT,state TEXT)')
            db.executemany('INSERT INTO attempts VALUES(?,?,?,?,?)',[
                ('1','EMPTY','author',self.source,'completed'),
                ('2',self.source,'author','b'*32,'failed'),
                ('3',self.source,'author','c'*32,'failed')])
        self.checkpoint=self.root/'artifacts/blend/BowlingPair01.blend'
        self.checkpoint.parent.mkdir(parents=True)
        self.checkpoint.write_bytes(b'fixture-only')
        self.plan_path=self.root/'testing/reconciliation-20261024/continuation.json'
        self.plan_path.parent.mkdir(parents=True)
        self.plan={'model':MODEL,'trial':TRIAL,'source_job':self.source,
            'checkpoint':'artifacts/blend/BowlingPair01.blend',
            'checkpoint_sha256':hashlib.sha256(self.checkpoint.read_bytes()).hexdigest(),
            'guard_rows_sha256':preflight.rows_hash(preflight.guard_rows(self.root)),
            'limits':{'per_source':6,'total':12}}
        self.plan_path.write_text(json.dumps(self.plan))

    def validate(self):
        with patch.object(preflight,'reference_check',return_value={'passed':True,'issues':[]}), patch.object(preflight,'resume_check',return_value={'passed':True,'issues':[],'last_verified_source':self.source}):
            return preflight.validate(self.root)

    def test_preserves_history_and_reports_remaining_budget(self):
        before=preflight.guard_rows(self.root)
        result=self.validate()
        self.assertEqual(result['failures_retained'],2)
        self.assertEqual(result['remaining_on_source'],4)
        self.assertEqual(result['remaining_total'],10)
        self.assertEqual(before,preflight.guard_rows(self.root))

    def test_changed_checkpoint_blocks(self):
        self.checkpoint.write_bytes(b'changed')
        with self.assertRaisesRegex(AssertionError,'checkpoint changed'):
            self.validate()

    def test_changed_or_pending_guard_history_blocks(self):
        with closing(sqlite3.connect(self.database)) as db, db:
            db.execute("INSERT INTO attempts VALUES('4',?,'author',?,'queued')",(self.source,'d'*32))
        with self.assertRaisesRegex(AssertionError,'Guard history changed'):
            self.validate()

    def test_different_trial_or_model_blocks(self):
        self.plan['model']='z6-llama/qwen38-27b'
        self.plan_path.write_text(json.dumps(self.plan))
        with self.assertRaisesRegex(AssertionError,'model/trial changed'):
            self.validate()


if __name__=='__main__':
    unittest.main()
