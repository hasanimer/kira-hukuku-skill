import base64
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from udf import UdfError, check  # noqa: E402


def udf_bytes(content='<template><content><![CDATA[KURGU SINAMA METNİ]]></content></template>',
              name='content.xml'):
    # Kurgu içerik; gerçek dilekçe veya Legaluga yanıtı değildir.
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(name, content.encode('utf-8'))
    return buffer.getvalue()


def encoded(data):
    return base64.b64encode(data), hashlib.sha256(data).hexdigest()


class UdfCheckTests(unittest.TestCase):
    def test_valid_payload_returns_original_bytes(self):
        data = udf_bytes()
        raw, digest = encoded(data)
        result, actual, names = check(raw, digest.upper(), 'taslak.udf')
        self.assertEqual(result, data)
        self.assertEqual(actual, digest)
        self.assertEqual(names, ['content.xml'])

    def test_wrapped_and_utf16_input_is_accepted(self):
        data = udf_bytes()
        raw, digest = encoded(data)
        wrapped = b'\n'.join(raw[i:i + 60] for i in range(0, len(raw), 60)) + b'\r\n'
        self.assertEqual(check(wrapped, digest, 'a.udf')[0], data)
        self.assertEqual(check(raw.decode('ascii').encode('utf-16'), digest, 'a.udf')[0], data)

    def test_integrity_failures_are_rejected(self):
        data = udf_bytes()
        raw, digest = encoded(data)
        cases = {
            'extension': (raw, digest, 'taslak.txt'),
            'base64': (raw + b'*', digest, 'a.udf'),
            'sha': (raw, '0' * 64, 'a.udf'),
            'truncated': (raw[:-8], hashlib.sha256(base64.b64decode(raw[:-8])).hexdigest(), 'a.udf'),
        }
        not_zip = b'duz metin'
        cases['not_zip'] = (*encoded(not_zip), 'a.udf')
        cases['no_content'] = (*encoded(udf_bytes(name='other.xml')), 'a.udf')
        cases['placeholder'] = (*encoded(udf_bytes(
            '<content><![CDATA[Tebliğ tarihi: [DOLDURULACAK: tarih]]]></content>')), 'a.udf')
        for label, args in cases.items():
            with self.subTest(label):
                with self.assertRaises(UdfError):
                    check(*args)


class UdfCliTests(unittest.TestCase):
    def run_cli(self, *args, stdin=None):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/udf.py'), 'kaydet', *args],
                              input=stdin, capture_output=True)

    def test_save_refuses_overwrite_and_bad_hash(self):
        data = udf_bytes()
        raw, digest = encoded(data)
        with tempfile.TemporaryDirectory(prefix='kira-udf-') as directory:
            source = Path(directory) / 'yanit.b64'
            source.write_bytes(raw)
            target = Path(directory) / 'taslak.udf'
            ok = self.run_cli(str(source), '--sha256', digest, '--cikti', str(target))
            self.assertEqual(ok.returncode, 0, ok.stderr.decode('utf-8'))
            result = json.loads(ok.stdout.decode('utf-8'))
            self.assertTrue(result['kaydedildi'])
            self.assertEqual(result['bayt'], len(data))
            self.assertEqual(target.read_bytes(), data)
            again = self.run_cli(str(source), '--sha256', digest, '--cikti', str(target))
            self.assertEqual(again.returncode, 1)
            self.assertEqual(target.read_bytes(), data)
            other = Path(directory) / 'baska.udf'
            bad = self.run_cli('-', '--sha256', '0' * 64, '--cikti', str(other), stdin=raw)
            self.assertEqual(bad.returncode, 2)
            failure = json.loads(bad.stdout.decode('utf-8'))
            self.assertFalse(failure['kaydedildi'])
            self.assertTrue(failure['yedek'].startswith('https://'))
            self.assertFalse(other.exists())
            self.assertNotIn(raw.decode('ascii')[:40], bad.stdout.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
