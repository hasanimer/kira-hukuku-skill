import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import unicodedata
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pool import (BEDESTEN_URL, QUOTE_MAX_OCCURRENCES, enrich, kind_of, kunye,  # noqa: E402
                  load_pool, metadata, normalize, read_rows, term_pattern, text_decision_date)

MAIN = 'topic-rescan-assistant-adjusted.jsonl'
BAM = 'bam-selected.jsonl'
SCRIPT = ROOT / 'scripts/pool.py'


def row(document_id, text, kind, **extra):
    base = {'document_id': document_id, 'court': '3. Hukuk Dairesi', 'esas_no': '2017/1',
            'karar_no': '2019/2', 'karar_tarihi': '2019-05-28',
            'text': text, 'text_sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
            'value_assessment': {'icerik_turu': {'choice': kind}}}
    base.update(extra)
    return base


def write_rows(path, rows):
    path.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows),
                    encoding='utf-8')


def write_root(directory, main_rows, bam_rows=None, extra=None):
    """Geçici havuz kökü; extra: {dosya adı: kayıtlar} (ör. manifestte olmayan dosya)."""
    directory = Path(directory)
    write_rows(directory / MAIN, main_rows)
    if bam_rows is not None:
        write_rows(directory / BAM, bam_rows)
    for name, rows in (extra or {}).items():
        write_rows(directory / name, rows)
    return directory


def run_pool(directory, *args, env=None):
    command = [sys.executable, str(SCRIPT)]
    if directory is not None:
        command += ['--root', str(directory)]
    return subprocess.run(command + list(args), capture_output=True, timeout=120, env=env)


def parsed(proc):
    return json.loads(proc.stdout.decode('utf-8'))


def stderr_of(proc):
    return proc.stderr.decode('utf-8', errors='backslashreplace')


class PoolTests(unittest.TestCase):
    def test_bedesten_url_is_derived_only_for_numeric_ids(self):
        main = enrich(row('525578700', 'metin', 'esas_gerekcesi'), bedesten_ids=True)
        self.assertEqual(main['source_url'], BEDESTEN_URL.format('525578700'))
        self.assertEqual(main['source_provider'], 'Bedesten (kimlikten türetildi)')
        self.assertEqual(main['court_type'], 'yargitay')
        uuid = enrich(row('615160e1-265c', 'metin', 'esas_gerekcesi',
                          court='Denizli Bölge Adliye Mahkemesi 6. Hukuk Dairesi'),
                      bedesten_ids=True)
        self.assertIsNone(uuid.get('source_url'))
        self.assertIsNone(uuid.get('court_type'))
        bam = enrich(row('987654', 'metin', 'esas_gerekcesi',
                         court='Ankara Bölge Adliye Mahkemesi 6. Hukuk Dairesi'))
        self.assertIsNone(bam.get('source_url'))
        self.assertIsNone(bam.get('source_provider'))

    def test_bedesten_url_is_not_derived_for_selection_files(self):
        selection = row('987654', 'kira metin', 'esas_gerekcesi',
                        court='Ankara Bölge Adliye Mahkemesi 6. Hukuk Dairesi', court_type='bam')
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, [row('2', 'kira metin', 'esas_gerekcesi')], [selection])
            bam = run_pool(directory, 'get', '987654')
            main = run_pool(directory, 'get', '2')
        self.assertEqual(bam.returncode, 0, stderr_of(bam))
        self.assertIsNone(parsed(bam)['source_url'])
        self.assertIsNone(parsed(bam)['source_provider'])
        self.assertEqual(parsed(bam)['pool_file'], BAM)
        self.assertEqual(parsed(main)['source_url'], BEDESTEN_URL.format('2'))

    def test_written_source_url_is_not_overwritten(self):
        given = enrich(row('123', 'metin', 'esas_gerekcesi', source_url='https://example.org/x',
                           source_provider='Dejure', court_type='bam'), bedesten_ids=True)
        self.assertEqual(given['source_url'], 'https://example.org/x')
        self.assertEqual(given['source_provider'], 'Dejure')
        self.assertEqual(given['court_type'], 'bam')

    def test_kunye_uses_court_name_and_petition_format(self):
        self.assertEqual(kunye(row('1', 'm', 'kisa_karar')),
                         'Yargıtay 3. HD, E. 2017/1, K. 2019/2, T. 28.05.2019')
        self.assertEqual(kunye(row('2', 'm', 'kisa_karar', court='Hukuk Genel Kurulu')),
                         'Yargıtay HGK, E. 2017/1, K. 2019/2, T. 28.05.2019')
        self.assertEqual(kunye(row('3', 'm', 'kisa_karar',
                                   court='Denizli Bölge Adliye Mahkemesi 6. Hukuk Dairesi')),
                         'Denizli BAM 6. HD, E. 2017/1, K. 2019/2, T. 28.05.2019')
        self.assertEqual(kunye(row('4', 'm', 'kisa_karar', court='Hukuk Daireleri Başkanlar Kurulu')),
                         'Yargıtay HDBK, E. 2017/1, K. 2019/2, T. 28.05.2019')

    def test_written_kunye_is_rebuilt_from_structured_fields(self):
        stale = enrich(row('5', 'm', 'kisa_karar', kunye='Yargıtay 3. HD, E. 1999/1'))
        self.assertEqual(stale['kunye'], 'Yargıtay 3. HD, E. 2017/1, K. 2019/2, T. 28.05.2019')

    def test_empty_court_is_rejected(self):
        with self.assertRaises(ValueError):
            kunye(row('9', 'm', 'kisa_karar', court=''))
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            path = Path(directory) / MAIN
            write_rows(path, [row('9', 'm', 'kisa_karar', court=' ')])
            with self.assertRaisesRegex(ValueError, 'Missing court'):
                list(read_rows(path))

    def test_search_ranks_reasoned_decisions_before_short_ones(self):
        rows = [row('1', 'kira kira kira onama', 'kisa_karar'),
                row('2', 'kira bedeli hak ve nesafet gerekçesi', 'esas_gerekcesi'),
                row('3', 'kira usul', 'usul_gerekcesi')]
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, rows)
            out = run_pool(directory, 'search', 'kira')
        self.assertEqual(out.returncode, 0, stderr_of(out))
        result = parsed(out)
        self.assertEqual([r['document_id'] for r in result['results']], ['2', '3', '1'])
        self.assertEqual(result['results'][0]['kunye'],
                         'Yargıtay 3. HD, E. 2017/1, K. 2019/2, T. 28.05.2019')
        self.assertEqual(result['results'][0]['source_url'], BEDESTEN_URL.format('2'))
        self.assertEqual(result['results'][0]['pool_file'], MAIN)
        self.assertEqual(list(result['pool_files']), [MAIN])
        self.assertIs(result['manifest_verified'], False)
        # Çıktı zarfı yerel mutlak yol içermez.
        self.assertNotIn(str(Path(directory).resolve()), out.stdout.decode('utf-8'))
        self.assertNotIn('source_file', result)

    def test_load_pool_returns_rows_and_envelope(self):
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, [row('1', 'kira', 'esas_gerekcesi')],
                       [row('b1', 'kira', 'esas_gerekcesi', court_type='bam',
                            court='Ankara Bölge Adliye Mahkemesi 6. Hukuk Dairesi')])
            rows, envelope = load_pool(Path(directory))
        self.assertEqual([r['document_id'] for r in rows], ['1', 'b1'])
        self.assertEqual(envelope['records'], 2)
        self.assertEqual(list(envelope['pool_files']), [MAIN, BAM])
        self.assertIs(envelope['manifest_verified'], False)

    def test_manifest_is_verified_when_present(self):
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            root = write_root(directory, [row('1', 'kira metni', 'esas_gerekcesi')])
            digest = hashlib.sha256((root / MAIN).read_bytes()).hexdigest()
            (root / 'manifest.json').write_text(json.dumps({'files': {MAIN: digest}}),
                                                encoding='utf-8')
            ok = run_pool(root, 'get', '1')
            self.assertEqual(ok.returncode, 0, stderr_of(ok))
            self.assertIs(parsed(ok)['manifest_verified'], True)
            # Metin ve metin hash'i geçerli; yalnız künye bilgisi değiştirildi.
            write_rows(root / MAIN, [row('1', 'kira metni', 'esas_gerekcesi', esas_no='1999/1')])
            tampered = run_pool(root, 'get', '1')
            self.assertEqual(tampered.returncode, 1)
            self.assertIn('manifest', stderr_of(tampered))
            self.assertEqual(tampered.stdout, b'')
            # Manifestte yer almayan havuz dosyası da reddedilir.
            write_rows(root / MAIN, [row('1', 'kira metni', 'esas_gerekcesi')])
            write_rows(root / BAM, [row('b1', 'kira', 'esas_gerekcesi', court_type='bam',
                                        court='Ankara Bölge Adliye Mahkemesi 6. Hukuk Dairesi')])
            unpinned = run_pool(root, 'stats')
            self.assertEqual(unpinned.returncode, 1)
            self.assertIn('not pinned', stderr_of(unpinned))

    def test_unpinned_label_file_is_ignored(self):
        labels = row('1', 'kira metni', 'esas_gerekcesi')
        labels['value_assessment'] = {'icerik_turu': {'choice': 'kisa_karar'}}
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, [row('1', 'kira metni', 'esas_gerekcesi')],
                       extra={'verified-topic-pool.jsonl': [labels]})
            out = run_pool(directory, 'stats')
        self.assertEqual(out.returncode, 0, stderr_of(out))
        self.assertEqual(parsed(out)['kinds'], {'esas_gerekcesi': 1})
        self.assertEqual(list(parsed(out)['pool_files']), [MAIN])

    def test_stats_counts_kinds_and_unknown(self):
        unlabeled = row('3', 'kira', 'kisa_karar')
        del unlabeled['value_assessment']
        null_kind = row('4', 'kira', 'kisa_karar', value_assessment={'icerik_turu': None})
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, [row('1', 'kira', 'esas_gerekcesi'),
                                   row('2', 'kira', 'esas_gerekcesi'), unlabeled, null_kind])
            out = run_pool(directory, 'stats')
        self.assertEqual(out.returncode, 0, stderr_of(out))
        result = parsed(out)
        self.assertEqual(result['kinds'], {'esas_gerekcesi': 2, 'unknown': 2})
        self.assertEqual(result['collections'], {MAIN: 4})
        self.assertIsNone(kind_of({'value_assessment': {'icerik_turu': None}}))
        self.assertIsNone(kind_of({'value_assessment': None}))

    def test_filters_by_court_type_and_kind(self):
        bam = row('b', 'kira', 'esas_gerekcesi', court_type='bam',
                  court='Ankara Bölge Adliye Mahkemesi 6. Hukuk Dairesi')
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, [row('1', 'kira', 'esas_gerekcesi'),
                                   row('2', 'kira', 'kisa_karar')], [bam])
            by_court = run_pool(directory, 'search', 'kira', '--court-type', 'bam')
            by_kind = run_pool(directory, 'search', 'kira', '--kind', 'kisa_karar')
        self.assertEqual([r['document_id'] for r in parsed(by_court)['results']], ['b'])
        self.assertEqual([r['document_id'] for r in parsed(by_kind)['results']], ['2'])

    def test_duplicate_ids_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, [row('1', 'a', 'kisa_karar'), row('1', 'b', 'kisa_karar')])
            same_file = run_pool(directory, 'stats')
        self.assertEqual(same_file.returncode, 1)
        self.assertIn('Duplicate document_id: 1', stderr_of(same_file))
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, [row('1', 'a', 'kisa_karar')], [row('1', 'b', 'kisa_karar')])
            across = run_pool(directory, 'stats')
        self.assertEqual(across.returncode, 1)
        self.assertIn('Duplicate document_id across pools', stderr_of(across))

    def test_malformed_records_report_file_and_line_without_traceback(self):
        good = json.dumps(row('1', 'kira', 'esas_gerekcesi'), ensure_ascii=False)
        text_int = row('2', 'x', 'kisa_karar')
        text_int['text'] = 123
        cases = {
            'bad json': '{bad json',
            'not object': '[1, 2]',
            'text int': json.dumps(text_int),
            'missing hash': json.dumps({'document_id': '2', 'text': 'x', 'court': '3. Hukuk Dairesi'}),
            'assessment str': json.dumps(row('2', 'x', 'kisa_karar', value_assessment='esas')),
            'date format': json.dumps(row('2', 'x', 'kisa_karar', karar_tarihi='01.01.2025')),
        }
        for label, second in cases.items():
            with self.subTest(label), tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
                (Path(directory) / MAIN).write_text(good + '\n' + second + '\n', encoding='utf-8')
                proc = run_pool(directory, 'stats')
                stderr = stderr_of(proc)
                self.assertEqual(proc.returncode, 1, stderr)
                self.assertTrue(stderr.startswith('HATA (veri bütünlüğü):'), stderr)
                self.assertIn(f'{MAIN}:2', stderr)
                self.assertNotIn('Traceback', stderr)

    def test_text_hash_mismatch_is_data_error(self):
        broken = row('1', 'kira', 'esas_gerekcesi')
        broken['text'] = 'kira değişti'
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, [broken])
            proc = run_pool(directory, 'search', 'kira')
        self.assertEqual(proc.returncode, 1)
        self.assertIn('Text hash mismatch', stderr_of(proc))
        self.assertEqual(proc.stdout, b'')

    def test_exit_codes_distinguish_usage_not_found_and_data_errors(self):
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, [row('1', 'kira bedeli', 'esas_gerekcesi')])
            unknown = run_pool(directory, 'get', '999')
            self.assertEqual(unknown.returncode, 3)
            self.assertEqual(unknown.stdout, b'')
            self.assertIn('HATA: Karar bulunamadı: 999', stderr_of(unknown))
            absent = run_pool(directory, 'quote', '1', 'bulunmayan alıntı')
            self.assertEqual(absent.returncode, 3)
            self.assertIs(parsed(absent)['exact_match'], False)
            self.assertEqual(parsed(absent)['occurrence_count'], 0)
            for args in (('search', 'kira', '--limit', '0'), ('search', 'kira', '--limit', '2001'),
                         ('search', 'kira', '--limit', 'x'), ('search', ' '), ('quote', '1', ' ')):
                with self.subTest(args):
                    usage = run_pool(directory, *args)
                    self.assertEqual(usage.returncode, 2, stderr_of(usage))
                    self.assertEqual(usage.stdout, b'')
        # Girdi hataları havuz okunmadan bildirilir: kök klasör yokken de kullanım hatası 2'dir.
        missing_root = Path(tempfile.gettempdir()) / 'kira-pool-yok-0d1c'
        self.assertEqual(run_pool(missing_root, 'search', 'kira', '--limit', '0').returncode, 2)
        self.assertEqual(run_pool(missing_root, 'stats').returncode, 1)

    def test_help_documents_exit_codes(self):
        proc = run_pool(None, '--help')
        self.assertEqual(proc.returncode, 0)
        help_text = proc.stdout.decode('utf-8')
        self.assertIn('Çıkış kodları', help_text)
        self.assertIn('quote KARAR_KIMLIGI -- "-alıntı"', help_text)

    def test_quote_offsets_dash_and_nfc_input(self):
        text = 'aaa - davacı çekişmeli şerh'
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, [row('1', text, 'esas_gerekcesi')])
            overlap = run_pool(directory, 'quote', '1', 'aa')
            dash = run_pool(directory, 'quote', '1', '--', '- davacı')
            nfd = run_pool(directory, 'quote', '1', unicodedata.normalize('NFD', 'çekişmeli şerh'))
        self.assertEqual(overlap.returncode, 0, stderr_of(overlap))
        self.assertEqual([o['start'] for o in parsed(overlap)['occurrences']], [0, 1])
        self.assertIs(parsed(overlap)['input_normalized'], False)
        self.assertIn('warning', parsed(overlap))
        self.assertEqual(dash.returncode, 0, stderr_of(dash))
        self.assertEqual(parsed(dash)['occurrences'][0]['start'], 4)
        self.assertEqual(nfd.returncode, 0, stderr_of(nfd))
        result = parsed(nfd)
        self.assertIs(result['exact_match'], True)
        self.assertIs(result['input_normalized'], True)
        self.assertEqual(result['quotation'], 'çekişmeli şerh')
        start = result['occurrences'][0]['start']
        self.assertEqual(text[start:result['occurrences'][0]['end']], 'çekişmeli şerh')

    def test_quote_caps_stored_occurrences(self):
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, [row('1', 'ab ' * 100, 'esas_gerekcesi')])
            proc = run_pool(directory, 'quote', '1', 'a')
        result = parsed(proc)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(result['occurrence_count'], 100)
        self.assertEqual(len(result['occurrences']), QUOTE_MAX_OCCURRENCES)
        self.assertIs(result['occurrences_truncated'], True)
        self.assertIn('warning', result)
        long_quote = 'ab ab ab ab ab ab ab ab'
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, [row('1', long_quote, 'esas_gerekcesi')])
            full = parsed(run_pool(directory, 'quote', '1', long_quote))
        self.assertNotIn('warning', full)
        self.assertIs(full['occurrences_truncated'], False)

    def test_normalize_unifies_case_accents_quotes_and_spaces(self):
        self.assertEqual(normalize('KİRA IŞIK ığüşöç'), 'kira isik igusoc')
        self.assertEqual(normalize('TBK’nın'), normalize("TBK'nın"))
        self.assertEqual(normalize('eski  kiracı'), normalize('eski kiracı'))
        self.assertEqual(normalize('eski kiracı'), 'eski kiraci')
        self.assertEqual(normalize('Kanun´un'), normalize("Kanun'un"))
        self.assertEqual(normalize('“emsal”'), normalize('"emsal"'))
        self.assertEqual(normalize('2010–2015'), normalize('2010-2015'))
        self.assertEqual(normalize('IŞIK'), normalize('ışık'))
        self.assertEqual(normalize('İSTANBUL'), 'istanbul')
        self.assertEqual(normalize('kira­cı'), 'kiraci')

    def test_search_normalizes_query_and_text(self):
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, [row('1', 'IŞIK ve TBK’nın   344/3 hükmü', 'esas_gerekcesi')])
            for query in (['ışık'], ["TBK'nın"], ['tbk’nın', '344']):
                with self.subTest(query):
                    proc = run_pool(directory, 'search', *query)
                    self.assertEqual(parsed(proc)['total_matches'], 1, stderr_of(proc))

    def test_term_matching_starts_at_word_and_bounds_numbers(self):
        rows = [row('1', 'Yargıtay 2017/13443 e. sayılı dosya', 'esas_gerekcesi'),
                row('2', 'TBK 344/3 uyarınca kira tespiti', 'esas_gerekcesi'),
                row('3', 'hususun tartışılması gerekir', 'esas_gerekcesi'),
                row('4', 'kira artışı TÜFE oranında', 'esas_gerekcesi')]
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, rows)

            def ids(*args):
                proc = run_pool(directory, 'search', *args)
                self.assertEqual(proc.returncode, 0, stderr_of(proc))
                return sorted(r['document_id'] for r in parsed(proc)['results'])

            self.assertEqual(ids('344'), ['2'])
            self.assertEqual(ids('artış'), ['4'])
            self.assertEqual(ids('ÜFE'), [])
            self.assertEqual(ids('kira'), ['2', '4'])
            self.assertEqual(ids('344', '--substring'), ['1', '2'])
            self.assertEqual(ids('artış', '--substring'), ['3', '4'])
        self.assertTrue(term_pattern('344').search(normalize('tbk/344')))
        self.assertTrue(term_pattern('344').search(normalize('TBK 344/3')))
        self.assertIsNone(term_pattern('344').search(normalize('3445 ve 2017/13443 e.')))
        self.assertTrue(term_pattern('kira').search(normalize('kiracının')))
        self.assertIsNone(term_pattern('kira').search(normalize('ekiran')))

    def test_search_snippet_is_centered_on_late_match(self):
        text = ('kira ' * 360) + 'bilirkişi' + ('x' * 191)  # terim 1.800. karakterde, paragraf 2.000 karakter
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, [row('9', text, 'esas_gerekcesi')])
            out = run_pool(directory, 'search', 'bilirkişi')
        snippet = parsed(out)['results'][0]['snippet']
        self.assertIn('bilirkişi', snippet)
        self.assertLessEqual(len(snippet), 1402)
        self.assertTrue(snippet.startswith('…'))

    def test_scope_uncertain_and_out_of_scope_rank_last(self):
        def scoped(document_id, haric):
            return row(document_id, 'kira depozito', 'esas_gerekcesi', review_level='not_reviewed',
                       rescan_assessment={'korpus_karari': {'probabilities': {'haric': haric}}})
        caution_text = 'kira depozito uçak'
        out_of_scope = row('504158200', caution_text, 'esas_gerekcesi')
        caution = enrich(dict(out_of_scope, text_sha256='ee67ea4dd909a2a898a1316dc5c02a2dcc980fd3401690a67291aba02c188f79'))
        self.assertIs(caution['out_of_scope'], True)
        self.assertTrue(caution['research_notes']['cautions'])
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, [scoped('1', 0.4), scoped('2', 0.1),
                                   row('3', 'kira depozito', 'usul_gerekcesi')])
            proc = run_pool(directory, 'search', 'depozito')
        results = parsed(proc)['results']
        self.assertEqual([r['document_id'] for r in results], ['2', '1', '3'])
        self.assertIs(results[1]['scope_uncertain'], True)
        self.assertEqual(results[1]['scope_haric_probability'], 0.4)
        self.assertIs(results[0]['scope_uncertain'], False)
        self.assertIs(results[0]['out_of_scope'], False)

    def test_closing_date_conflict_is_flagged_without_false_positives(self):
        diff = enrich(row('9', 'ONANMASINA, 28.05.2018 tarihinde oybirliğiyle karar verildi.', 'kisa_karar'))
        self.assertEqual(text_decision_date(diff), '2018-05-28')
        self.assertIn('28.05.2018', metadata(diff)['date_warning'])
        same = enrich(row('10', 'BOZULMASINA, 28.05. 2019 gününde oybirliğiyle karar verildi.', 'kisa_karar'))
        self.assertNotIn('date_warning', metadata(same))
        hidden = enrich(row('11', '03.08.2010 tarihinde dava açılmış. ONANMASINA, ....05.2019 günü oybirliğiyle karar verildi.', 'kisa_karar'))
        self.assertIsNone(text_decision_date(hidden))
        self.assertNotIn('date_warning', metadata(hidden))

    def test_metadata_includes_provenance_fields(self):
        meta = metadata(enrich(dict(row('1', 'm', 'kisa_karar', raw_sha256='abc'), pool_file=MAIN)))
        self.assertEqual(meta['raw_sha256'], 'abc')
        self.assertEqual(meta['pool_file'], MAIN)
        for key in ('needs_scope_review', 'scope_uncertain', 'scope_haric_probability', 'out_of_scope'):
            self.assertIn(key, meta)

    def test_turkish_stderr_survives_legacy_console_encoding(self):
        env = {**os.environ, 'PYTHONIOENCODING': 'cp1254'}
        env.pop('PYTHONUTF8', None)
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            write_root(directory, [row('1', 'kira', 'esas_gerekcesi')])
            proc = run_pool(directory, 'get', 'kısa-şğ', env=env)
            found = run_pool(directory, 'search', 'kira', env={**env, 'PYTHONIOENCODING': 'cp1252'})
        self.assertEqual(proc.returncode, 3)
        self.assertIn('kısa-şğ', proc.stderr.decode('utf-8'))
        self.assertEqual(found.returncode, 0, stderr_of(found))
        self.assertIn('Yargıtay', parsed(found)['results'][0]['kunye'])

    @unittest.skipIf(sys.platform == 'win32', 'Windows kapalı boruyu EPIPE yerine EINVAL ile bildirir')
    def test_closed_pipe_is_not_reported_as_corpus_error(self):
        proc = subprocess.Popen([sys.executable, str(SCRIPT), 'search', 'kira', '--limit', '200'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.stdout.read(100)
        proc.stdout.close()
        stderr = proc.stderr.read().decode('utf-8', errors='backslashreplace')
        proc.stderr.close()
        proc.wait(timeout=120)
        self.assertNotIn('HATA', stderr)
        self.assertNotIn('Traceback', stderr)


if __name__ == '__main__':
    unittest.main()
