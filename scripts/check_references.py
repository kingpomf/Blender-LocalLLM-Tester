"""Validate the image-first prerequisite without submitting jobs or loading models."""
import hashlib
import json
from pathlib import Path
import subprocess
try:
    from .trial_settings import TRIAL
except ImportError:
    from trial_settings import TRIAL

ROLES = {'overview', 'layout', 'details'}


def image_dimensions(path):
    try:
        from PIL import Image
    except ImportError:
        python = Path(__file__).resolve().parents[2] / 'imageMCP/.venv/bin/python'
        code = ('from PIL import Image;import sys,json;'
                'im=Image.open(sys.argv[1]);im.verify();'
                'im=Image.open(sys.argv[1]);im.load();print(json.dumps(list(im.size)))')
        result = subprocess.run([str(python),'-c',code,str(path)],capture_output=True,text=True,timeout=30,check=True)
        return tuple(json.loads(result.stdout))
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        image.load()
        return image.size


def check(root, require_review=True):
    root = Path(root).resolve()
    folder = root / 'artifacts/references'
    manifest = folder / 'manifest.json'
    issues = []
    if not manifest.is_file():
        return {'passed': False, 'issues': ['Generate imageMCP references first; artifacts/references/manifest.json is missing.']}
    try:
        data = json.loads(manifest.read_text())
        images = data['images']
        if data.get('trial') != TRIAL:
            issues.append('Reference manifest belongs to another trial.')
        if {image['role'] for image in images} != ROLES or len(images) != len(ROLES):
            issues.append('Require exactly one overview, layout and details reference.')
        if len({image['job_id'] for image in images}) != len(images) or len({image['sha256'] for image in images}) != len(images):
            issues.append('Reference roles require distinct image jobs and image bytes.')
        for image in images:
            if image.get('tool') != 'imageMCP' or image.get('state') != 'completed':
                issues.append('Every reference must be a completed imageMCP job.')
            for key in ('job_id', 'provider', 'model', 'prompt'):
                if not isinstance(image.get(key), str) or not image[key].strip():
                    issues.append('Reference provenance is missing ' + key + '.')
            path = (root / image['path']).resolve()
            if not path.is_relative_to(folder.resolve()) or not path.is_file():
                issues.append('Reference file missing or outside artifacts/references.')
                continue
            with path.open('rb') as source:
                checksum = hashlib.file_digest(source, 'sha256').hexdigest()
            if checksum != image['sha256'] or path.stat().st_size != image['bytes']:
                issues.append('Reference size/SHA-256 mismatch: ' + image['path'])
            dimensions = image_dimensions(path)
            if dimensions != (image['width'],image['height']) or min(dimensions)<256:
                issues.append('Reference dimensions mismatch or too small: ' + image['path'])
            receipt_path = (root / image['receipt']).resolve()
            if not receipt_path.is_relative_to(folder.resolve()) or not receipt_path.is_file():
                issues.append('Missing imageMCP result receipt.')
                continue
            receipt = json.loads(receipt_path.read_text())
            if receipt.get('job_id') != image['job_id'] or receipt.get('status') != 'succeeded' or receipt.get('model') != image['model']:
                issues.append('Image job identity/state differs from imageMCP receipt.')
            artifacts = receipt.get('artifacts',[])
            if not any(a.get('sha256')==checksum and a.get('bytes')==path.stat().st_size and
                       (a.get('width'),a.get('height'))==dimensions and
                       Path(a.get('local_path','')).resolve()==path for a in artifacts):
                issues.append('Image is not the verified artifact in its imageMCP receipt.')
        notes = folder / 'DESIGN_GUIDE.md'
        if not require_review:
            return {'passed':not issues,'issues':issues,'manifest':str(manifest)}
        if not notes.is_file():
            issues.append('Write artifacts/references/DESIGN_GUIDE.md before Blender authoring.')
        else:
            text = notes.read_text()
            if len(text.strip()) < 200 or any(Path(image['path']).name not in text for image in images):
                issues.append('Design guide must discuss each reference and the features used for construction.')
            if data.get('inspection_method') != 'visual' or not data.get('reviewer_model'):
                issues.append('A vision-capable reviewer must inspect actual image pixels before authoring.')
            reviews = data.get('visual_review',[])
            if {r.get('sha256') for r in reviews} != {i['sha256'] for i in images} or any(len(r.get('observations','').strip())<80 for r in reviews):
                issues.append('Record image-derived observations for every reference hash.')
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError) as error:
        issues.append('Invalid reference manifest: ' + str(error))
    return {'passed': not issues, 'issues': issues, 'manifest': str(manifest)}


if __name__ == '__main__':
    result = check(Path(__file__).resolve().parents[1])
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
