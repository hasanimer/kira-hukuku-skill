import json
from datetime import date, timedelta
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from deadlines import RULES, add_months, calculate, parse_date

TIMEOUT = 120


class DeadlineTests(unittest.TestCase):
    def dates(self, rule, value, **kwargs):
        return calculate(rule, date.fromisoformat(value), **kwargs)['raw_dates']

    def test_month_is_not_thirty_days(self):
        self.assertEqual(self.dates('takvim', '2026-01-31', count=1, unit='ay')['ham_bitis'], '2026-02-28')
        self.assertEqual(self.dates('takvim', '2026-01-31', count=30, unit='gun')['ham_bitis'], '2026-03-02')

    def test_parse_date_formats(self):
        for value in ('2026-09-01', '01.09.2026', '01/09/2026', ' 01.09.2026 '):
            self.assertEqual(parse_date(value), date(2026, 9, 1))
        for value in ('', '20260901', '2026-W36-2', '31.02.2026'):
            with self.assertRaises(ValueError):
                parse_date(value)

    def test_leap_day_and_direct_month_arithmetic(self):
        self.assertEqual(add_months(date(2024, 2, 29), 12), date(2025, 2, 28))
        self.assertEqual(add_months(date(2024, 1, 31), 1), date(2024, 2, 29))
        self.assertEqual(add_months(date(2026, 1, 31), 2), date(2026, 3, 31))
        self.assertEqual(add_months(date(2026, 3, 31), -1), date(2026, 2, 28))

    def test_notice_day_excluded_once(self):
        self.assertEqual(self.dates('tbk315', '2026-09-01')['otuzuncu_gun'], '2026-10-01')
        self.assertEqual(self.dates('takvim', '2026-09-01', count=2, unit='hafta')['ham_bitis'], '2026-09-15')

    def test_backward_threshold_not_rolled_forward(self):
        self.assertEqual(self.dates('tbk345', '2026-09-01')['otuz_gun_once_esigi'], '2026-08-02')

    def test_new_owner_waiting_period_separate_from_notice(self):
        self.assertEqual(self.dates('tbk351', '2026-01-31'), {
            'bir_aylik_bildirim_ham_sonu': '2026-02-28',
            'alti_ayin_ham_dolum_tarihi': '2026-07-31',
            'temkinli_en_erken_arabuluculuk_ve_dava_gunu': '2026-08-01'})
        result = calculate('tbk351', date(2026, 1, 31))
        self.assertIn('arabuluculuk', ' '.join(result['pending_checks']))
        self.assertIn('tapu', result['meaning'])

    def test_need_eviction_month_window(self):
        self.assertEqual(self.dates('tbk350', '2026-01-31'), {'bir_aylik_dava_ham_sonu': '2026-02-28'})
        result = calculate('tbk350', date(2026, 1, 31))
        self.assertIn('2025/1495', ' '.join(result['pending_checks']))
        # Girdi yalnız ilk süre sonu değildir; TBK 347/1 ile uzamış sözleşmede içinde bulunulan uzama yılının bitimidir.
        self.assertIn('uzama yılı', result['meaning'])
        self.assertIn('TBK 347/1', result['meaning'])
        # TBK 353: "en geç" sürede ulaşan bildirim yeter; daha önce yapılan bildirim dışlanmaz.
        notice = [c for c in result['pending_checks'] if 'TBK 353' in c]
        self.assertEqual(len(notice), 1)
        self.assertIn('En geç dava açma süresinin son gününe kadar kiracıya ulaşmış', notice[0])
        self.assertIn('kira süresi içinde de yapılabilen', notice[0])

    def test_undertaking_month_and_five_year_boundary(self):
        self.assertEqual(self.dates('tbk352', '2026-01-31')['bir_aylik_basvuru_ham_sonu'], '2026-02-28')
        self.assertEqual(self.dates('tbk344', '2020-09-01')['bes_yil_sonraki_yildonumu'], '2025-09-01')

    def test_bam_ten_year_example(self):
        self.assertEqual(self.dates('tbk347', '2010-11-01'), {
            'on_yillik_uzama_ham_sonu': '2020-11-01',
            'izleyen_ilk_uzama_yili_ham_sonu': '2021-11-01',
            'uc_ay_once_bildirim_esigi': '2021-08-01',
            'uc_ay_once_temkinli_esik': '2021-07-31'})
        # Ay sonu: 01.03 yıldönümünde temkinli eşik 28/29 Şubat'tan geri sayılır.
        self.assertEqual(self.dates('tbk347', '2016-03-01')['uc_ay_once_temkinli_esik'], '2026-11-28')
        self.assertEqual(self.dates('tbk347', '2016-03-01')['uc_ay_once_bildirim_esigi'], '2026-12-01')

    def test_uets_fifth_day_remains_sunday(self):
        self.assertEqual(self.dates('uets', '2026-09-01')['teblig_edilmis_sayilma_gunu'], '2026-09-06')
        result = calculate('uets', date(2026, 9, 1))
        self.assertEqual(result['basis'], '7201 sayılı Kanun 7/a/4')
        self.assertIn('mevzuat.gov.tr', result['source_url'])

    def test_service_date_and_uets_guidance(self):
        self.assertIn('tebliğ', calculate('tbk315', date(2026, 9, 1))['meaning'])
        for rule in ('tbk345', 'tbk347'):
            self.assertIn('UETS', ' '.join(calculate(rule, date(2026, 9, 1))['pending_checks']))

    def test_backward_takvim(self):
        self.assertEqual(self.dates('takvim', '2026-09-01', count=15, unit='gun', backward=True)['ham_geri_esik'], '2026-08-17')
        self.assertEqual(self.dates('takvim', '2026-12-31', count=3, unit='ay', backward=True)['ham_geri_esik'], '2026-09-30')
        self.assertEqual(self.dates('takvim', '2026-09-01', count=30, unit='gun', backward=True)['ham_geri_esik'],
                         self.dates('tbk345', '2026-09-01')['otuz_gun_once_esigi'])
        self.assertEqual(self.dates('takvim', '2026-09-01', count=1, unit='yil', backward=True), {'ham_geri_esik': '2025-09-01'})
        with self.assertRaises(ValueError):
            calculate('uets', date(2026, 1, 1), backward=True)

    def test_tbk316_mirrors_tbk315_days_but_not_its_meaning(self):
        self.assertEqual(self.dates('tbk316', '2026-09-01'), {'otuzuncu_gun': '2026-10-01'})
        # Gün hesabıdır: ay sonunda ay hesabına kırpılmaz; artık yılda şubat 29 gündür.
        self.assertEqual(self.dates('tbk316', '2026-01-31')['otuzuncu_gun'], '2026-03-02')
        self.assertEqual(self.dates('tbk316', '2026-02-01')['otuzuncu_gun'], '2026-03-03')
        self.assertEqual(self.dates('tbk316', '2028-02-01')['otuzuncu_gun'], '2028-03-02')
        for value in ('2026-01-31', '2028-02-29', '2026-12-15'):
            self.assertEqual(self.dates('tbk316', value), self.dates('tbk315', value))
        result = calculate('tbk316', date(2026, 9, 1))
        self.assertIn('TBK 316/2', result['basis'])
        self.assertIn('konut ve çatılı işyeri', result['basis'])
        for phrase in ('tebliğ', 'keşide', 'aykırılığın başladığı', 'TBK 92/1', 'uets',
                       'fesih, arabuluculuk, dava veya tahliye tarihi değildir'):
            self.assertIn(phrase, result['meaning'])
        self.assertNotEqual(result['meaning'], calculate('tbk315', date(2026, 9, 1))['meaning'])
        checks = ' '.join(result['pending_checks'])
        for phrase in ('316/3', 'tbk315', 'iik269', 'TBK 316 aykırılığına İİK 269', 'TBK 93',
                       'HUAK 18/B', 'UETS', 'TBK 349/3', '+1 gün'):
            self.assertIn(phrase, checks)
        tbk315_checks = ' '.join(calculate('tbk315', date(2026, 9, 1))['pending_checks'])
        self.assertIn('tbk316', tbk315_checks)
        self.assertIn('iik269', tbk315_checks)

    def test_iik269_payment_order_dates(self):
        self.assertEqual(self.dates('iik269', '2026-09-01'), {
            'itiraz_suresi_ham_sonu': '2026-09-08',
            'odeme_suresi_ham_sonu': '2026-10-01',
            'en_erken_tahliye_talebi_ham_gunu': '2026-10-02',
            'tahliye_talebi_alti_ay_ham_sonu': '2027-04-01'})
        # Ay sonu: O = 31.08.2026; altı ay 28.02.2027'ye kırpılır.
        self.assertEqual(self.dates('iik269', '2026-08-01'), {
            'itiraz_suresi_ham_sonu': '2026-08-08',
            'odeme_suresi_ham_sonu': '2026-08-31',
            'en_erken_tahliye_talebi_ham_gunu': '2026-09-01',
            'tahliye_talebi_alti_ay_ham_sonu': '2027-02-28'})
        # Artık yıl: O = 31.08.2027; altı ay 29.02.2028.
        self.assertEqual(self.dates('iik269', '2027-08-01')['tahliye_talebi_alti_ay_ham_sonu'], '2028-02-29')
        # Altı ay ödeme süresinin bitiminden (O) tek adımda sayılır; tebliğden altı ay + 30 gün farklı çıkar.
        start = date(2026, 8, 1)
        self.assertEqual(add_months(start, 6) + timedelta(days=30), date(2027, 3, 3))
        self.assertEqual(self.dates('iik269', '2026-08-01')['tahliye_talebi_alti_ay_ham_sonu'],
                         add_months(start + timedelta(days=30), 6).isoformat())
        # Ödeme süresinin sonu tbk315/takvim 30 gün ile aynı ham günü verir.
        self.assertEqual(self.dates('iik269', '2026-01-31')['odeme_suresi_ham_sonu'],
                         self.dates('takvim', '2026-01-31', count=30, unit='gun')['ham_bitis'])
        result = calculate('iik269', date(2026, 9, 1))
        self.assertIn('MevzuatNo=2004', result['source_url'])
        self.assertIn('resmî metinden doğrula', result['basis'])
        for phrase in ('13 örnek', 'tebliğ', 'takip talebi', 'noter ihtarnamesinin tebliği', 'konut ve çatılı işyeri',
                       "Altı ay O'dan sayılır", 'Yedi günün geçmesi ödeme süresini kısaltmaz', 'uets'):
            self.assertIn(phrase, result['meaning'])
        checks = ' '.join(result['pending_checks'])
        for phrase in ('TBK 362/2', 'İİK 19', 'HGK 2017/2340 E., 2021/261 K.', '2025/7021 E., 2025/5902 K.',
                       'karşıoy', 'resmî metinden doğrula', 'HUAK 18/B', 'itirazın kaldırılması', 'UETS', 'TBK 349/3'):
            self.assertIn(phrase, checks)

    def test_undertaking_rule_documents_iik272_without_new_rule(self):
        self.assertNotIn('iik272', RULES)
        result = calculate('tbk352', date(2026, 1, 31))
        self.assertEqual(result['raw_dates'], {'bir_aylik_basvuru_ham_sonu': '2026-02-28'})
        checks = ' '.join(result['pending_checks'])
        for phrase in ('İİK 272', 'ayrı kural yoktur', 'İİK 19', 'TBK 93'):
            self.assertIn(phrase, checks)

    def test_outputs_are_not_final_deadlines(self):
        self.assertTrue({'tbk316', 'iik269'} <= set(RULES))
        for rule in RULES:
            args = {'count': 1, 'unit': 'gun'} if rule == 'takvim' else {}
            result = calculate(rule, date(2026, 1, 1), **args)
            self.assertEqual(result['status'], 'takvim_adayi_hukuki_kontrol_gerekli')
            self.assertTrue(result['pending_checks'])
            self.assertFalse(result['holiday_adjustment_applied'])
            self.assertFalse(result['mediation_adjustment_applied'])

    def test_invalid_options_are_not_silently_ignored(self):
        for kwargs in ({}, {'count': 0, 'unit': 'gun'}, {'count': -1, 'unit': 'ay'}):
            with self.assertRaises(ValueError):
                calculate('takvim', date(2026, 1, 1), **kwargs)
        with self.assertRaises(ValueError):
            calculate('uets', date(2026, 1, 1), count=30)
        for rule, kwargs in (('iik269', {'count': 60, 'unit': 'gun'}), ('tbk316', {'backward': True})):
            with self.assertRaises(ValueError):
                calculate(rule, date(2026, 1, 1), **kwargs)
        with self.assertRaises(ValueError):
            calculate('tbk3522', date(2026, 1, 1))

    def test_cli_portable_and_bad_date_fails_without_output(self):
        command = [sys.executable, str(ROOT / 'scripts/deadlines.py')]
        result = subprocess.run(command + ['tbk345', '2026-09-01'], cwd=ROOT.parent,
                                capture_output=True, encoding='utf-8', timeout=TIMEOUT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('raw_dates', json.loads(result.stdout))
        result = subprocess.run(command + ['tbk352', '2026-02-30'], capture_output=True, timeout=TIMEOUT)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b'')

    def test_cli_accepts_turkish_dates_and_rejects_version_specific_iso(self):
        command = [sys.executable, str(ROOT / 'scripts/deadlines.py')]
        for value in ('01.09.2026', '01/09/2026', '2026-09-01'):
            result = subprocess.run(command + ['tbk315', value], capture_output=True, encoding='utf-8', timeout=TIMEOUT)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['raw_dates']['otuzuncu_gun'], '2026-10-01')
        for value in ('20260901', '2026-W36-2'):
            result = subprocess.run(command + ['tbk315', value], capture_output=True, encoding='utf-8', timeout=TIMEOUT)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, '')
            self.assertIn('Desteklenenler', result.stderr)
        result = subprocess.run(command + ['takvim', '2026-09-01', '--count', '15', '--unit', 'gun', '--geri'],
                                capture_output=True, encoding='utf-8', timeout=TIMEOUT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['raw_dates'], {'ham_geri_esik': '2026-08-17'})
        result = subprocess.run(command + ['tbk345', '2026-09-01', '--geri'], capture_output=True, encoding='utf-8',
                                timeout=TIMEOUT)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '')

    def test_cli_new_eviction_rules(self):
        command = [sys.executable, str(ROOT / 'scripts/deadlines.py')]
        result = subprocess.run(command + ['iik269', '01.09.2026'], capture_output=True, encoding='utf-8',
                                timeout=TIMEOUT, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['raw_dates']['tahliye_talebi_alti_ay_ham_sonu'], '2027-04-01')
        self.assertFalse(output['holiday_adjustment_applied'])
        result = subprocess.run(command + ['tbk316', '2026-09-01'], capture_output=True, encoding='utf-8',
                                timeout=TIMEOUT, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['raw_dates'], {'otuzuncu_gun': '2026-10-01'})
        for extra in (['tbk316', '2026-09-01', '--count', '30', '--unit', 'gun'], ['iik269', '2026-09-01', '--geri'],
                      ['tbk3522', '2026-09-01']):
            result = subprocess.run(command + extra, capture_output=True, encoding='utf-8', timeout=TIMEOUT, check=False)
            self.assertEqual(result.returncode, 2, extra)
            self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()
