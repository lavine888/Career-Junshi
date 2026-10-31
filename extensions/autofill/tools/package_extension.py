"""Build a load-unpacked zip from reviewed source and hash-checked vendor assets."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.expanduser().absolute()
    if output.exists():
        raise ValueError('Preserve the existing package; choose a new output')
    assets = json.loads((ROOT / 'vendor/assets.json').read_text(encoding='utf-8'))
    for asset in assets:
        path = (ROOT / 'vendor' / asset['path']).resolve()
        if not path.is_relative_to((ROOT / 'vendor').resolve()) or path.is_symlink():
            raise ValueError('Invalid vendor path')
        if hashlib.sha256(path.read_bytes()).hexdigest() != asset['sha256']:
            raise ValueError('Vendor hash mismatch: ' + asset['path'])
    paths = [ROOT / x for x in ('manifest.json', 'background.js', 'panel.html', 'panel.css', 'panel.mjs', 'README.md', 'THIRD_PARTY.md')]
    paths += [p for sub in ('lib', 'licenses', 'vendor') for p in (ROOT / sub).rglob('*') if p.is_file()]
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            if path.is_symlink():
                raise ValueError('Do not package symlinks')
            archive.write(path, 'junshi-autofill/' + path.relative_to(ROOT).as_posix())
        archive.write(ROOT.parents[1] / 'LICENSE', 'junshi-autofill/LICENSE')
    print(json.dumps({'package': str(output), 'files': len(paths) + 1, 'bytes': output.stat().st_size,
                      'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
