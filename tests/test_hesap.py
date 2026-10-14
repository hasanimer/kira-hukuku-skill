"""Unit tests for scripts/hesap.py."""
from datetime import date, timedelta
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from hesap import (
    parse_date,
    add_years,
    sub_months,
    compute_periods,
    compute_tespit,
    compute_tahliye_10yil
)

TIMEOUT = 120


class HesapTests(unittest.TestCase):
    def _cli(self, *args, isolated=False):
        command = [sys.executable, *(["-I"] if isolated else []), str(ROOT / "scripts/hesap.py"), *args]
        return subprocess.run(command, capture_output=True, encoding="utf-8", timeout=TIMEOUT)

    def test_parse_date(self):
        self.assertEqual(parse_date("01.07.2020"), date(2020, 7, 1))
        self.assertEqual(parse_date("2020-07-01"), date(2020, 7, 1))
        self.assertEqual(parse_date("01/07/2020"), date(2020, 7, 1))
        with self.assertRaises(ValueError):
            parse_date("")
        with self.assertRaises(ValueError):
            parse_date("invalid-date")
        with self.assertRaises(ValueError):
            parse_date("32.01.2020")
        # Python sürümüne göre değişen fromisoformat biçimleri kabul edilmez.
        for value in ("20200701", "2020-W27-3"):
            with self.assertRaises(ValueError):
                parse_date(value)

    def test_add_years_and_leap_year(self):
        self.assertEqual(add_years(date(2021, 5, 10), 3), date(2024, 5, 10))
        # 29 Şubat'tan 1 yıl sonrası artık olmayan yılda 28 Şubat olmalı
        self.assertEqual(add_years(date(2020, 2, 29), 1), date(2021, 2, 28))
        # 29 Şubat'tan 4 yıl sonrası (2024 artık yıl) 29 Şubat olmalı
        self.assertEqual(add_years(date(2020, 2, 29), 4), date(2024, 2, 29))

    def test_sub_months(self):
        # 31 Aralık - 3 ay = 30 Eylül
        self.assertEqual(sub_months(date(2025, 12, 31), 3), date(2025, 9, 30))
        # 31 Mayıs - 3 ay = 28 Şubat (2025 artık yıl değil)
        self.assertEqual(sub_months(date(2025, 5, 31), 3), date(2025, 2, 28))
        # Yıl devri: 15 Ocak - 3 ay = 15 Ekim önceki yıl
        self.assertEqual(sub_months(date(2025, 1, 15), 3), date(2024, 10, 15))

    def test_compute_periods_and_hak_nesafet(self):
        start = date(2018, 7, 1)
        periods = compute_periods(start, count=12)
        self.assertEqual(len(periods), 12)

        # 1. Kira Yılı: 01.07.2018 - 30.06.2019
        self.assertEqual(periods[0]["baslangic"], "01.07.2018")
        self.assertEqual(periods[0]["bitis"], "30.06.2019")
        self.assertFalse(periods[0]["hak_nesafet_yili"])

        # 5. Kira Yılı: 01.07.2022 - 30.06.2023 (5 yılın dolumu)
        self.assertEqual(periods[4]["bitis"], "30.06.2023")
        self.assertFalse(periods[4]["hak_nesafet_yili"])
        self.assertFalse(periods[4]["bes_yil_doldu_mu"])
        self.assertFalse(periods[4]["tbk344_3_kosullu_aday"])

        # 6. Kira Yılı (İlk hak ve nesafet): 01.07.2023 - 30.06.2024
        self.assertEqual(periods[5]["baslangic"], "01.07.2023")
        self.assertTrue(periods[5]["hak_nesafet_yili"])
        self.assertTrue(periods[5]["bes_yillik_dongu_adayi"])
        self.assertIn("Hak ve Nesafet", periods[5]["rejim"])

        # 7-10. Kira yılları: önceki 344/3 belirlemesine bağlı koşullu aday
        self.assertFalse(periods[6]["hak_nesafet_yili"])
        self.assertFalse(periods[6]["bes_yillik_dongu_adayi"])
        self.assertTrue(periods[6]["bes_yil_doldu_mu"])
        self.assertTrue(periods[6]["tbk344_3_kosullu_aday"])
        self.assertNotIn("Ara Yıl", periods[6]["rejim"])
        self.assertIn("koşullu", periods[6]["rejim"])
        self.assertIn("2017/4515", periods[6]["rejim"])

        # 11. Kira Yılı (İkinci hak ve nesafet): 01.07.2028 - 30.06.2029
        self.assertEqual(periods[10]["baslangic"], "01.07.2028")
        self.assertTrue(periods[10]["hak_nesafet_yili"])
        self.assertFalse(periods[10]["tbk344_3_kosullu_aday"])
        self.assertTrue(periods[11]["tbk344_3_kosullu_aday"])

    def test_tbk345_with_increase_clause(self):
        start = date(2018, 7, 1)
        target = date(2024, 7, 1)
        action = date(2024, 11, 15)  # Hedef dönem içinde dava
        res = compute_tespit(
            start_date=start,
            has_increase_clause=True,
            notice_date=None,
            action_date=action,
            target_period_start=target
        )
        self.assertTrue(res["sure_analizi"]["artis_sarti_var"])
        self.assertEqual(res["sure_analizi"]["aday_etki_tarihi"], "01.07.2024")
        self.assertIs(res["sure_analizi"]["hedef_donem_tarih_kosulu"], True)
        self.assertIn("TBK 345/3", res["sure_analizi"]["uygulanan_kural"])
        self.assertEqual(res["sure_analizi"]["hedef_doneme_etki_son_dava_adayi"], "30.06.2025")
        self.assertEqual(res["sure_analizi"]["hedef_donem_ham_sonu"], "30.06.2025")
        self.assertNotIn("en_gec_dava_tarihi", res["sure_analizi"])

    def test_tbk345_without_increase_clause_timely_notice(self):
        start = date(2018, 7, 1)
        target = date(2024, 7, 1)
        # 30 gün öncesi son gün: 01.06.2024
        notice = date(2024, 5, 25)  # Süresinde ihtar
        action = date(2024, 9, 10)  # Dönem içinde açılan dava
        res = compute_tespit(
            start_date=start,
            has_increase_clause=False,
            notice_date=notice,
            action_date=action,
            target_period_start=target
        )
        self.assertFalse(res["sure_analizi"]["artis_sarti_var"])
        self.assertEqual(res["sure_analizi"]["en_gec_ihtar_teblig_tarihi"], "01.06.2024")
        self.assertEqual(res["sure_analizi"]["aday_etki_tarihi"], "01.07.2024")
        self.assertIs(res["sure_analizi"]["hedef_donem_tarih_kosulu"], True)
        self.assertIs(res["sure_analizi"]["ihtar_suresinde"], True)
        self.assertEqual(res["sure_analizi"]["hedef_doneme_etki_son_dava_adayi"], "30.06.2025")

    def test_tbk345_without_increase_clause_late_notice(self):
        start = date(2018, 7, 1)
        target = date(2024, 7, 1)
        # 30 gün öncesi son gün: 01.06.2024
        notice = date(2024, 6, 15)  # Geç tebliğ edilen ihtar
        action = date(2024, 9, 10)
        res = compute_tespit(
            start_date=start,
            has_increase_clause=False,
            notice_date=notice,
            action_date=action,
            target_period_start=target
        )
        # Sonraki dönem otomatik ilan edilmez.
        self.assertIsNone(res["sure_analizi"]["kararin_gecerlilik_tarihi"])
        self.assertIsNone(res["sure_analizi"]["aday_etki_tarihi"])
        self.assertIs(res["sure_analizi"]["hedef_donem_tarih_kosulu"], False)
        self.assertIn("sonraki dönem otomatik seçilmez", res["tespitler"][-1])
        self.assertIs(res["sure_analizi"]["ihtar_suresinde"], False)
        self.assertEqual(res["sure_analizi"]["hedef_doneme_etki_son_dava_adayi"], "01.06.2024")

    def test_effect_window_scenarios(self):
        def sa(clause, notice=None):
            return compute_tespit(date(2018, 7, 1), clause, notice, None, date(2024, 7, 1))["sure_analizi"]
        none = sa(False)
        self.assertEqual(none["hedef_doneme_etki_son_dava_adayi"], "01.06.2024")
        self.assertIsNone(none["ihtar_suresinde"])
        self.assertEqual(none["etki_senaryolari"], {
            "artis_sarti_veya_suresinde_yazili_bildirim_varsa": "30.06.2025",
            "artis_sarti_ve_suresinde_bildirim_yoksa": "01.06.2024"})
        self.assertEqual(sa(False, date(2024, 5, 25))["hedef_doneme_etki_son_dava_adayi"], "30.06.2025")
        late = sa(False, date(2024, 6, 15))
        self.assertEqual(late["hedef_doneme_etki_son_dava_adayi"], "01.06.2024")
        self.assertIs(late["ihtar_suresinde"], False)
        self.assertEqual(sa(True)["hedef_doneme_etki_son_dava_adayi"], "30.06.2025")
        notes = " ".join(compute_tespit(date(2018, 7, 1), False, target_period_start=date(2024, 7, 1))["tespitler"])
        self.assertIn("dava en geç 01.06.2024", notes)
        self.assertIn("yine açılabilir", notes)

    def test_tbk345_notice_on_deadline_and_action_after_period(self):
        s, t = date(2018, 7, 1), date(2024, 7, 1)
        self.assertIs(compute_tespit(s, False, date(2024, 6, 1), date(2024, 9, 10), t)["sure_analizi"]["hedef_donem_tarih_kosulu"], True)
        self.assertIs(compute_tespit(s, True, None, date(2025, 7, 1), t)["sure_analizi"]["hedef_donem_tarih_kosulu"], False)

    def test_tbk345_boundaries(self):
        def sa(clause, notice=None, action=None):
            return compute_tespit(date(2018, 7, 1), clause, notice, action, date(2024, 7, 1))["sure_analizi"]
        self.assertEqual(sa(False, date(2024, 6, 1), date(2024, 9, 10))["aday_etki_tarihi"], "01.07.2024")
        self.assertIsNone(sa(False, date(2024, 6, 2), date(2024, 9, 10))["aday_etki_tarihi"])
        self.assertTrue(sa(False, action=date(2024, 6, 1))["hedef_donem_tarih_kosulu"])
        self.assertFalse(sa(False, action=date(2024, 6, 2))["hedef_donem_tarih_kosulu"])
        self.assertTrue(sa(True, action=date(2025, 6, 30))["hedef_donem_tarih_kosulu"])
        self.assertFalse(sa(True, action=date(2025, 7, 1))["hedef_donem_tarih_kosulu"])

    def test_first_lease_year_target_rejected(self):
        with self.assertRaises(ValueError):
            compute_tespit(date(2018, 7, 1), False, target_period_start=date(2018, 7, 1))

    def test_action_from_earlier_period_not_counted(self):
        for clause in (True, False):
            sa = compute_tespit(date(2018, 7, 1), clause, None, date(2019, 1, 1), date(2024, 7, 1))["sure_analizi"]
            self.assertIs(sa["hedef_donem_tarih_kosulu"], False)
            self.assertIsNone(sa["aday_etki_tarihi"])

    def test_notice_from_previous_period_not_reused(self):
        res = compute_tespit(date(2018, 7, 1), False, date(2023, 5, 15), date(2024, 9, 15), date(2024, 7, 1))
        self.assertIs(res["sure_analizi"]["hedef_donem_tarih_kosulu"], False)
        self.assertIsNone(res["sure_analizi"]["aday_etki_tarihi"])
        self.assertIs(res["sure_analizi"]["ihtar_suresinde"], False)
        self.assertTrue(any("hesaba katılmadı" in note for note in res["tespitler"]))
        # Eski ihtar tek başına koşulu bozmaz: 30 gün eşiğinden önce açılan dava yine yeterlidir.
        timely = compute_tespit(date(2018, 7, 1), False, date(2019, 1, 1), date(2024, 5, 1), date(2024, 7, 1))
        self.assertIs(timely["sure_analizi"]["hedef_donem_tarih_kosulu"], True)

    def test_clause_action_in_previous_period_warns(self):
        res = compute_tespit(date(2018, 7, 1), True, None, date(2024, 5, 15), date(2024, 7, 1))
        self.assertEqual(res["sure_analizi"]["aday_etki_tarihi"], "01.07.2024")
        self.assertTrue(any("daha önceki bir dönemden" in note for note in res["tespitler"]))

    def test_transitional_rule_notes(self):
        def n(s, t):
            return " ".join(compute_tespit(s, True, target_period_start=t)["tespitler"])
        self.assertIn("geçici 2", n(date(2018, 7, 1), date(2024, 7, 1)))
        self.assertIn("geçici 1", n(date(2018, 7, 1), date(2023, 7, 1)))
        self.assertIn("6217", n(date(2014, 7, 1), date(2019, 7, 1)))
        self.assertIn("7161", n(date(2014, 7, 1), date(2019, 7, 1)))
        self.assertNotIn("7161", n(date(2013, 7, 1), date(2018, 7, 1)))
        self.assertIn("6217", n(date(2013, 7, 1), date(2018, 7, 1)))
        self.assertIn("818", n(date(2008, 7, 1), date(2011, 7, 1)))
        self.assertIn("6570", n(date(2008, 7, 1), date(2011, 7, 1)))
        self.assertNotIn("6570", n(date(2014, 7, 1), date(2019, 7, 1)))
        clean = n(date(2020, 7, 1), date(2025, 7, 1))
        self.assertNotIn("geçici", clean)
        self.assertNotIn("6217", clean)

    def test_transitional_and_mediation_boundaries(self):
        def n(s, t):
            return " ".join(compute_tespit(s, True, target_period_start=t)["tespitler"])
        # TBK geçici 1: yürürlük günü 11.06.2022 dahil, önceki gün değil
        self.assertIn("geçici 1", n(date(2017, 6, 11), date(2022, 6, 11)))
        self.assertNotIn("geçici", n(date(2017, 6, 10), date(2022, 6, 10)))
        # geçici 1 -> geçici 2 devri: 01.07.2023 / 02.07.2023
        self.assertIn("geçici 1", n(date(2018, 7, 1), date(2023, 7, 1)))
        self.assertIn("geçici 2", n(date(2018, 7, 2), date(2023, 7, 2)))
        self.assertNotIn("geçici 1", n(date(2018, 7, 2), date(2023, 7, 2)))
        # geçici 2 sonu: 01.07.2024 dahil, 02.07.2024 değil
        self.assertIn("geçici 2", n(date(2019, 7, 1), date(2024, 7, 1)))
        self.assertNotIn("geçici", n(date(2019, 7, 2), date(2024, 7, 2)))
        # 6217 s.K. geçici 2 penceresi: 01.07.2012 – 01.07.2020 (sınır günü işaretlenir); öncesi 818/6570/6101 notu
        self.assertIn("6217", n(date(2007, 7, 1), date(2012, 7, 1)))
        self.assertNotIn("6101", n(date(2007, 7, 1), date(2012, 7, 1)))
        self.assertIn("6101", n(date(2007, 6, 30), date(2012, 6, 30)))
        self.assertNotIn("6217", n(date(2007, 6, 30), date(2012, 6, 30)))
        self.assertIn("6217", n(date(2015, 7, 1), date(2020, 7, 1)))
        self.assertNotIn("6217", n(date(2015, 7, 2), date(2020, 7, 2)))

        # HUAK 18/B: 01.09.2023 ve sonrasında açılan davada arabuluculuk dava şartı
        def med(d):
            return compute_tespit(date(2016, 9, 1), True, None, d, date(2023, 9, 1))["sure_analizi"]["arabuluculuk_zorunlu"]
        self.assertIs(med(date(2023, 8, 31)), False)
        self.assertIs(med(date(2023, 9, 1)), True)

    def test_mediation_flag(self):
        with_action = compute_tespit(date(2018, 7, 1), False, None, date(2024, 5, 15), date(2024, 7, 1))
        self.assertIs(with_action["sure_analizi"]["arabuluculuk_zorunlu"], True)
        self.assertTrue(any("HUAK 18/B-1-a" in note and "01.06.2024" in note for note in with_action["tespitler"]))
        notice_route = compute_tespit(date(2018, 7, 1), False, date(2024, 5, 25), date(2024, 9, 10), date(2024, 7, 1))
        mediation = [note for note in notice_route["tespitler"] if "HUAK 18/B-1-a" in note]
        self.assertEqual(len(mediation), 1)
        self.assertIn("hedef dönem sonuna kadar açılmış", mediation[0])
        self.assertNotIn("ihtarsız", mediation[0])
        without = compute_tespit(date(2018, 7, 1), True, target_period_start=date(2024, 7, 1))
        self.assertIsNone(without["sure_analizi"]["arabuluculuk_zorunlu"])
        # Dava tarihi yokken not yola göre sınır verir: artış şartında hedef dönem sonu, ihtarsız yolda 30 gün eşiği.
        clause_note = [note for note in without["tespitler"] if "HUAK 18/B-1-a" in note]
        self.assertEqual(len(clause_note), 1)
        self.assertIn("30.06.2025", clause_note[0])
        self.assertNotIn("01.06.2024", clause_note[0])
        self.assertIn("genel dava son günü değildir", clause_note[0])
        no_clause = compute_tespit(date(2018, 7, 1), False, target_period_start=date(2024, 7, 1))
        bare_note = [note for note in no_clause["tespitler"] if "HUAK 18/B-1-a" in note]
        self.assertEqual(len(bare_note), 1)
        self.assertIn("01.06.2024", bare_note[0])
        self.assertIn("durdurduğu veya karşıladığı varsayılmaz", bare_note[0])
        timely_notice = compute_tespit(date(2018, 7, 1), False, date(2024, 5, 25), None, date(2024, 7, 1))
        notice_note = [note for note in timely_notice["tespitler"] if "HUAK 18/B-1-a" in note]
        self.assertEqual(len(notice_note), 1)
        self.assertIn("TBK 345/2 süresinde yazılı bildirim", notice_note[0])
        self.assertIn("30.06.2025", notice_note[0])
        self.assertNotIn("01.06.2024", notice_note[0])
        before = compute_tespit(date(2016, 7, 1), True, None, date(2022, 9, 1), date(2022, 7, 1))
        self.assertIs(before["sure_analizi"]["arabuluculuk_zorunlu"], False)

    def test_five_year_fields(self):
        res = compute_tespit(date(2020, 9, 1), True, target_period_start=date(2025, 9, 1))
        self.assertEqual(res["bes_yil_dolum_tarihi"], "31.08.2025")
        self.assertEqual(res["besinci_kira_yili_son_gunu"], "31.08.2025")
        self.assertEqual(res["bes_yil_yildonumu"], "01.09.2025")
        self.assertTrue(res["hedef_donem"]["bes_yillik_dongu_adayi"])
        self.assertFalse(res["hedef_donem"]["tbk344_3_kosullu_aday"])
        later = compute_tespit(date(2018, 7, 1), True, target_period_start=date(2024, 7, 1))["hedef_donem"]
        self.assertTrue(later["tbk344_3_kosullu_aday"])

    def test_tbk347_ten_year_extension(self):
        start = date(2015, 1, 1)
        res = compute_tahliye_10yil(start, initial_years=1)
        self.assertEqual(res["ilk_sozlesme_bitis"], "01.01.2016")
        self.assertEqual(res["on_yillik_uzama_baslangic"], "01.01.2016")
        self.assertEqual(res["on_yillik_uzama_bitis"], "01.01.2026")
        self.assertEqual(res["toplam_yil"], 12)
        self.assertEqual(res["ilk_fesih_donem_sonu"], "01.01.2027")
        # İzleyen yıl sınırından üç ay önce bildirim: temkinli eşik ve yıldönümü eşiği ayrı verilir
        self.assertEqual(res["en_gec_ihtar_teblig_tarihi"], "30.09.2026")
        self.assertEqual(res["yildonumu_ihtar_esigi"], "01.10.2026")
        # Otomatik bir aylık dava penceresi üretilmez.
        self.assertIsNone(res["tahliye_dava_acma_araligi"])
        self.assertIn("TBK 347 için otomatik bir aylık dava penceresi veya TBK 353 uzaması üretilmez.", res["tespitler"])
        self.assertTrue(all(y["tahliye_dava_donemi"] is None for y in res["izleyen_uzama_yillari"]))
        self.assertEqual(len(res["izleyen_uzama_yillari"]), 3)
        self.assertEqual(res["ilk_sozlesme_son_kullanim_gunu"], "31.12.2015")
        self.assertEqual(res["on_yillik_uzama_son_kullanim_gunu"], "31.12.2025")
        self.assertEqual(res["ilk_sure_kaynagi"], "sure_yil")
        self.assertFalse(any("varsayıldı" in note for note in res["tespitler"]))

    def test_tbk347_default_term_is_flagged(self):
        res = compute_tahliye_10yil(date(2015, 1, 1))
        self.assertEqual(res["ilk_sure_kaynagi"], "varsayilan_12_ay")
        self.assertEqual(res["ilk_fesih_donem_sonu"], "01.01.2027")
        self.assertIn("varsayıldı", res["tespitler"][0])

    def test_tbk347_multi_year_initial_term(self):
        r = compute_tahliye_10yil(date(2015, 1, 1), 3)
        self.assertEqual((r["ilk_sozlesme_bitis"], r["on_yillik_uzama_bitis"], r["ilk_fesih_donem_sonu"],
                          r["en_gec_ihtar_teblig_tarihi"], r["yildonumu_ihtar_esigi"], r["toplam_yil"]),
                         ("01.01.2018", "01.01.2028", "01.01.2029", "30.09.2028", "01.10.2028", 14))
        f = r["izleyen_uzama_yillari"][0]
        self.assertEqual((f["uzama_yili"], f["toplam_kira_yili"], f["donem_sonu"], f["en_gec_ihtar_tarihi"],
                          f["yildonumu_ihtar_esigi"]),
                         (12, 15, "01.01.2030", "30.09.2029", "01.10.2029"))

    def test_tbk347_month_terms_and_explicit_end(self):
        r = compute_tahliye_10yil(date(2015, 1, 1), initial_months=11)
        self.assertEqual(r["ilk_fesih_donem_sonu"], "01.12.2026")
        self.assertEqual(r["en_gec_ihtar_teblig_tarihi"], "30.08.2026")
        self.assertEqual(r["yildonumu_ihtar_esigi"], "01.09.2026")
        self.assertIsNone(r["toplam_yil"])
        self.assertIsNone(r["izleyen_uzama_yillari"][0]["toplam_kira_yili"])
        self.assertIsNone(r["ilk_sozlesme_suresi_yil"])
        self.assertEqual(r["ilk_sozlesme_suresi_ay"], 11)

        keys = ("ilk_sozlesme_bitis", "on_yillik_uzama_bitis", "ilk_fesih_donem_sonu", "en_gec_ihtar_teblig_tarihi",
                "yildonumu_ihtar_esigi", "izleyen_uzama_yillari", "toplam_yil")
        explicit = compute_tahliye_10yil(date(2015, 1, 1), first_end=date(2016, 1, 1))
        yearly = compute_tahliye_10yil(date(2015, 1, 1), initial_years=1)
        self.assertEqual({k: explicit[k] for k in keys}, {k: yearly[k] for k in keys})
        self.assertEqual(explicit["ilk_sure_kaynagi"], "ilk_bitis")

        short = compute_tahliye_10yil(date(2015, 1, 1), initial_months=6)
        self.assertTrue(any("TBK 339/1" in note for note in short["tespitler"]))
        self.assertFalse(any("TBK 339/1" in note for note in yearly["tespitler"]))

        self.assertFalse(any("son kullanım günü gibi" in note for note in explicit["tespitler"]))

        # Sözleşmedeki son kullanım günü --ilk-bitis olarak verilirse uyarılır; hesap girdiden yürür.
        last_day = compute_tahliye_10yil(date(2015, 1, 1), first_end=date(2015, 12, 31))
        warn = [note for note in last_day["tespitler"] if "son kullanım günü gibi" in note]
        self.assertEqual(len(warn), 1)
        self.assertIn("01.01.2016", warn[0])
        self.assertEqual(last_day["ilk_fesih_donem_sonu"], "31.12.2026")
        self.assertIsNone(last_day["ilk_sozlesme_suresi_ay"])
        clamped_last_day = compute_tahliye_10yil(date(2015, 1, 31), first_end=date(2015, 2, 27))
        self.assertTrue(any("son kullanım günü gibi" in note and "28.02.2015" in note
                            for note in clamped_last_day["tespitler"]))
        for start, end in ((date(2015, 1, 31), date(2015, 2, 28)), (date(2016, 2, 29), date(2017, 2, 28)),
                           (date(2015, 1, 1), date(2015, 1, 15)), (date(2015, 3, 15), date(2018, 7, 20))):
            self.assertFalse(any("son kullanım günü gibi" in note
                                 for note in compute_tahliye_10yil(start, first_end=end)["tespitler"]), (start, end))

        for kwargs in ({"initial_years": 1, "initial_months": 12}, {"initial_months": 12, "first_end": date(2016, 1, 1)},
                       {"initial_months": 0}, {"first_end": date(2015, 1, 1)}):
            with self.assertRaises(ValueError):
                compute_tahliye_10yil(date(2015, 1, 1), **kwargs)

    def test_tbk347_leap_day_start_single_step(self):
        r = compute_tahliye_10yil(date(2020, 2, 29), 1)
        self.assertEqual(r["ilk_fesih_donem_sonu"], "29.02.2032")
        self.assertEqual(r["yildonumu_ihtar_esigi"], "29.11.2031")
        # Temkinli alan zincirleme okumanın (28.02.2032) erken eşiğine çekilir; not ile alan aynı tarihi verir.
        self.assertEqual(r["en_gec_ihtar_teblig_tarihi"], "27.11.2031")
        self.assertTrue(any("28.02.2032" in note and "28.11.2031" in note and "27.11.2031" in note
                            and "29.11.2031" in note for note in r["tespitler"]))
        # Aynı sözleşme --ilk-bitis ile verildiğinde temkinli alan değişmez.
        explicit = compute_tahliye_10yil(date(2020, 2, 29), first_end=date(2021, 2, 28))
        self.assertEqual(explicit["en_gec_ihtar_teblig_tarihi"], "27.11.2031")
        r2 = compute_tahliye_10yil(date(2020, 2, 29), 2)
        self.assertEqual(r2["on_yillik_uzama_bitis"], "29.02.2032")
        self.assertEqual(r2["ilk_fesih_donem_sonu"], "28.02.2033")
        self.assertEqual(r2["izleyen_uzama_yillari"][2]["donem_sonu"], "29.02.2036")
        self.assertEqual(r2["izleyen_uzama_yillari"][2]["en_gec_ihtar_tarihi"], "27.11.2035")
        self.assertEqual(r2["izleyen_uzama_yillari"][2]["yildonumu_ihtar_esigi"], "29.11.2035")
        self.assertTrue(any("28.02.2036" in note and "27.11.2035" in note for note in r2["tespitler"]))
        # Ay sonu (31 Ocak) başlangıcında da alan erken eşiğe çekilir.
        month_end = compute_tahliye_10yil(date(2020, 1, 31), initial_months=13)
        self.assertEqual((month_end["ilk_sozlesme_bitis"], month_end["ilk_fesih_donem_sonu"],
                          month_end["en_gec_ihtar_teblig_tarihi"], month_end["yildonumu_ihtar_esigi"]),
                         ("28.02.2021", "29.02.2032", "27.11.2031", "29.11.2031"))
        # Kırpma olmayan başlangıçta zincirleme okuma uyarısı üretilmez.
        self.assertFalse(any("kırpması" in note for note in compute_tahliye_10yil(date(2015, 1, 1), 1)["tespitler"]))

    def test_unknown_and_misaligned_target_rejected(self):
        for target in (None, date(2024, 7, 2)):
            with self.assertRaises(ValueError):
                compute_tespit(date(2018, 7, 1), True, target_period_start=target)

    def test_missing_action_does_not_assert_effect(self):
        result = compute_tespit(date(2018, 7, 1), True,
                                target_period_start=date(2024, 7, 1))
        self.assertIsNone(result['sure_analizi']['aday_etki_tarihi'])
        self.assertIsNone(result['sure_analizi']['hedef_donem_tarih_kosulu'])

    def test_shared_calendar_matches_bam_example(self):
        result = compute_tahliye_10yil(date(2009, 11, 1), 1)
        self.assertEqual(result['ilk_fesih_donem_sonu'], '01.11.2021')
        self.assertEqual(result['en_gec_ihtar_teblig_tarihi'], '31.07.2021')
        self.assertEqual(result['yildonumu_ihtar_esigi'], '01.08.2021')

    def test_range_guards(self):
        for n in (0, 121):
            with self.assertRaises(ValueError):
                compute_periods(date(2018, 7, 1), count=n)
        self.assertEqual(len(compute_periods(date(2018, 7, 1), count=120)), 120)
        with self.assertRaises(ValueError):
            compute_tahliye_10yil(date(2015, 1, 1), 0)
        with self.assertRaises(ValueError):
            compute_tespit(date(2018, 7, 1), True, target_period_start=date(2017, 7, 1))
        proc = self._cli("donemler", "--baslangic", "01.07.2018", "--yil", "0")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("1–120", proc.stderr)

    def test_leap_day_periods_are_contiguous(self):
        ps = compute_periods(date(2024, 2, 29), count=6)
        self.assertEqual(ps[0]["baslangic"], "29.02.2024")
        for prev, cur in zip(ps, ps[1:]):
            self.assertEqual(date.fromisoformat(prev["bitis_iso"]) + timedelta(days=1),
                             date.fromisoformat(cur["baslangic_iso"]))

    def test_cli_subprocess(self):
        # tespit json testi
        proc = self._cli("tespit", "--baslangic", "01.07.2018", "--artis-sarti", "--dava-tarihi", "15.05.2024",
                         "--hedef-donem", "01.07.2024", "--json")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual(data["sozlesme_baslangic"], "01.07.2018")
        self.assertTrue(data["sure_analizi"]["artis_sarti_var"])

        # tahliye-10yil json testi (ilk süre verilmezse 12 ay varsayılır ve işaretlenir)
        proc2 = self._cli("tahliye-10yil", "--baslangic", "01.01.2015", "--json")
        self.assertEqual(proc2.returncode, 0, proc2.stderr)
        data2 = json.loads(proc2.stdout)
        self.assertEqual(data2["toplam_yil"], 12)
        self.assertEqual(data2["ilk_sure_kaynagi"], "varsayilan_12_ay")

        proc3 = self._cli("tahliye-10yil", "--baslangic", "01.01.2015", "--sure-ay", "11", "--json")
        self.assertEqual(proc3.returncode, 0, proc3.stderr)
        self.assertEqual(json.loads(proc3.stdout)["ilk_fesih_donem_sonu"], "01.12.2026")
        proc4 = self._cli("tahliye-10yil", "--baslangic", "01.01.2015", "--ilk-bitis", "01.01.2018", "--json")
        self.assertEqual(proc4.returncode, 0, proc4.stderr)
        self.assertEqual(json.loads(proc4.stdout)["ilk_fesih_donem_sonu"], "01.01.2029")
        proc5 = self._cli("tahliye-10yil", "--baslangic", "01.01.2015", "--ilk-bitis", "31.12.2015")
        self.assertEqual(proc5.returncode, 0, proc5.stderr)
        self.assertIn("son kullanım günü gibi", proc5.stdout)
        both = self._cli("tahliye-10yil", "--baslangic", "01.01.2015", "--sure-yil", "1", "--sure-ay", "12")
        self.assertEqual(both.returncode, 2)
        self.assertEqual(both.stdout, "")

    def test_cli_invalid_date_exits_1(self):
        proc = self._cli("tespit", "--baslangic", "invalid-date", "--artis-sarti", "--hedef-donem", "01.07.2024")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Geçersiz tarih", proc.stderr)
        self.assertTrue(proc.stderr.startswith("HATA:"))
        self.assertEqual(proc.stdout, "")

    def test_cli_missing_required_flags_exits_2(self):
        self.assertEqual(self._cli("tespit", "--baslangic", "01.07.2018").returncode, 2)

    def test_cli_text_modes_and_donemler(self):
        for args, marker in (
                (("tespit", "--baslangic", "01.07.2018", "--artis-sarti", "--hedef-donem", "01.07.2024",
                  "--dava-tarihi", "15.11.2024"), "Aday Dönem Etkisi"),
                (("tespit", "--baslangic", "01.09.2020", "--hedef-donem", "01.09.2025", "--artis-sarti-yok",
                  "--ihtar-tarihi", "01.08.2025", "--dava-tarihi", "15.10.2025"), "Aday Dönem Etkisi"),
                (("tahliye-10yil", "--baslangic", "01.01.2015"), "İlk Hedef Yıldönümü"),
                (("tahliye-10yil", "--baslangic", "01.01.2015", "--sure-ay", "11"), "11 Ay Süreli"),
                (("donemler", "--baslangic", "15.09.2017"), "KİRA DÖNEMLERİ ÇİZELGESİ")):
            proc = self._cli(*args)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn(marker, proc.stdout)
        data = json.loads(self._cli("donemler", "--baslangic", "01.07.2018", "--yil", "11", "--json").stdout)
        self.assertEqual(data["yil_sayisi"], 11)
        self.assertEqual(len(data["donemler"]), 11)
        self.assertTrue(data["donemler"][10]["hak_nesafet_yili"])

    def test_text_output_is_aligned_and_clause_aware(self):
        clause = self._cli("tespit", "--baslangic", "01.09.2020", "--hedef-donem", "01.09.2025", "--artis-sarti").stdout
        self.assertNotIn("En Geç İhtar", clause)
        self.assertIn("345/3'te ihtar şart değil", clause)
        self.assertIn("5 Yıllık Döngü Adayı", clause)
        rows = [line for line in clause.splitlines()
                if ": " in line and not line.startswith(("  ", "---", "==="))]
        self.assertGreater(len(rows), 10)
        self.assertEqual({line.index(": ") for line in rows}, {28})
        table = self._cli("donemler", "--baslangic", "01.09.2020", "--yil", "7").stdout.splitlines()
        body = [line for line in table if line[:1].isdigit()]
        self.assertEqual(len({line.index("İlk sözleşme süresi") for line in body}), 1)

    def test_runs_in_isolated_mode(self):
        proc = self._cli("--help", isolated=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
