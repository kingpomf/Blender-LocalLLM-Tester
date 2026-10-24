import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image

from scripts.check_references import check


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.folder = self.root / 'artifacts/references'
        self.folder.mkdir(parents=True)

    def ready(self):
        images = []
        for index, role in enumerate(['overview', 'layout', 'details']):
            path = self.folder / (role + '.png')
            Image.new('RGB',(256,256),(index*80,90,120)).save(path)
            content = path.read_bytes()
            receipt = self.folder / (role + '.receipt.json')
            receipt.write_text(json.dumps({'job_id':'job-'+role,'status':'succeeded','model':'qwen-image-2.1-turbo',
                'artifacts':[{'local_path':str(path),'sha256':hashlib.sha256(content).hexdigest(),
                              'bytes':len(content),'width':256,'height':256}]}))
            images.append({'role':role, 'tool':'imageMCP', 'state':'completed',
                'job_id':'job-' + role, 'provider':'z6-fastapi', 'model':'qwen-image-2.1-turbo',
                'prompt':'Reference for ' + role, 'path':str(path.relative_to(self.root)),
                'bytes':len(content), 'sha256':hashlib.sha256(content).hexdigest(),
                'width':256,'height':256,'receipt':str(receipt.relative_to(self.root))})
        data = {'trial':'bowling52-qwen36-mtp-q8-20261023', 'inspection_method':'visual',
                'reviewer_model':'z6-llama/qwen38-27b','images':images,
                'visual_review':[{'sha256':i['sha256'],'observations':'The actual reference pixels show a uniform color panel, which is a test fixture rather than bowling alley geometry.'} for i in images]}
        self.write(data)
        (self.folder / 'DESIGN_GUIDE.md').write_text(
            'Use overview.png for composition, layout.png for arrangement and details.png for materials. '
            'Prompt-guided inspection only; no image vision claimed. Written specifications override '
            'the generated proportions, object counts, lettering and dimensions. Original geometry is required.')
        return data

    def write(self, data):
        (self.folder / 'manifest.json').write_text(json.dumps(data))

    def test_missing_references_block(self):
        self.assertFalse(check(self.root)['passed'])

    def test_ready_visual_set_with_receipts_passes(self):
        self.ready()
        self.assertTrue(check(self.root)['passed'])

    def test_pending_job_blocks(self):
        data = self.ready()
        data['images'][0]['state'] = 'queued'
        self.write(data)
        self.assertFalse(check(self.root)['passed'])

    def test_tampered_image_blocks(self):
        self.ready()
        (self.folder / 'layout.png').write_bytes(b'changed')
        self.assertFalse(check(self.root)['passed'])

    def test_old_trial_and_path_escape_block(self):
        data = self.ready()
        data['trial'] = 'old-trial'
        data['images'][0]['path'] = '../outside.png'
        self.write(data)
        self.assertFalse(check(self.root)['passed'])

    def test_missing_role_or_guide_blocks(self):
        data = self.ready()
        data['images'].pop()
        self.write(data)
        (self.folder / 'DESIGN_GUIDE.md').unlink()
        self.assertFalse(check(self.root)['passed'])

    def test_invalid_manifest_blocks(self):
        (self.folder / 'manifest.json').write_text('{')
        self.assertFalse(check(self.root)['passed'])

    def test_prompt_only_review_blocks(self):
        data = self.ready()
        data['inspection_method'] = 'prompt-guided'
        self.write(data)
        self.assertFalse(check(self.root)['passed'])

    def test_fake_png_with_matching_hash_blocks(self):
        data = self.ready()
        path = self.folder / 'overview.png'
        content = b'\x89PNG\r\n\x1a\nnot a PNG'
        path.write_bytes(content)
        data['images'][0].update(bytes=len(content),sha256=hashlib.sha256(content).hexdigest())
        self.write(data)
        self.assertFalse(check(self.root)['passed'])

    def test_duplicate_job_and_missing_receipt_block(self):
        data = self.ready()
        data['images'][0]['job_id'] = data['images'][1]['job_id']
        self.write(data)
        (self.folder / 'overview.receipt.json').unlink()
        self.assertFalse(check(self.root)['passed'])

    def test_false_receipt_identity_blocks(self):
        self.ready()
        path = self.folder / 'overview.receipt.json'
        receipt = json.loads(path.read_text())
        receipt['job_id'] = 'different-job'
        path.write_text(json.dumps(receipt))
        self.assertFalse(check(self.root)['passed'])


if __name__ == '__main__':
    unittest.main()
