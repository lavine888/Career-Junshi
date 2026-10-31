"""Fetch pinned public OCR/PDF runtime assets; no installation scripts or user data."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import os
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / 'vendor'
TESSDATA = '87416418657359cb625c412a48b6e1d6d41c29bd'


def main():
    VENDOR.mkdir(exist_ok=True)
    cache = Path(os.environ.get('JUNSHI_VENDOR_CACHE', str(ROOT.parent.parent.parent / 'Career-Junshi-private' / 'vendor-cache')))
    cache.mkdir(parents=True, exist_ok=True)
    receipt = []
    opener = urllib.request.build_opener()

    def get(url):
        path = cache / hashlib.sha256(url.encode()).hexdigest()
        if not path.exists():
            request = urllib.request.Request(url, headers={'User-Agent': 'Career-Junshi-local-build/0.1'})
            with opener.open(request, timeout=60) as response:
                data = response.read(45 * 1024 * 1024 + 1)
            if len(data) > 45 * 1024 * 1024:
                raise ValueError('Asset exceeds build download limit')
            path.write_bytes(data)
        return path.read_bytes()

    def put(relative, data, url):
        path = VENDOR / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        receipt.append({'path': relative, 'source': url, 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})

    packages = [
        ('tesseract.js', '7.0.0', {'dist/tesseract.min.js': 'ocr/tesseract.min.js', 'dist/worker.min.js': 'ocr/worker.min.js', 'LICENSE.md': 'licenses/tesseract-js.txt'}),
        ('tesseract.js-core', '7.0.0', {}),
        ('pdfjs-dist', '6.4.299', {'build/pdf.mjs': 'pdf/pdf.mjs', 'build/pdf.worker.mjs': 'pdf/pdf.worker.mjs', 'LICENSE': 'licenses/pdfjs.txt'}),
    ]
    for package, version, wanted in packages:
        url = f'https://registry.npmjs.org/{package}/-/{package}-{version}.tgz'
        with tarfile.open(fileobj=io.BytesIO(get(url)), mode='r:gz') as archive:
            if package == 'tesseract.js-core':
                wanted = {m.name.removeprefix('package/'): 'ocr/core/' + Path(m.name).name
                          for m in archive.getmembers() if m.isfile() and (m.name.endswith('.wasm') or m.name.endswith('.wasm.js'))}
                for license_name in ('LICENSE', 'LICENSE.md'):
                    if 'package/' + license_name in archive.getnames():
                        wanted[license_name] = 'licenses/tesseract-core.txt'
                        break
            for member, destination in wanted.items():
                stream = archive.extractfile('package/' + member)
                if stream is None:
                    raise ValueError('Missing asset: ' + member)
                put(destination, stream.read(), url + '#' + member)
    for lang in ('eng', 'chi_sim'):
        url = f'https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/{TESSDATA}/{lang}.traineddata'
        put(f'ocr/lang/{lang}.traineddata.gz', gzip.compress(get(url), mtime=0), url)
    url = f'https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/{TESSDATA}/LICENSE'
    put('licenses/tessdata-fast.txt', get(url), url)
    (VENDOR / 'assets.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'files': len(receipt), 'bytes': sum(x['bytes'] for x in receipt), 'runtime_network': False}))


if __name__ == '__main__':
    main()
