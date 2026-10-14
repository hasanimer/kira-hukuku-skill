"""Paketin kaynak bütünlüğünü, belge tutarlılığını ve taşınabilir komut davranışını
çevrimdışı doğrular (yalnız standart kütüphane)."""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unicodedata
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 300  # saniye; tam doğrulama birkaç saniye sürer, Windows CI için geniş pay
SKILL_NAME = 'kira-tespit-asistani'
FRONTMATTER_KEYS = {'name', 'description', 'license', 'allowed-tools', 'metadata'}
# SKILL.md büyük veri dosyalarına bağlantı vermez; ajan onları araçlarla seçerek okur.
BULK_LINK = re.compile(r'(\./)?data/(.+\.jsonl|mevzuat/.+\.md)$')
LAW_HEADING = re.compile(r'(?m)^[ \t]*(?:#+\s*)?(?:\*\*)?MADDE\s+(\d+)\b')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_jsonl(path):
    """pool.py ile aynı okuma: BOM kabul edilir, boş satır atlanır, yalnız \\n satır sonudur."""
    rows = []
    with path.open(encoding='utf-8-sig') as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f'Invalid JSON: {path.name}:{line_no}: {exc}') from exc
    return rows


def run(script, *args, expected=0, parse=True):
    """Betiği alt süreçte çalıştırır; parse=True ise stdout JSON'unu, değilse stdout metnini döner.
    stdout katı UTF-8 çözülür (bozulma görünür kalsın); stderr hoşgörülü çözülür."""
    command = [sys.executable, str(ROOT / 'scripts' / script), *args]
    label = ' '.join([script, *args])
    if len(label) > 200:
        label = label[:197] + '...'
    try:
        result = subprocess.run(command, cwd=ROOT.parent, capture_output=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        raise ValueError(f'{label}: {TIMEOUT} sn içinde tamamlanmadı') from None
    stderr = result.stderr.decode('utf-8', errors='backslashreplace')
    if result.returncode != expected:
        shown = result.stdout.decode('utf-8', errors='backslashreplace')
        raise ValueError(
            f'{label}: çıkış kodu {result.returncode} (beklenen {expected})\n'
            f'stderr: {stderr.strip()[-500:] or "<boş>"}\n'
            f'stdout: {shown.strip()[:500] or "<boş>"}')
    try:
        stdout = result.stdout.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise ValueError(f'{label}: stdout UTF-8 değil ({exc})') from None
    if not parse:
        return stdout
    if not stdout.strip():
        raise ValueError(f'{label}: stdout boş, JSON bekleniyordu')
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f'{label}: geçersiz JSON ({exc}): {stdout[:300]}') from None


def check_data_files(manifest):
    data_dir = ROOT / 'data'
    for name, digest in manifest['files'].items():
        path = (data_dir / name).resolve()
        require(path.is_relative_to(data_dir), f'Invalid manifest path: {name}')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == digest,
                f'File hash mismatch: {name}')
    # Manifestte olmayan veri dosyası (ör. eski etiket havuzu) sessizce kalamaz.
    present = {p.relative_to(data_dir).as_posix() for p in data_dir.rglob('*')
               if p.is_file() and p.name != 'manifest.json'
               and not any(part.startswith('.') for part in p.relative_to(data_dir).parts)}
    require(present == set(manifest['files']),
            f'Unpinned or missing data files: {sorted(present ^ set(manifest["files"]))}')
    data = json.loads((data_dir / 'mevzuat/6098-source.json').read_text(encoding='utf-8'))
    text = '\n\n'.join(c['markdown'] for c in data['chunks'])
    readable = (data_dir / 'mevzuat/6098-turk-borclar-kanunu.md').read_text(encoding='utf-8')
    require(readable == text + '\n', 'Readable law differs from source chunks')


def check_pool(manifest, pool):
    pool_rows, envelope = pool.load_pool(ROOT / 'data')
    require(envelope['manifest_verified'], 'Pool files not verified against manifest')
    by_id = {str(r['document_id']): r for r in pool_rows}
    stats = run('pool.py', 'stats')
    require(stats['records'] == manifest['records'] == len(pool_rows), 'Decision count mismatch')
    require(stats['manifest_verified'] and stats['pool_files'] == envelope['pool_files'],
            'pool.py stats envelope differs from in-process load')
    if 'kinds' in manifest:
        require(stats['kinds'] == manifest['kinds'], 'Kind count mismatch')
    if 'collections' in manifest:
        for name, count in manifest['collections'].items():
            require(len(read_jsonl(ROOT / 'data' / name)) == count,
                    f'Collection count mismatch: {name}')
        require(stats['collections'] == manifest['collections'], 'Pool collection count mismatch')
    # quote yalnız girdiyi NFC'ye getirir; bunun önkoşulu bütün metinlerin NFC olmasıdır.
    for row in pool_rows:
        require(unicodedata.is_normalized('NFC', row['text']),
                f'Corpus text not NFC: {row["collection"]} {row["document_id"]}')
    bam_file = ROOT / 'data/bam-selected.jsonl'
    if bam_file.exists():
        for bam in read_jsonl(bam_file):
            key = str(bam['document_id'])
            require(key in by_id, f'BAM record missing from pool: {key}')
            fetched = {**pool.metadata(by_id[key]), 'text': by_id[key]['text']}
            require(fetched['text'] == bam['text'] and fetched['source_url'] == bam['source_url']
                    and fetched['collection'] == bam_file.name, 'BAM text or provenance lost')
            require(fetched.get('court_type') == 'bam', f'BAM selection record lost court_type: {key}')
            if bam.get('redactions'):
                require(fetched['redactions'] == bam['redactions'] and
                        fetched['source_text_sha256'] == bam['source_text_sha256'],
                        'Anonymization provenance lost')
                require(bam['source_text_sha256'] != bam['text_sha256'],
                        'Redacted text must have a distinct source hash')
                require(bam['text'].count('[KİŞİ ADI ANONİMLEŞTİRİLDİ]') ==
                        bam['redactions']['replacement_count'],
                        'Anonymization count mismatch')
        filtered = run('pool.py', 'search', 'kira', '--court-type', 'bam')
        # Seçkilerin hepsindeki BAM kayıtları (derleme dahil); pool.py'nin sözcük başı eşleşmesiyle.
        pattern = pool.term_pattern('kira')
        expected = sum(row.get('court_type') == 'bam' and bool(pattern.search(pool.normalize(row['text'])))
                       for row in pool_rows)
        require(filtered['total_matches'] == expected, 'BAM filter missed records')
        require(all(r['court_type'] == 'bam' for r in filtered['results']), 'BAM filter leaked')
        # Hesaplanan beklentiden bağımsız çapa: seçkideki her kayıt filtrede görünmeli.
        everything = run('pool.py', 'search', 'kira', '--court-type', 'bam', '--limit', '2000')
        require(sum(r['collection'] == bam_file.name for r in everything['results']) ==
                manifest['collections'][bam_file.name], 'BAM selection dropped out of --court-type bam')
    yargitay_file = ROOT / 'data/yargitay-selected.jsonl'
    if yargitay_file.exists():
        selected = read_jsonl(yargitay_file)
        for decision in selected:
            key = str(decision['document_id'])
            require(key in by_id, f'Yargitay record missing from pool: {key}')
            fetched = {**pool.metadata(by_id[key]), 'text': by_id[key]['text']}
            require(fetched['text'] == decision['text'] and
                    fetched['source_url'] == decision['source_url'] and
                    fetched['research_notes'] == decision['research_notes'],
                    'Yargitay text or provenance lost')
        filtered = run('pool.py', 'search', 'kira', '--court-type', 'yargitay', '--limit', '2000')
        require({r['document_id'] for r in filtered['results']}.issuperset(
                {r['document_id'] for r in selected}), 'Yargitay filter missed additions')
        require(all(r['court_type'] == 'yargitay' for r in filtered['results']),
                'Yargitay filter leaked')
    # Seçki kimlikleri (UUID) için CLI quote yolunu gerçek veriyle bir kez sına.
    for name in pool.SELECTIONS:
        if (ROOT / 'data' / name).exists():
            sample = read_jsonl(ROOT / 'data' / name)[0]
            quoted = run('pool.py', 'quote', str(sample['document_id']), '--', sample['text'][-100:])
            require(quoted['exact_match'] and quoted['collection'] == name,
                    f'{name}: final text quote failed')
    derleme_file = ROOT / 'data/derleme-v5-selected.jsonl'
    if derleme_file.exists():
        index = run('derleme.py', 'validate')
        require(index['structural_validation'] == 'pass', 'Compilation index invalid')
        compiled = read_jsonl(derleme_file)
        require(all(d['source_url'] == pool.BEDESTEN_URL.format(d['document_id']) for d in compiled),
                'Compilation texts must carry their Bedesten address')
        # CLI yolunu ilk ve son kayıtla sına; tüm kayıtlar aynı okuyucudan geçer.
        for decision in (compiled[0], compiled[-1]):
            fetched = run('pool.py', 'get', str(decision['document_id']))
            require(fetched['text'] == decision['text'] and
                    fetched['research_notes'] == decision['research_notes'] and
                    fetched['collection'] == derleme_file.name, 'Compilation text or provenance lost')
    # Kod tarafındaki kapsam uyarıları ve kapanış tarihi uyarısı veriyle eşleşmeyi sürdürmeli.
    for key in ('1018247800', '504158200'):
        require(key in by_id and by_id[key]['out_of_scope'] and by_id[key]['research_notes'],
                f'Out-of-scope caution no longer matches record {key}')
    require('date_warning' in pool.metadata(by_id['147530800']) and
            'date_warning' not in pool.metadata(by_id['964286900']),
            'Closing-date conflict flag wrong')
    return stats


def check_pool_cli():
    search = run('pool.py', 'search', 'eski kiracı', '--kind', 'esas_gerekcesi', '--limit', '1')
    require(search['total_matches'] > 0, 'Known search returned no matches')
    row = run('pool.py', 'get', search['results'][0]['document_id'])
    quote = row['text'][:80]
    match = run('pool.py', 'quote', row['document_id'], quote)
    require(match['exact_match'] and match['occurrences'][0]['start'] == 0
            and not match['input_normalized'], 'Exact quote verification failed')
    absent = run('pool.py', 'quote', row['document_id'], 'NONEXISTENT-QUOTE-f06d52cb', expected=3)
    require(absent is not None and not absent['exact_match'], 'Absent quote was accepted')
    require(run('pool.py', 'get', '0', expected=3, parse=False) == '',
            'Unknown id must be reported as not found')
    # Ayrık kodlanmış (NFD) Türkçe harf içeren birebir alıntı da bulunmalı.
    idx = next(i for i, ch in enumerate(row['text']) if ch in 'çşğüöÇŞĞÜÖİ')
    span = row['text'][max(0, idx - 20):idx + 20]
    nfd = run('pool.py', 'quote', row['document_id'], '--', unicodedata.normalize('NFD', span))
    require(nfd['exact_match'] and nfd['input_normalized'], 'NFD quote not normalized')
    # Bedesten çıktısı yerel metinden yalnız boşlukta ayrışabilir; gevşek mod isteğe bağlıdır.
    loose = re.sub(r'\s+', lambda m: m.group(0) + ' ', quote, count=1)
    require(loose != quote, 'Whitespace probe needs a quote with spaces')
    run('pool.py', 'quote', row['document_id'], loose, expected=3)
    spaced = run('pool.py', 'quote', row['document_id'], loose, '--ignore-space')
    require(spaced['match_mode'] == 'ignore_space' and not spaced['exact_match'] and
            spaced['occurrences'][0]['start'] == len(quote) - len(quote.lstrip()) and
            spaced['occurrences'][0]['matched_text'] == quote.strip(),
            'Whitespace-insensitive quote mapping failed')
    with tempfile.TemporaryDirectory(prefix='kira-integrity-') as directory:
        corrupt = dict(row, text=row['text'] + 'changed')
        path = Path(directory) / 'topic-rescan-assistant-adjusted.jsonl'
        path.write_text(json.dumps(corrupt), encoding='utf-8')
        run('pool.py', '--root', directory, 'stats', expected=1, parse=False)


def check_quality_and_counts():
    scenarios = run('scenarios.py', 'list')
    quality = run('quality.py', 'validate')
    triggers = run('quality.py', 'triggers')
    require(triggers['structural_validation'] == 'pass'
            and triggers['trigger_performance'] == 'not_measured',
            'Trigger set structure or qualification lost')
    answers = run('decision_qa.py', 'validate')
    require(answers['examples'] == quality['cards'] and answers['model_performance'] == 'not_measured',
            'Decision answer set incomplete or mislabeled')
    require(quality['structural_validation'] == 'pass' and quality['cases'] >= 40
            and quality['cards'] >= 6 and quality['legal_performance'] == 'not_measured',
            'Quality suite structure or performance qualification lost')
    catalog = json.loads((ROOT / 'references/kiraci-senaryolari.json').read_text(encoding='utf-8'))
    require(scenarios['fictional'] and 0 < scenarios['total'] == len(scenarios['scenarios'])
            == len(catalog['scenarios']), 'Scenario catalog incomplete or fiction label lost')
    # Belgelerdeki sayılar araç çıktısından sapmamalı; sayı değişirse bu belgeler birlikte güncellenir.
    n, k, s = quality['cases'], quality['cards'], scenarios['total']
    for rel, phrases in {
            'README.md': [f'[{n} özgün dosyayla sınama ve {k} yapılandırılmış karar kartı]',
                          f'{s} kurgu senaryo'],
            'SKILL.md': [f'[{n} dosyalık sınama akışını]'],
            'references/kalite-sinama.md': [f'**{n} özgün kurgu sınama dosyası (B01–B{n:02d})**',
                                            f'**{k} yapılandırılmış karar kartı**',
                                            f'bu {n} soruyla'],
            'references/kararlardan-soru-yanit.md': [f'Mevcut {n} kurgu sınama dosyasının (B01–B{n:02d})']}.items():
        text = (ROOT / rel).read_text(encoding='utf-8')
        for phrase in phrases:
            require(phrase in text, f'Count drift in {rel}: {phrase}')


def check_law():
    info = run('tbk.py')
    require(info['article_count'] == 649 and 'markdown' not in info, 'tbk.py source mode lost')
    articles = {}
    for number in (1, 8, 59, 344, 345, 647, 649):
        article = run('tbk.py', str(number))
        require(article['requested_article'] == number and
                [int(n) for n in LAW_HEADING.findall(article['markdown'])] == [number],
                f'Article {number} unavailable or sliced to the wrong article')
        articles[number] = article
    a344 = articles[344]
    require(a344['markdown'].startswith('## II. Belirlenmesi')
            and 'III. Dava açma süresi' not in a344['markdown']
            and '7161' in a344['footnotes'].get('3', '')
            and 'tacir' in a344.get('temporary_provision', ''),
            'Article 344 heading/footnotes/temporary provision wrong')
    require(articles[345]['markdown'].startswith('## III. Dava açma süresi'),
            'Article 345 heading missing')
    require(articles[8]['markdown'].rstrip().endswith('öneri sayılır.'),
            'Article 8 lost its second paragraph')
    require('GEÇİCİ MADDE' not in articles[647]['markdown'], 'Temporary articles leak into 647')
    require('İŞLENEMEYEN' not in articles[649]['markdown']
            and '* * *' not in articles[649]['markdown'], 'Tail or footnotes leak into 649')
    g1 = run('tbk.py', '--gecici', '1')
    require('7409/4' in g1['markdown'] and '7456' not in g1['markdown'], 'Geçici 1 unavailable')
    g2 = run('tbk.py', '--gecici', '2')
    require('7456/23' in g2['markdown'] and '6217' not in g2['markdown']
            and 'MADDE 648' not in g2['markdown'], 'Geçici 2 unavailable')
    ek = run('tbk.py', '--ek')
    require('6217' in ek['markdown'] and '6353/53' in ek['markdown'],
            'Unenacted provisions unavailable')
    run('tbk.py', '650', expected=2, parse=False)


def check_calculators():
    deadline = run('deadlines.py', 'tbk345', '2026-09-01')
    require(deadline['raw_dates']['otuz_gun_once_esigi'] == '2026-08-02' and
            deadline['status'] == 'takvim_adayi_hukuki_kontrol_gerekli',
            'Deadline calendar or qualification lost')
    calc = run('hesap.py', 'tespit', '--baslangic', '01.07.2018', '--artis-sarti',
               '--hedef-donem', '01.07.2024', '--json')
    first = calc['ilk_hak_nesafet_donemi']
    require(calc['bes_yil_dolum_tarihi'] == '30.06.2023' and
            (first['baslangic'], first['bitis'], first['kira_yili']) == ('01.07.2023', '30.06.2024', 6),
            'hesap.py tespit calculation error')
    calc10 = run('hesap.py', 'tahliye-10yil', '--baslangic', '01.01.2015', '--sure-yil', '1',
                 '--json')
    require(calc10['toplam_yil'] == 12 and calc10['ilk_fesih_donem_sonu'] == '01.01.2027' and
            calc10['en_gec_ihtar_teblig_tarihi'] == '30.09.2026' and
            calc10.get('yildonumu_ihtar_esigi') == '01.10.2026',
            'hesap.py tahliye-10yil calculation error')
    run('hesap.py', 'tespit', '--baslangic', 'invalid', '--hedef-donem', '01.07.2024',
        '--artis-sarti', expected=1, parse=False)


def check_triage():
    with tempfile.TemporaryDirectory(prefix='kira-triage-') as directory:
        sample = Path(directory) / 'triage.json'
        sample.write_text(json.dumps({'query': 'Tahliye taahhüdüne itiraz ve depozito iadesi', 'candidates': [
            {'provider': 'ornek', 'source_id': 'temsili-1', 'text': 'Kiracı depozitonun iadesini talep etmiştir.',
             'full_text': False}]}, ensure_ascii=False), encoding='utf-8')
        dry = run('triage.py', str(sample), '--dry-run')
        require(dry['model'] == 'jev-latest' and {'outside_scope', 'relevant_0', 'court_view_0'} <= set(dry['questions'])
                and len(dry['state']['candidates'][0]['text_sha256']) == 64, 'triage.py dry-run request lost')


def check_udf():
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w') as udf:
        udf.writestr('content.xml', '<content>KURGU SINAMA</content>')
    with tempfile.TemporaryDirectory(prefix='kira-udf-') as directory:
        encoded = Path(directory) / 'yanit.b64'
        encoded.write_bytes(base64.b64encode(archive.getvalue()))
        target = str(Path(directory) / 'taslak.udf')
        digest = hashlib.sha256(archive.getvalue()).hexdigest()
        saved = run('udf.py', 'kaydet', str(encoded), '--sha256', digest, '--cikti', target)
        require(saved['kaydedildi'] and Path(target).read_bytes() == archive.getvalue(),
                'UDF save failed')
        rejected = run('udf.py', 'kaydet', str(encoded), '--sha256', '0' * 64, '--cikti',
                       str(Path(directory) / 'baska.udf'), expected=2)
        require(not rejected['kaydedildi'] and not (Path(directory) / 'baska.udf').exists(),
                'UDF hash mismatch was saved')
        run('udf.py', 'kaydet', str(encoded), '--sha256', digest, '--cikti', target, expected=1,
            parse=False)


def check_frontmatter():
    skill = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
    require(skill.startswith('---\n') and '\n---\n' in skill[4:], 'SKILL.md frontmatter missing')
    front = skill[4:].split('\n---\n', 1)[0]
    meta = {}
    for line in front.splitlines():
        # Yalnız üst düzey anahtarlar; girintili satırlar (ör. metadata altı) atlanır.
        if not line.strip() or line[0] in ' \t' or line.startswith('#'):
            continue
        key, sep, value = line.partition(':')
        require(sep, f'SKILL.md frontmatter line invalid: {line}')
        meta[key.strip()] = value.strip().strip('"\'')
    require({'name', 'description'} <= set(meta) <= FRONTMATTER_KEYS, 'SKILL.md frontmatter keys invalid')
    require(re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', meta['name']) and len(meta['name']) <= 64
            and meta['name'] == SKILL_NAME, 'Skill name invalid')
    description = meta['description']
    require(0 < len(description) <= 1024 and not ({'<', '>'} & set(description)),
            'Skill description invalid')
    # Düz YAML skaleri ': ' ve ' #' taşıyamaz; özel karakterle başlayamaz.
    require(': ' not in description and ' #' not in description
            and description[0] not in '>|[]{}&*!%@`\'"#,?:-', 'SKILL.md description unsafe for YAML')
    # Codex önceki skill belgelerinde açıklamayı tek satır ve 500 karakterle sınırlıyordu; bayt sayımına karşı temkinli.
    require(len(meta['description'].encode('utf-8')) <= 500, 'Skill description exceeds 500-byte Codex budget')
    require('$' + meta['name'] in (ROOT / 'agents/openai.yaml').read_text(encoding='utf-8'),
            'openai.yaml invocation does not match skill name')
    require(len(skill.splitlines()) <= 500, 'SKILL.md exceeds 500 lines')


def heading_slugs(text):
    """GitHub başlık bağlantıları; kod blokları atlanır, tekrar eden başlığa -1, -2 eklenir."""
    seen, slugs, fenced = {}, set(), False
    for line in text.splitlines():
        if line.lstrip().startswith('```'):
            fenced = not fenced
            continue
        match = None if fenced else re.match(r'#{1,6}\s+(.*?)\s*#*\s*$', line)
        if match:
            slug = re.sub(r'[^\w\- ]', '', match.group(1).strip().lower()).replace(' ', '-')
            count = seen.get(slug, 0)
            seen[slug] = count + 1
            slugs.add(slug if count == 0 else f'{slug}-{count}')
    return slugs


def check_links():
    law_md = ROOT / 'data/mevzuat/6098-turk-borclar-kanunu.md'
    docs = [p for p in sorted(ROOT.rglob('*.md'))
            if not any(part.startswith('.') or part == 'research-private'
                       for part in p.relative_to(ROOT).parts) and p != law_md]
    for doc in docs:
        text = re.sub(r'```.*?```', '', doc.read_text(encoding='utf-8'), flags=re.S)
        text = re.sub(r'`[^`\n]*`', '', text)
        rel = doc.relative_to(ROOT).as_posix()
        for target in re.findall(r'\]\(([^)\s]+)', text):
            if '://' in target or target.startswith('mailto:'):
                continue
            path, _, fragment = target.partition('#')
            if rel == 'SKILL.md':
                require(not BULK_LINK.match(path),
                        f'SKILL.md must not link bulk data directly: {target}')
            dest = doc if not path else doc.parent / path
            require(dest.exists(), f'Broken link in {rel}: {target}')
            if fragment and dest.suffix == '.md':
                require(fragment in heading_slugs(dest.read_text(encoding='utf-8')),
                        f'Broken anchor in {rel}: {target}')


def main():
    manifest = json.loads((ROOT / 'data/manifest.json').read_text(encoding='utf-8'))
    check_data_files(manifest)
    sys.path.insert(0, str(ROOT / 'scripts'))
    import pool  # noqa: E402  (betik klasörü yola eklendikten sonra)
    stats = check_pool(manifest, pool)
    check_pool_cli()
    check_quality_and_counts()
    check_law()
    check_calculators()
    check_triage()
    check_udf()
    check_frontmatter()
    check_links()
    print(f'PASS: {stats["records"]} decisions, file/text hashes, law, links, frontmatter, '
          'CLI, UDF and rejection checks')


if __name__ == '__main__':
    for stream, errors in ((sys.stdout, 'strict'), (sys.stderr, 'backslashreplace')):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors=errors)
    argparse.ArgumentParser(
        description='Paketin veri bütünlüğünü ve CLI davranışını çevrimdışı doğrular.').parse_args()
    try:
        main()
    except (ValueError, OSError, KeyError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
