"""Tahliye rota kataloğu aracı: sebep çözümü, rehber bağlantısı, takvim, emsal ve doğrulama.

Birim testleri geçici bir kök (en küçük katalog + rehber) ve gerçek karar havuzuyla çalışır;
gerçek katalog (references/tahliye-yollari.json) varsa ayrıca onunla sınanır.
"""
import copy
from datetime import date
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import deadlines  # noqa: E402
import tahliye  # noqa: E402
import validate  # noqa: E402

DATA = ROOT / 'data'
REAL_CATALOG = ROOT / tahliye.CATALOG
REAL_GUIDE = ROOT / tahliye.GUIDE
# Rehberin sebep başlıkları (references/tahliye.md düzey-2 başlıkları).
HEADINGS = {
    'ortak_usul': 'Ortak usul: arabuluculuk, görev, taraf ve tebligat',
    'temerrut': 'Temerrüt (TBK 315) ve ilamsız tahliye takibi',
    'iki_hakli_ihtar': 'Kira yılı içinde iki haklı ihtar (TBK 352/2)',
    'taahhut': 'Tahliye taahhüdü (TBK 352/1)',
    'ihtiyac': 'Gereksinim ve yeniden inşa (TBK 350)',
    'yeni_malik': 'Yeni malik (TBK 351)',
    'on_yillik_uzama': 'On yıllık uzama ve belirsiz süreli kira (TBK 347)',
    'akde_aykirilik': 'Özen ve komşulara saygı borcuna aykırılık (TBK 316)',
    'kiracinin_konutu_ve_diger': 'Kiracının konutu (TBK 352/3) ve diğer sona erme halleri',
    'tahliye_sonrasi': 'Tahliye kararından sonra: icra, tehir ve TBK 355',
}
# Gerçek havuz kayıtları; alıntılar pool.py quote ile birebir doğrulanmıştır.
DECISIONS = [
    {'document_id': '1155987500',
     'kunye': 'Yargıtay 3. HD, E. 2025/1495, K. 2025/3048, T. 26.05.2025',
     'outcome': 'BAM daireleri arasındaki uyuşmazlık giderildi; oybirliği, kesin.',
     'holding': 'TBK 350 davasında dava şartı arabuluculuk başvurusu dava açma hakkı doğduktan '
                'sonra ve dava açma süresi içinde yapılmalıdır.',
     'quote': 'tahliye davası açma hakkının doğumundan sonra',
     'caveat': 'TBK 350 davaları için verilmiştir; 351 ve 352 yollarına otomatik taşınmaz.'},
    {'document_id': 'aa156eaa-5348-4eef-963a-75a3f84b14a7',
     'kunye': 'İstanbul BAM 35. HD, E. 2025/5438, K. 2025/3212, T. 30.12.2025',
     'outcome': 'İlk derecenin usulden ret kararı kaldırıldı; tahliyeye hükmedildi.',
     'holding': '26.05.2025 tarihinden önce açılan davada erken arabuluculuk başvurusu nedeniyle '
                'usulden ret öngörülemez sayıldı.',
     'quote': 'arabuluculuk başvurusunun dava açma süresinden önce yapıldığı gerekçesiyle',
     'caveat': 'Tek BAM dairesi; ölçüt dava tarihidir.'},
]
TBK350 = 'python scripts/deadlines.py tbk350 <donem-sonu>'
WEEKS = 'python scripts/deadlines.py takvim <gorevlendirme-tarihi> --count 3 --unit hafta'
OPEN_COUNT = 'python scripts/deadlines.py takvim <donem-sonu> --count <n> --unit ay --geri'


def deadline(name, rule, command, confidence='medium'):
    return {'name': name, 'start_event': 'Sınama başlangıç olayı', 'duration': '1 ay',
            'formula': 'A(E,1)', 'rule': rule, 'command': command, 'basis': 'TBK 350',
            'confidence': confidence}


def entry(key):
    return {
        'key': key, 'title': f'Sınama sebebi {key}', 'guide_heading': HEADINGS[key],
        'legal_basis': ['TBK 350/1'], 'requester': 'Kiraya veren.',
        'scope': 'Konut ve çatılı işyeri kirası.', 'notice': 'Yazılı bildirim.',
        'preconditions': ['Sınama koşulu.'],
        'deadlines': [
            deadline('Dava süresi', 'tbk350', TBK350),
            deadline('Arabuluculuk süreci', 'takvim', WEEKS),
            deadline('Sözleşmesel ihbar', 'takvim', OPEN_COUNT, 'low'),
            deadline('Dönem çizelgesi', None,
                     'python scripts/hesap.py donemler --baslangic <kira-baslangici>', 'high'),
            deadline('Durma', None, 'yok', 'low'),
        ],
        'routes': [{'route': 'Tahliye davası', 'forum': 'Sulh hukuk mahkemesi',
                    'arabuluculuk': 'dava_sarti',
                    'arabuluculuk_note': 'HUAK 18/B; resmî metinden doğrula.',
                    'procedure': 'Basit yargılama.'}],
        'tenant_defenses': ['Süre itirazı.'], 'pitfalls': ['Erken başvuru.'],
        'decisions': copy.deepcopy(DECISIONS),
        'open_questions': ['Sınama sorusu.'],
    }


def make_catalog():
    return {'schema_version': 1, 'version': '2026-10-14.1', 'checked_on': '2026-10-14',
            'note': 'Sınama kataloğu; hukuki görüş değildir.',
            'grounds': [entry(key) for key in tahliye.GROUNDS]}


def make_guide(headings=None):
    headings = HEADINGS.values() if headings is None else headings
    body = ''.join(f'## {heading}\n\nMetin.\n\n' for heading in headings)
    return ('# Tahliye: sebepler, yollar ve süreler\n\n## Yol seçimi tablosu\n\n' + body
            + '```text\n## Kod bloğundaki başlık sayılmaz\n```\n')


def write_root(directory, catalog=None, guide=None):
    root = Path(directory)
    (root / 'references').mkdir(parents=True, exist_ok=True)
    (root / tahliye.CATALOG).write_text(
        json.dumps(make_catalog() if catalog is None else catalog, ensure_ascii=False, indent=1),
        encoding='utf-8')
    (root / tahliye.GUIDE).write_text(make_guide() if guide is None else guide, encoding='utf-8')
    return root


def run(*args, expected=0, flags=()):
    proc = subprocess.run([sys.executable, *flags, str(ROOT / 'scripts' / 'tahliye.py'), *args],
                          cwd=ROOT, capture_output=True, timeout=120)
    stderr = proc.stderr.decode('utf-8', errors='backslashreplace')
    if proc.returncode != expected:
        raise AssertionError(f'tahliye.py {args}: rc={proc.returncode} {stderr}')
    proc.out = proc.stdout.decode('utf-8')
    proc.err = proc.stderr.decode('utf-8')
    return proc


class FixtureCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix='kira-tahliye-')
        self.root = write_root(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def check(self, mutate=None, guide=None):
        """Kataloğu değiştirip validate raporunu döner (havuz: gerçek data/)."""
        catalog = make_catalog()
        if mutate:
            mutate(catalog)
        write_root(self.root, catalog, guide)
        return tahliye.validate(self.root, pool_dir=DATA)

    def assertRejected(self, report, fragment):
        self.assertFalse(report['ok'], report)
        self.assertTrue(any(fragment in error for error in report['errors']), report['errors'])


class ResolveTests(unittest.TestCase):
    def test_exact_keys_resolve_to_themselves(self):
        for key in tahliye.GROUNDS:
            self.assertEqual(tahliye.resolve(key), key)

    def test_aliases_and_spelling_variants(self):
        cases = {
            'temerrut': ('temerrüt', 'TEMERRÜT', 'temerrut', '315', 'TBK 315', 'odeme', 'ödeme'),
            'iki_hakli_ihtar': ('iki-ihtar', 'iki-hakli-ihtar', 'iki haklı ihtar', '352-2', '352/2'),
            'taahhut': ('taahhüt', 'taahhut', 'taahhutname', '352-1', 'TBK 352/1'),
            'ihtiyac': ('ihtiyaç', 'İHTİYAÇ', 'ihtiyac', 'gereksinim', '350', 'yeniden-insa',
                        'yeniden inşa'),
            'yeni_malik': ('yeni-malik', 'yeni malik', 'Yeni_Malik', '351'),
            'on_yillik_uzama': ('on-yil', '10yil', '10 yıl', '347', 'uzama', 'on yıllık uzama'),
            'akde_aykirilik': ('aykirilik', 'aykırılık', 'ozen', 'özen', '316', 'komsu', 'komşu'),
            'kiracinin_konutu_ve_diger': ('kiracinin-konutu', 'kiracının konutu', '352-3', 'diger',
                                          'diğer'),
            'ortak_usul': ('usul', 'arabuluculuk', 'ortak', 'Ortak usul'),
            'tahliye_sonrasi': ('sonrasi', 'sonrası', 'tehir', '355', 'icra', 'İcra'),
        }
        for key, names in cases.items():
            for name in names:
                with self.subTest(name=name):
                    self.assertEqual(tahliye.resolve(name), key)

    def test_unknown_or_partial_names_do_not_resolve(self):
        for name in ('xyz', '352', 'tahliye', '', '3155', 'temerrut-x'):
            with self.subTest(name=name):
                self.assertIsNone(tahliye.resolve(name))

    def test_resolution_is_limited_to_given_keys(self):
        self.assertIsNone(tahliye.resolve('temerrüt', keys=('ihtiyac',)))
        self.assertEqual(tahliye.resolve('gereksinim', keys=('ihtiyac',)), 'ihtiyac')


class SlugTests(unittest.TestCase):
    def test_slug_matches_validate_heading_slugs(self):
        for heading in [*HEADINGS.values(), 'Yol seçimi tablosu', 'Açık sorular ve sınırlar',
                        'Kiracı savunmaları kontrol listesi', '  Boşluklu   başlık  ']:
            with self.subTest(heading=heading):
                self.assertEqual({tahliye.slug(heading)}, validate.heading_slugs(f'## {heading}\n'))

    def test_document_headings_skip_code_blocks(self):
        titles = [title for _, title in tahliye.document_headings(make_guide())]
        self.assertIn(HEADINGS['ihtiyac'], titles)
        self.assertNotIn('Kod bloğundaki başlık sayılmaz', titles)
        slugs = {tahliye.slug(title) for title in titles}
        self.assertEqual(slugs, validate.heading_slugs(make_guide()))

    def test_real_catalog_headings_link_to_real_guide(self):
        catalog = tahliye.read_catalog(ROOT)
        anchors = validate.heading_slugs(REAL_GUIDE.read_text(encoding='utf-8'))
        for item in catalog['grounds']:
            with self.subTest(key=item['key']):
                heading = item['guide_heading']
                self.assertEqual({tahliye.slug(heading)}, validate.heading_slugs(f'## {heading}\n'))
                self.assertIn(tahliye.slug(heading), anchors)


class CommandTests(unittest.TestCase):
    def test_deadline_call_parses_options(self):
        self.assertEqual(tahliye.deadline_call(['tbk350', '<E>']), ('tbk350', {}))
        self.assertEqual(tahliye.deadline_call(['takvim', '<T>', '--count', '3', '--unit', 'ay', '--geri']),
                         ('takvim', {'count': 3, 'unit': 'ay', 'backward': True}))
        self.assertEqual(tahliye.deadline_call(['takvim', '<T>', '--count', '<n>', '--unit', 'gun'])[1],
                         {'count': '<n>', 'unit': 'gun'})

    def test_malformed_deadline_commands(self):
        for args in (['tbk350'], ['tbk999', '<E>'], ['tbk350', '2026-01-31'], ['tbk350', '<E>', '--geri'],
                     ['takvim', '<T>', '--count', '3'], ['takvim', '<T>', '--count', '0', '--unit', 'gun'],
                     ['takvim', '<T>', '--count', '3', '--unit', 'saat'],
                     ['takvim', '<T>', '--count', '3', '--count', '4', '--unit', 'gun'],
                     ['takvim', '<T>', '--count', '3', '--unit', 'gun', '--foo']):
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    tahliye.deadline_call(args)

    def test_command_problems(self):
        self.assertEqual(tahliye.command_problems('yok', None), [])
        self.assertEqual(tahliye.command_problems(TBK350, 'tbk350'), [])
        self.assertEqual(tahliye.command_problems('python scripts/hesap.py donemler --baslangic <S>', None), [])
        for command, rule in (('yok', 'tbk350'), ('python3 scripts/deadlines.py tbk350 <E>', 'tbk350'),
                              ('python scripts/olmayan.py <E>', None), (TBK350, None), (TBK350, 'tbk351'),
                              ('python scripts/hesap.py donemler --baslangic <S>', 'tbk350'),
                              (TBK350 + ' ; python scripts/deadlines.py uets <U>', 'tbk350'),
                              ('python scripts/../scripts/deadlines.py tbk350 <E>', 'tbk350')):
            with self.subTest(command=command, rule=rule):
                self.assertTrue(tahliye.command_problems(command, rule))


class ScheduleTests(unittest.TestCase):
    def test_schedule_equals_deadlines_calculate(self):
        start = date(2026, 12, 31)
        plan = tahliye.schedule(entry('ihtiyac'), start)
        self.assertEqual([item['rule'] for item in plan], ['tbk350', 'takvim', 'takvim'])
        self.assertEqual(plan[0]['sonuc'], deadlines.calculate('tbk350', start))
        self.assertEqual(plan[0]['komut'], 'python scripts/deadlines.py tbk350 2026-12-31')
        self.assertEqual(plan[1]['sonuc'], deadlines.calculate('takvim', start, count=3, unit='hafta'))
        self.assertEqual(plan[1]['guven'], 'medium')
        # Süre miktarı yer tutucuysa hesap uydurulmaz; komut ayrıca çalıştırılmak üzere verilir.
        self.assertIsNone(plan[2]['sonuc'])
        self.assertIn('<n>', plan[2]['atlandi'])
        self.assertEqual(plan[2]['komut'],
                         'python scripts/deadlines.py takvim 2026-12-31 --count <n> --unit ay --geri')


class FixtureValidateTests(FixtureCase):
    def test_fixture_catalog_is_valid(self):
        report = tahliye.validate(self.root, pool_dir=DATA)
        n = len(tahliye.GROUNDS)
        self.assertEqual(report, {'ok': True, 'grounds': n, 'decisions': 2 * n, 'deadlines': 5 * n})

    def test_duplicate_key_fails(self):
        def mutate(catalog):
            catalog['grounds'][1]['key'] = 'ortak_usul'
        self.assertRejected(self.check(mutate), 'Yinelenen sebep anahtarı: ortak_usul')

    def test_duplicate_json_field_fails(self):
        text = json.dumps(make_catalog(), ensure_ascii=False)
        twice = text.replace('{"schema_version": 1,', '{"schema_version": 1, "schema_version": 1,', 1)
        (self.root / tahliye.CATALOG).write_text(twice, encoding='utf-8')
        self.assertRejected(tahliye.validate(self.root, pool_dir=DATA), 'Yinelenen JSON alanı')

    def test_missing_unknown_and_extra_fields_fail(self):
        def mutate(catalog):
            catalog['grounds'].pop()
            catalog['grounds'][0]['key'] = 'bilinmeyen'
            catalog['grounds'][1]['fazla'] = 'x'
            del catalog['grounds'][2]['routes'][0]['procedure']
        report = self.check(mutate)
        self.assertRejected(report, 'Eksik sebep: ortak_usul, tahliye_sonrasi')
        self.assertRejected(report, 'Bilinmeyen sebep anahtarı: bilinmeyen')
        self.assertRejected(report, "fazla: ['fazla']")
        self.assertRejected(report, "eksik: ['procedure']")

    def test_bad_rule_fails(self):
        def mutate(catalog):
            catalog['grounds'][0]['deadlines'][0]['rule'] = 'tbk999'
        self.assertRejected(self.check(mutate), 'deadlines[0].rule')

    def test_rule_must_match_command(self):
        def mutate(catalog):
            catalog['grounds'][0]['deadlines'][1]['rule'] = None
            catalog['grounds'][1]['deadlines'][0]['command'] = 'python scripts/olmayan.py <E>'
        report = self.check(mutate)
        self.assertRejected(report, "rule alanı 'takvim' olmalı")
        self.assertRejected(report, 'betik yok: scripts/olmayan.py')

    def test_bad_enums_fail(self):
        def mutate(catalog):
            catalog['grounds'][0]['deadlines'][0]['confidence'] = 'yuksek'
            catalog['grounds'][0]['routes'][0]['arabuluculuk'] = 'zorunlu'
            catalog['schema_version'] = 2
        report = self.check(mutate)
        self.assertRejected(report, 'confidence')
        self.assertRejected(report, 'arabuluculuk: dava_sarti/istisna/tartismali/uygulanmaz')
        self.assertRejected(report, 'schema_version')

    def test_empty_lists_and_too_many_decisions_fail(self):
        def mutate(catalog):
            catalog['grounds'][0]['pitfalls'] = []
            catalog['grounds'][1]['decisions'] = copy.deepcopy(DECISIONS) * 5
        report = self.check(mutate)
        self.assertRejected(report, 'pitfalls: en az 1 öğeli liste')
        self.assertRejected(report, 'decisions: en çok 8 karar')
        self.assertRejected(report, 'aynı karar iki kez')

    def test_missing_heading_fails(self):
        guide = make_guide([h for k, h in HEADINGS.items() if k != 'yeni_malik'])
        self.assertRejected(self.check(guide=guide), f'"## {HEADINGS["yeni_malik"]}" satırı yok')
        duplicated = make_guide() + f'### {HEADINGS["taahhut"]}\n'
        self.assertRejected(self.check(guide=duplicated), 'bağlantısı rehberde tekil değil')

    def test_heading_with_dotted_capital_i_fails(self):
        def mutate(catalog):
            catalog['grounds'][0]['guide_heading'] = 'İcra yolu'
        self.assertRejected(self.check(mutate), 'büyük "İ"')

    def test_bad_quote_fails(self):
        def mutate(catalog):
            catalog['grounds'][0]['decisions'][0]['quote'] = 'tahliye davası açma hakkının doğumundan önce'
            catalog['grounds'][1]['decisions'][0]['quote'] = 'kısa'
        report = self.check(mutate)
        self.assertRejected(report, 'ortak_usul.decisions[0].quote: karar metninde birebir bulunamadı')
        self.assertRejected(report, 'temerrut.decisions[0].quote: en az 20 karakter')

    def test_unknown_decision_and_wrong_kunye_fail(self):
        def mutate(catalog):
            catalog['grounds'][0]['decisions'][0]['document_id'] = '0'
            catalog['grounds'][1]['decisions'][0]['kunye'] = 'Yargıtay 3. HD, E. 2025/14950, K. 2025/3048, T. 26.05.2025'
            catalog['grounds'][2]['decisions'][1]['kunye'] = 'Yargıtay 3. HD, E. 2025/5438, K. 2025/3212, T. 30.12.2025'
        report = self.check(mutate)
        self.assertRejected(report, 'karar havuzda yok: 0')
        self.assertRejected(report, 'temerrut.decisions[0].kunye: "E. 2025/1495" içermeli')
        self.assertRejected(report, 'mahkeme "İstanbul BAM 35. HD" ile başlamalı')

    def test_missing_files_are_reported(self):
        (self.root / tahliye.GUIDE).unlink()
        self.assertRejected(tahliye.validate(self.root, pool_dir=DATA), f'{tahliye.GUIDE} bulunamadı')
        self.assertRejected(tahliye.validate(self.root), 'Karar havuzu okunamadı')
        (self.root / tahliye.CATALOG).unlink()
        self.assertEqual(tahliye.validate(self.root, pool_dir=DATA),
                         {'ok': False, 'errors': [f'{tahliye.CATALOG} bulunamadı']})

    def test_load_catalog_rejects_invalid_structure(self):
        def mutate(catalog):
            catalog['grounds'][0]['deadlines'][0]['rule'] = 'tbk999'
        self.check(mutate)
        with self.assertRaisesRegex(ValueError, 'tahliye.py validate'):
            tahliye.load_catalog(self.root)


class FixtureCliTests(FixtureCase):
    def test_list(self):
        listing = json.loads(run('--root', str(self.root), 'list').out)
        self.assertEqual(listing['version'], '2026-10-14.1')
        self.assertEqual([g['key'] for g in listing['grounds']], list(tahliye.GROUNDS))
        first = listing['grounds'][0]
        self.assertEqual(set(first), {'key', 'title', 'legal_basis', 'rehber'})
        self.assertEqual(first['rehber'], 'references/tahliye.md#ortak-usul-arabuluculuk-görev-taraf-ve-tebligat')

    def test_yol_with_date_equals_deadlines(self):
        card = json.loads(run('yol', 'gereksinim', '--root', str(self.root), '--tarih', '31.12.2026').out)
        expected = {**entry('ihtiyac'), 'rehber': 'references/tahliye.md#gereksinim-ve-yeniden-inşa-tbk-350',
                    'katalog_surumu': '2026-10-14.1'}
        self.assertEqual({k: card[k] for k in expected}, expected)
        self.assertEqual(card['tarih'], '2026-12-31')
        self.assertIn('Aynı tarih (2026-12-31)', card['uyari'])
        self.assertIn('meaning', card['uyari'])
        self.assertEqual(card['takvim'], json.loads(json.dumps(tahliye.schedule(entry('ihtiyac'), date(2026, 12, 31)))))
        self.assertEqual(card['takvim'][0]['sonuc'], deadlines.calculate('tbk350', date(2026, 12, 31)))
        plain = json.loads(run('--root', str(self.root), 'yol', 'ihtiyac').out)
        self.assertNotIn('takvim', plain)

    def test_yol_text_rendering(self):
        # Windows konsolunda print satır sonunu \r\n yazar; içerik karşılaştırılır.
        text = run('--root', str(self.root), 'yol', 'temerrüt', '--metin', '--tarih',
                   '2026-12-31').out.replace('\r\n', '\n')
        self.assertTrue(text.startswith('Sınama sebebi temerrut [temerrut]\n'), text[:80])
        for fragment in ('Rehber: references/tahliye.md#temerrüt-tbk-315-ve-ilamsız-tahliye-takibi',
                         'güven: düşük', 'Araç: araç yok', 'Arabuluculuk: dava şartı',
                         'Yargıtay 3. HD, E. 2025/1495, K. 2025/3048, T. 26.05.2025',
                         'Tam metin: python scripts/pool.py get 1155987500',
                         'Ham takvim adayı (girdi 31.12.2026)', 'bir_aylik_dava_ham_sonu 31.01.2027',
                         'Ayrı çağır: python scripts/deadlines.py tbk350 2026-12-31'):
            self.assertIn(fragment, text)

    def test_emsal_shape(self):
        result = json.loads(run('--root', str(self.root), 'emsal', '352/3').out)
        self.assertEqual(result['key'], 'kiracinin_konutu_ve_diger')
        self.assertEqual(len(result['decisions']), len(DECISIONS))
        for got, want in zip(result['decisions'], DECISIONS):
            self.assertEqual(got, {**want, 'komut': f'python scripts/pool.py get {want["document_id"]}'})

    def test_unknown_key_exits_3_and_lists_keys(self):
        proc = run('--root', str(self.root), 'yol', 'xyz', expected=3)
        self.assertEqual(proc.stdout, b'')
        self.assertTrue(proc.err.startswith('HATA: '), proc.err)
        for key in tahliye.GROUNDS:
            self.assertIn(key, proc.err)
        # Bilinmeyen sebep katalog okunmadan bildirilir.
        self.assertTrue(run('--root', str(self.root / 'yok'), 'emsal', 'xyz', expected=3).err.startswith('HATA: '))

    def test_usage_and_data_errors(self):
        proc = run('--root', str(self.root), 'yol', 'ihtiyac', '--tarih', '31.02.2026', expected=2)
        self.assertIn('HATA: ', proc.err)
        run('--root', str(self.root), 'yol', expected=2)
        missing = run('--root', str(self.root / 'yok'), 'list', expected=1)
        self.assertTrue(missing.err.startswith('HATA: Dosya bulunamadı'), missing.err)
        self.assertEqual(missing.stdout, b'')

    def test_validate_cli(self):
        report = json.loads(run('validate', '--root', str(self.root), '--havuz', str(DATA)).out)
        self.assertTrue(report['ok'], report)
        catalog = make_catalog()
        catalog['grounds'][0]['routes'][0]['arabuluculuk'] = 'zorunlu'
        write_root(self.root, catalog)
        report = json.loads(run('--root', str(self.root), 'validate', '--havuz', str(DATA), expected=1).out)
        self.assertFalse(report['ok'])
        self.assertTrue(report['errors'])

    def test_root_flag_accepted_before_and_after_command(self):
        before = run('--root', str(self.root), 'list').out
        after = run('list', '--root', str(self.root)).out
        self.assertEqual(before, after)


class RealCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = tahliye.read_catalog(ROOT)

    def test_real_catalog_validates(self):
        report = tahliye.validate(ROOT)
        self.assertTrue(report['ok'], report.get('errors'))
        self.assertEqual(report['grounds'], len(tahliye.GROUNDS))

    def test_every_ground_resolves_and_has_bounded_decisions(self):
        for item in self.catalog['grounds']:
            with self.subTest(key=item['key']):
                self.assertEqual(tahliye.resolve(item['key']), item['key'])
                self.assertTrue(1 <= len(item['decisions']) <= tahliye.MAX_DECISIONS)

    def test_real_schedule_matches_deadlines(self):
        start = date(2026, 12, 31)
        for item in self.catalog['grounds']:
            for row in tahliye.schedule(item, start):
                with self.subTest(key=item['key'], name=row['name']):
                    if row['sonuc'] is None:
                        self.assertTrue(row['atlandi'])
                        continue
                    tokens = row['komut'].split()
                    self.assertEqual(tokens[:4], ['python', 'scripts/deadlines.py', row['rule'], '2026-12-31'])
                    tokens[3] = '<girdi>'
                    _, options = tahliye.deadline_call(tokens[2:])
                    self.assertEqual(row['sonuc'], deadlines.calculate(row['rule'], start, **options))

    def test_cli_on_real_catalog(self):
        listing = json.loads(run('list').out)
        self.assertEqual([g['key'] for g in listing['grounds']], [g['key'] for g in self.catalog['grounds']])
        card = json.loads(run('yol', 'ihtiyac', '--tarih', '2026-12-31').out)
        self.assertTrue(any(item['sonuc'] for item in card['takvim']))
        emsal = json.loads(run('emsal', 'temerrüt').out)
        self.assertTrue(all(d['komut'] == f'python scripts/pool.py get {d["document_id"]}'
                            for d in emsal['decisions']))


if __name__ == '__main__':
    unittest.main()
