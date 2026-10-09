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
from udf import UdfError, check, read  # noqa: E402


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


TEMPLATE = ('<?xml version="1.0" encoding="UTF-8" ?><template format_id="1.8">'
            '<content><![CDATA[\nKURGU MAHKEMESİNE\nDAVACI\t: ...\n]]></content>'
            '<elements resolver="hvl-default"><paragraph><content startOffset="0" length="1" /></paragraph>'
            '<paragraph><content bold="true" startOffset="1" length="17" /></paragraph></elements></template>')


class UdfReadTests(unittest.TestCase):
    def test_reads_text_structure_and_blanks(self):
        result = read(udf_bytes(TEMPLATE))
        self.assertEqual(result['format_id'], '1.8')
        self.assertEqual(result['paragraf'], 2)
        self.assertTrue(result['metin'].startswith('\nKURGU MAHKEMESİNE'))
        self.assertEqual(result['bos_alan']['uc_nokta'], 1)
        self.assertTrue(result['uyarilar'])

    def test_rejects_entities_missing_text_and_offsets_outside(self):
        for content in ('<!DOCTYPE t [<!ENTITY a "x">]><template><content>&a;</content></template>',
                        '<template><elements /></template>', '<template><content>açık'):
            with self.subTest(content[:20]):
                with self.assertRaises(UdfError):
                    read(udf_bytes(content))
        result = read(udf_bytes(TEMPLATE.replace('length="17"', 'length="999"')))
        self.assertIn('dışına', ' '.join(result['uyarilar']))


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

    def test_oku_prints_text_or_json(self):
        with tempfile.TemporaryDirectory(prefix='kira-udf-') as directory:
            path = Path(directory) / 'dilekce.udf'
            path.write_bytes(udf_bytes(TEMPLATE))
            run = lambda *a: subprocess.run([sys.executable, str(ROOT / 'scripts/udf.py'), 'oku', *a],
                                            capture_output=True)
            text = run(str(path))
            self.assertEqual(text.returncode, 0)
            self.assertTrue(text.stdout.decode('utf-8').startswith('KURGU MAHKEMESİNE'))
            data = json.loads(run(str(path), '--json').stdout.decode('utf-8'))
            self.assertTrue(data['okundu'])
            self.assertEqual(data['paragraf'], 2)
            other = Path(directory) / 'duz.udf'
            other.write_bytes(b'duz metin')
            self.assertEqual(run(str(other)).returncode, 2)


if __name__ == '__main__':
    unittest.main()
