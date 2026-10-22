"""Install the official pinned Linux runtime alongside the shared Blender version.

Run this script on Z6 with --tools pointing at the worker's tools directory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import tarfile

VERSION = '5.2.3'
ARCHIVE = f'blender-{VERSION}-linux-x64.tar.xz'
SHA256 = '78486c018b4443efe5e75ab54c290ed8c15abafd249b862c2c9ce2530a918eec'
URL = f'https://download.blender.org/release/Blender5.2/{ARCHIVE}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tools', type=Path, required=True)
    args = parser.parse_args()
    assert platform.system() == 'Linux' and platform.machine() == 'x86_64'
    tools = args.tools.resolve(strict=True)
    destination = tools / ARCHIVE.removesuffix('.tar.xz')
    if destination.exists():
        raise SystemExit('Destination exists; inspect it rather than overwriting it.')
    archive = tools / ARCHIVE
    if not archive.exists():
        partial = tools / (ARCHIVE + '.partial')
        with partial.open('xb') as output:
            subprocess.run(['curl', '--fail', '--location', '--silent', '--show-error',
                            '--max-time', '600', URL], stdout=output, check=True)
        partial.rename(archive)
    with archive.open('rb') as source:
        actual = hashlib.file_digest(source, 'sha256').hexdigest()
    assert actual == SHA256, 'Official archive checksum mismatch; no extraction performed'
    with tarfile.open(archive) as package:
        assert all(Path(m.name).parts[0] == destination.name for m in package.getmembers())
        package.extractall(tools, filter='data')
    version = subprocess.check_output([str(destination / 'blender'), '--version'], text=True)
    print(json.dumps({'binary': str(destination / 'blender'), 'archive_sha256': actual,
                      'version_output': version}, indent=2))


if __name__ == '__main__':
    main()
