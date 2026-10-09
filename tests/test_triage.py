import hashlib
import http.client
import http.server
import io
import json
import math
import os
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
import unittest
import urllib.error
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'triage.py'
sys.path.insert(0, str(ROOT / 'scripts'))
import triage
from triage import ENDPOINT, build_request, evaluate, interpret, read_key


def no_utf8_mode(**extra):
    env = {**os.environ, **extra}
    env.pop('PYTHONUTF8', None)
    return env


class TriageTests(unittest.TestCase):
    def setUp(self):
        self.data = {'query': 'Tahliye ve depozito iadesi', 'candidates': [
            {'provider': 'a', 'source_id': '1', 'text': 'Taraf iddiası', 'full_text': False},
            {'provider': 'b', 'source_id': '1', 'text': 'Mahkeme gerekçesi', 'full_text': True}]}
        self.request = build_request(self.data)
        self.response = {'answers': {k: {'type': 'noul', 'noul': 0.2} for k in self.request['questions']}}

    def test_ranking_preserves_provenance_and_low_scores(self):
        self.response['answers']['relevant_1']['noul'] = 0.9
        result = interpret(self.request, self.response)
        self.assertEqual([x['provider'] for x in result['candidates']], ['b', 'a'])
        self.assertTrue(result['candidates'][1]['needs_full_text'])
        self.assertTrue(all(x['legal_review_required'] for x in result['candidates']))

    def test_invalid_probability_is_rejected(self):
        for value in (math.nan, math.inf, -1, 2, True, '0.9'):
            self.response['answers']['outside_scope']['noul'] = value
            with self.assertRaises(ValueError):
                interpret(self.request, self.response)

    def test_missing_answer_rejected(self):
        del self.response['answers']['route_tahliye']
        with self.assertRaises(ValueError):
            interpret(self.request, self.response)

    def test_non_object_inputs_and_responses_rejected(self):
        for value in ([], None, 'metin'):
            with self.assertRaises(ValueError):
                build_request(value)
            with self.assertRaises(ValueError):
                interpret(self.request, value)

    def test_duplicate_source_rejected(self):
        self.data['candidates'].append(self.data['candidates'][0])
        with self.assertRaises(ValueError):
            build_request(self.data)

    def test_source_completeness_cannot_be_assumed(self):
        del self.data['candidates'][0]['full_text']
        with self.assertRaises(ValueError):
            build_request(self.data)


class CandidateFieldTests(unittest.TestCase):
    def test_extra_candidate_fields_stay_local(self):
        data = {'query': 'Tahliye', 'candidates': [
            {'provider': 'p', 'source_id': '1', 'text': 'Metin', 'full_text': False,
             'client_phone': 'x', 'kunye': 'Yargıtay 3. HD, E. 1, K. 2, T. 01.01.2020'}]}
        request = build_request(data)
        sent = request['state']['candidates'][0]
        self.assertEqual(set(sent), {'provider', 'source_id', 'text', 'full_text', 'text_sha256'})
        self.assertNotIn('client_phone', triage.encode_request(request).decode('utf-8'))
        response = {'answers': {k: {'type': 'noul', 'noul': 0.5} for k in request['questions']}}
        ranked = interpret(request, response, data['candidates'])['candidates'][0]
        self.assertEqual(ranked['client_phone'], 'x')
        self.assertEqual(ranked['kunye'], data['candidates'][0]['kunye'])
        self.assertEqual(ranked['text_sha256'], sent['text_sha256'])

    def test_candidate_limits(self):
        def candidates(n, text='Metin'):
            return [{'provider': 'p', 'source_id': str(i), 'text': text, 'full_text': False}
                    for i in range(n)]
        build_request({'query': 'Tahliye', 'candidates': candidates(20)})
        for bad in (candidates(21), 'x'):
            with self.assertRaisesRegex(ValueError, 'en fazla 20'):
                build_request({'query': 'Tahliye', 'candidates': bad})
        with self.assertRaisesRegex(ValueError, 'Aday nesne olmalı'):
            build_request({'query': 'Tahliye', 'candidates': [1]})
        with self.assertRaisesRegex(ValueError, '180 KB'):
            build_request({'query': 'Tahliye', 'candidates': candidates(1, 'ş' * 200000)})
        with self.assertRaises(ValueError):
            build_request({'query': 'Tahliye', 'candidates': candidates(1, '  ')})

    def _big(self, n):
        return {'query': 'Tahliye', 'candidates': [
            {'provider': 'p', 'source_id': str(i), 'text': 'ş' * n, 'full_text': False}
            for i in range(20)]}

    def test_size_limit_measures_sent_body(self):
        request = build_request(self._big(4000))
        sent = {}

        def fake_open(req, timeout):
            sent['body'] = req.data
            sent['type'] = req.get_header('Content-type')
            return io.BytesIO(b'{}')
        with mock.patch.object(triage._OPENER, 'open', fake_open):
            triage.evaluate(request, 'k')
        self.assertLessEqual(len(sent['body']), triage.MAX_REQUEST_BYTES)
        self.assertEqual(json.loads(sent['body'].decode('utf-8')), request)
        self.assertEqual(sent['type'], 'application/json; charset=utf-8')

    def test_over_limit_rejected(self):
        with self.assertRaisesRegex(ValueError, '180 KB'):
            build_request(self._big(4100))

    def test_request_hash_covers_sent_bytes(self):
        request = build_request(self._big(10))
        response = {'answers': {k: {'type': 'noul', 'noul': 0.5} for k in request['questions']}}
        self.assertEqual(interpret(request, response)['request_sha256'],
                         hashlib.sha256(triage.encode_request(request)).hexdigest())


class NetworkErrorTests(unittest.TestCase):
    def setUp(self):
        self.request = build_request({'query': 'Tahliye', 'candidates': [
            {'provider': 'p', 'source_id': '1', 'text': 'Metin', 'full_text': False}]})

    def test_http_error_hides_body_and_key(self):
        error = urllib.error.HTTPError(ENDPOINT, 401, 'Unauthorized', {}, io.BytesIO(b'sk-SECRET'))
        with mock.patch.object(triage._OPENER, 'open', side_effect=error):
            with self.assertRaises(ValueError) as ctx:
                evaluate(self.request, 'sk-SECRET')
        self.assertNotIn('sk-SECRET', str(ctx.exception))
        self.assertIn('HTTP 401', str(ctx.exception))
        self.assertIsNone(ctx.exception.__cause__)

    def test_url_error_reports_reason(self):
        with mock.patch.object(triage._OPENER, 'open', side_effect=urllib.error.URLError('x')):
            with self.assertRaises(ValueError) as ctx:
                evaluate(self.request, 'k')
        self.assertEqual(str(ctx.exception), 'TypeSafe bağlantısı başarısız: x')

    def test_protocol_errors_and_non_json_body_are_labelled(self):
        cases = [(http.client.IncompleteRead(b''), 'IncompleteRead'),
                 (http.client.BadStatusLine('sunucu-metni'), 'BadStatusLine'),
                 (ConnectionResetError(), 'ConnectionResetError'),
                 (TimeoutError(), 'TimeoutError')]
        for error, name in cases:
            with mock.patch.object(triage._OPENER, 'open', side_effect=error):
                with self.assertRaises(ValueError) as ctx:
                    evaluate(self.request, 'k')
            self.assertEqual(str(ctx.exception), f'TypeSafe bağlantısı başarısız: {name}')
            self.assertNotIn('sunucu-metni', str(ctx.exception))
        for body in (b'<html>', b'\xff\xfe'):
            with mock.patch.object(triage._OPENER, 'open', return_value=io.BytesIO(body)):
                with self.assertRaisesRegex(ValueError, 'geçerli JSON değil'):
                    evaluate(self.request, 'k')

    def test_header_error_does_not_echo_key(self):
        error = ValueError("Invalid header value b'Bearer sk-SECRET\\nX'")
        with mock.patch.object(triage._OPENER, 'open', side_effect=error):
            with self.assertRaises(ValueError) as ctx:
                evaluate(self.request, 'sk-SECRET')
        self.assertNotIn('sk-SECRET', str(ctx.exception))

    def test_redirect_is_not_followed_and_key_not_forwarded(self):
        seen = []

        class Sink(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                seen.append(self.headers.get('Authorization'))
                self.send_response(200)
                self.send_header('Content-Length', '2')
                self.end_headers()
                self.wfile.write(b'{}')
            do_POST = do_GET

            def log_message(self, *a):
                pass
        sink = http.server.HTTPServer(('127.0.0.1', 0), Sink)

        class Redirect(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                self.send_response(302)
                self.send_header('Location', f'http://127.0.0.1:{sink.server_port}/x')
                self.send_header('Content-Length', '0')
                self.end_headers()

            def log_message(self, *a):
                pass
        origin = http.server.HTTPServer(('127.0.0.1', 0), Redirect)
        for server in (origin, sink):
            threading.Thread(target=server.serve_forever, daemon=True).start()
            self.addCleanup(server.server_close)
            self.addCleanup(server.shutdown)
        with mock.patch.object(triage, 'ENDPOINT', f'http://127.0.0.1:{origin.server_port}/v1'), \
             mock.patch.dict(os.environ, {'no_proxy': '*', 'NO_PROXY': '*'}):
            with self.assertRaisesRegex(ValueError, 'HTTP 302'):
                triage.evaluate(self.request, 'sk-test')
        self.assertEqual(seen, [])


class ReadKeyTests(unittest.TestCase):
    def env_file(self, content):
        handle = tempfile.NamedTemporaryFile('w', encoding='utf-8', suffix='.env', delete=False)
        with handle:
            handle.write(content)
        self.addCleanup(os.unlink, handle.name)
        return handle.name

    def read_file(self, content, environ=None):
        with mock.patch.dict(os.environ, environ or {}, clear=environ is None):
            return read_key(self.env_file(content))

    def test_env_file_parsing(self):
        cases = {
            'TYPESAFE_API_KEY=sk-abc # kişisel\n': 'sk-abc',
            'TYPESAFE_API_KEY="sk-abc" # yorum\n': 'sk-abc',
            "TYPESAFE_API_KEY='sk-abc'\n": 'sk-abc',
            'export\tTYPESAFE_API_KEY=sk-abc\n': 'sk-abc',
            'TYPESAFE_API_KEY=sk-a#b\n': 'sk-a#b',
            '# TYPESAFE_API_KEY=old\nTYPESAFE_API_KEY=sk-new\n': 'sk-new',
            '﻿# TYPESAFE_API_KEY=yanlis\nexport TYPESAFE_API_KEY="sk-dosya"\n': 'sk-dosya',
            'OTHER=1\r\nTYPESAFE_API_KEY=sk-crlf\r\n': 'sk-crlf',
        }
        for content, expected in cases.items():
            with self.subTest(content=content):
                self.assertEqual(self.read_file(content), expected)

    def test_last_empty_assignment_is_an_error(self):
        with self.assertRaisesRegex(ValueError, 'ataması yok veya boş'):
            self.read_file('TYPESAFE_API_KEY=sk-abc\nTYPESAFE_API_KEY=\n')
        with self.assertRaisesRegex(ValueError, 'ataması yok veya boş'):
            self.read_file('BASKA=1\n')

    def test_explicit_env_file_wins_over_environment(self):
        self.assertEqual(self.read_file('TYPESAFE_API_KEY=sk-file\n', {'TYPESAFE_API_KEY': 'sk-stale'}),
                         'sk-file')
        with mock.patch.dict(os.environ, {'TYPESAFE_API_KEY': 'sk-stale'}):
            with self.assertRaises(OSError):
                read_key(str(Path(tempfile.gettempdir()) / 'kira-yok-boyle-dosya' / '.env'))

    def test_environment_variable(self):
        with mock.patch.dict(os.environ, {'TYPESAFE_API_KEY': '  sk-ortam  '}):
            self.assertEqual(read_key(), 'sk-ortam')
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, 'eksik'):
                read_key()

    def test_malformed_key_is_rejected_without_echo(self):
        for bad in ('sk-gizli\nX', 'sk-gizli\rX: y', 'sk gizli', 'sk-gizliş', 'sk-gizli\x7f'):
            with self.subTest(bad=bad):
                with mock.patch.dict(os.environ, {'TYPESAFE_API_KEY': bad}):
                    with self.assertRaises(ValueError) as ctx:
                        read_key()
                self.assertNotIn('sk-gizli', str(ctx.exception))
                self.assertNotIn('sk gizli', str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            self.read_file('TYPESAFE_API_KEY=sk-gizli şifre\n')
        self.assertNotIn('sk-gizli', str(ctx.exception))


class CliTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='kira-triage-')
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.input = self.dir / 'girdi.json'
        self.query = 'Tahliye taahhüdü ve kısa süreli kira'
        self.input.write_text(json.dumps({'query': self.query, 'candidates': [
            {'provider': 'ornek', 'source_id': 'temsili-1', 'text': 'Kiracı ılık yanıt verdi.',
             'full_text': False, 'kunye': 'yerel alan'}]}, ensure_ascii=False), encoding='utf-8')

    def run_cli(self, *args, **env):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True,
                              cwd=self.dir, env=no_utf8_mode(**env))

    def test_dry_run_under_legacy_windows_encoding(self):
        proc = self.run_cli(str(self.input), '--dry-run', PYTHONIOENCODING='cp1252')
        self.assertEqual(proc.returncode, 0, proc.stderr.decode('utf-8', 'replace'))
        result = json.loads(proc.stdout.decode('utf-8'))
        self.assertEqual(result['state']['query'], self.query)
        self.assertNotIn('kunye', result['state']['candidates'][0])
        proc = self.run_cli('--help', PYTHONIOENCODING='cp1252')
        self.assertEqual(proc.returncode, 0, proc.stderr.decode('utf-8', 'replace'))
        self.assertIn('TYPESAFE_API_KEY', proc.stdout.decode('utf-8'))

    def test_output_file_is_written_once_and_checked_before_key(self):
        out = self.dir / 'sonuc.json'
        proc = self.run_cli(str(self.input), '--dry-run', '--output', str(out))
        self.assertEqual(proc.returncode, 0, proc.stderr.decode('utf-8', 'replace'))
        self.assertEqual(proc.stdout, b'')
        self.assertEqual(json.loads(out.read_text(encoding='utf-8'))['state']['query'], self.query)
        before = out.read_bytes()
        # Canlı mod: anahtar okunmadan ve ağa çıkılmadan önce mevcut dosya reddedilir.
        proc = self.run_cli(str(self.input), '--output', str(out), TYPESAFE_API_KEY='')
        self.assertEqual(proc.returncode, 1)
        stderr = proc.stderr.decode('utf-8')
        self.assertTrue(stderr.startswith('HATA: '), stderr)
        self.assertIn('zaten var', stderr)
        self.assertEqual(out.read_bytes(), before)
        proc = self.run_cli(str(self.input), '--output', str(self.dir / 'yok' / 'sonuc.json'))
        self.assertEqual(proc.returncode, 1)
        self.assertIn('Çıktı klasörü yok', proc.stderr.decode('utf-8'))

    def test_invalid_input_json_is_labelled(self):
        self.input.write_text('{bozuk', encoding='utf-8')
        proc = self.run_cli(str(self.input), '--dry-run', PYTHONIOENCODING='cp1254')
        self.assertEqual(proc.returncode, 1)
        self.assertIn('HATA: Girdi geçerli JSON değil', proc.stderr.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
