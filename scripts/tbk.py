"""6098 sayılı Türk Borçlar Kanunu'nun pakete gömülü kopyasından madde getirir.

Yalnız standart kütüphane kullanır. Kopyanın SHA-256 değeri data/manifest.json ile,
bölüm sırası, toplam bayt sayısı ve 1-649 madde başlıkları her çağrıda denetlenir.
Numarasız çağrı yalnız kaynak bilgisini verir; geçici madde 1-2 için --gecici 1|2,
6217 sayılı Kanun geçici 2 ve değişiklik tablosu için --ek kullanılır.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

DATA_ROOT = Path(__file__).resolve().parents[1] / 'data'
SOURCE_NAME = 'mevzuat/6098-source.json'
ARTICLE_COUNT = 649
EPILOG = ('Çıkış kodları: 0 başarılı; 1 mevzuat verisi okunamadı veya bütünlük denetimi\n'
          'başarısız (hash, bölüm, bayt, başlık veya dipnot uyuşmazlığı); 2 kullanım hatası\n'
          '(ör. 1-649 dışında madde).')

HEADING = re.compile(r'(?m)^[ \t]*(?:#+\s*)?(?:\*\*)?MADDE\s+(\d+)\b')
# Kanuna işlenemeyen hükümler (6217 geçici 2) ve değişiklik tablosu 649. maddeden sonra gelir.
TAIL_HEADING = re.compile(r'(?m)^[ \t]*(?:\*\*)?6098 SAYILI KANUNA İŞLENEMEYEN HÜKÜMLER')
TEMPORARY_HEADING = re.compile(r'(?m)^[ \t]*(?:\*\*)?GEÇİCİ MADDE\s+(\d+)\b')
# Metin içi dipnot atfı: [\[3\]](#_ftn3)
REF = re.compile(r'\[\\\[(\d+)\\\]\]\(#_ftn\d+\)')
FOOTNOTE = re.compile(r'(?m)^\[_\*\*\\\[(\d+)\\\]\*\*_\]\(#_ftnref\d+\)\s*(.+)$')
FOOTNOTE_SEPARATOR = '\n* * *\n'
GM2_START = '**1- 31/3/2011 tarihli ve 6217 sayılı Kanunun hükmüdür:**'
GM2_END = '**6098 SAYILI KANUNA EK VE DEĞİŞİKLİK'
# 6217 sayılı Kanun geçici madde 2'nin saydığı maddeler; başlıklarındaki çıplak "2" dipnot 2'dir.
GM2_ARTICLES = frozenset({323, 325, 331, 340, 342, 343, 344, 346, 354})
TAIL_LABEL = 'işlenemeyen hükümler ve değişiklik tablosu'
ARTICLE_NOTE = (
    "Starts with the article's own heading(s) and ends before the next article's heading. "
    '"footnotes" holds the amendment footnotes referenced in the block (a bare digit after a heading, '
    'e.g. "Belirlenmesi2", is footnote 2). For 323, 325, 331, 340, 342, 343, 344, 346 and 354, '
    '"temporary_provision" is 6217 s. Kanun geçici madde 2: it covered only workplace leases with '
    'merchant or legal-person tenants, and its 8-year period ended on 1/7/2020. Temporary articles '
    '1-2 (Laws 7409/7456) and the unenacted-provisions tail are available via --gecici / --ek.')
TEMPORARY_NOTE = (
    'TBK temporary article added by Law 7409 (geçici 1) or Law 7456 (geçici 2). It covers only '
    'residential lease periods renewed within the dates stated in its text; it does not apply to '
    'workplace leases or to a TBK 344/3 market-rent determination automatically.')
TAIL_NOTE = (
    'Unenacted provisions (6217 s. Kanun geçici madde 2, workplace leases with merchant or '
    'legal-person tenants, 8 years from 1/7/2012) and the amendment table; "footnotes" lists every '
    'amendment footnote of the snapshot.')


def load_law(data_root: Path) -> tuple[dict, str, list, str]:
    """Kopyayı bir kez okur; hash'i ayrıştırmadan önce manifestle karşılaştırır.

    Dönüş: (kaynak JSON, birleşik metin, madde başlığı eşleşmeleri, SHA-256)."""
    raw = (data_root / SOURCE_NAME).read_bytes()
    manifest = json.loads((data_root / 'manifest.json').read_text(encoding='utf-8'))
    digest = hashlib.sha256(raw).hexdigest()
    if digest != manifest['files'][SOURCE_NAME]:
        raise ValueError('Mevzuat kopyasının hash değeri manifest ile uyuşmuyor')
    data = json.loads(raw.decode('utf-8'))
    chunks = data['chunks']
    if [c['chunk']['index'] for c in chunks] != list(range(1, 8)) or any(
            c['chunk']['total'] != 7 for c in chunks):
        raise ValueError('Mevzuat bölümleri eksik veya sırasız')
    text = '\n\n'.join(c['markdown'] for c in chunks)
    if len(text.encode('utf-8')) != chunks[0]['total_bytes']:
        raise ValueError('Mevzuat toplam bayt sayısı uyuşmuyor')
    matches = list(HEADING.finditer(text))
    if [int(m.group(1)) for m in matches] != list(range(1, ARTICLE_COUNT + 1)):
        raise ValueError('Madde başlıkları eksik, tekrarlı veya sırasız')
    return data, text, matches, digest


def structure(text, matches):
    """Geçici maddelerin, ek hükümlerin ve dipnot bloğunun yerini denetleyerek bulur."""
    tail = TAIL_HEADING.search(text)
    if not tail:
        raise ValueError('İşlenemeyen hükümler başlığı bulunamadı')
    # 6217 sayılı Kanunun "GEÇİCİ MADDE 2" başlığı ek bölümdedir; arama ondan önce biter.
    temporary = [m for m in TEMPORARY_HEADING.finditer(text) if m.start() < tail.start()]
    if [int(m.group(1)) for m in temporary] != [1, 2] or not (
            matches[646].start() < temporary[0].start() < temporary[1].start()
            < matches[647].start()):
        raise ValueError('Geçici madde başlıkları eksik veya yerinde değil')
    separator = text.find(FOOTNOTE_SEPARATOR)
    if separator < tail.start():
        raise ValueError('Dipnot bloğu bulunamadı')
    gm2_start, gm2_end = text.find(GM2_START), text.find(GM2_END)
    if not tail.start() < gm2_start < gm2_end < separator:
        raise ValueError('6217 sayılı Kanun geçici madde 2 metni bulunamadı')
    footnotes = {int(m.group(1)): m.group(2).strip().strip('_').strip()
                 for m in FOOTNOTE.finditer(text[separator:])}
    if not footnotes or any(int(ref) not in footnotes for ref in REF.findall(text[:separator])):
        raise ValueError('Dipnot atfı ile dipnot metni uyuşmuyor')
    return {'tail': tail.start(), 'temporary': [m.start() for m in temporary],
            'separator': separator, 'footnotes': footnotes,
            'gm2_text': text[gm2_start:gm2_end].strip()}


def is_heading(paragraph):
    """Kenar/üst başlık paragrafı mı? Kaynakta '## ...' biçimli gövde paragrafları da var
    (ör. TBK 8, 56, 58, 62'nin ikinci fıkraları); noktalama ile biten paragraf başlık sayılmaz."""
    p = paragraph.strip()
    if not p or 'MADDE' in p:
        return False
    q = REF.sub('', re.sub(r'^#+\s*', '', p)).strip().strip('*').strip()
    q = re.sub(r'\d+$', '', q).strip()
    return 0 < len(q) <= 120 and not q.endswith(('.', ';', ':', ','))


def block_start(text, matches, index):
    """index (0 tabanlı) maddesinin başlık paragraflarıyla birlikte başladığı konum."""
    floor = matches[index - 1].end() if index else 0
    start = matches[index].start()
    for m in reversed(list(re.finditer(r'(?:^|\n\n)([^\n].*?)(?=\n\n|$)',
                                       text[floor:start], re.S))):
        if not m.group(1).strip():
            continue
        if not is_heading(m.group(1)):
            break
        start = floor + m.start(1)
    return start


def article_result(text, matches, parts, number):
    start = block_start(text, matches, number - 1)
    if number == 647:
        end = parts['temporary'][0]
    elif number == ARTICLE_COUNT:
        end = parts['tail']
    else:
        end = block_start(text, matches, number)
    markdown = text[start:end].strip()
    refs = {int(x) for x in REF.findall(markdown)}
    if number in GM2_ARTICLES:
        refs.add(2)
    result = {'requested_article': number, 'markdown': markdown,
              'footnotes': {str(k): parts['footnotes'][k] for k in sorted(refs)}}
    if number in GM2_ARTICLES:
        result['temporary_provision'] = parts['gm2_text']
    result['context_note'] = ARTICLE_NOTE
    return result


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, epilog=EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    target = parser.add_mutually_exclusive_group()
    target.add_argument('article', type=int, nargs='?',
                        help='TBK madde numarası (1-649); verilmezse yalnız kaynak bilgisi döner')
    target.add_argument('--gecici', type=int, choices=[1, 2],
                        help='TBK geçici madde 1 (7409) veya 2 (7456) metnini getirir')
    target.add_argument('--ek', action='store_true',
                        help='6217 sayılı Kanun geçici madde 2, değişiklik tablosu ve tüm dipnotlar')
    return parser


def main(argv=None, data_root=None):
    for stream, errors in ((sys.stdout, 'strict'), (sys.stderr, 'backslashreplace')):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors=errors)
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.article is not None and not 1 <= args.article <= ARTICLE_COUNT:
        parser.error(f'Madde numarası 1 ile {ARTICLE_COUNT} arasında olmalı')
    data, text, matches, digest = load_law(data_root or DATA_ROOT)
    parts = structure(text, matches)
    chunks = data['chunks']
    result = {'retrieved_at_utc': data['retrieved_at_utc'],
              'source_url': chunks[0]['source_url'], 'article_count': len(matches),
              'snapshot_sha256': digest,
              'note': 'Stored retrieval snapshot; recheck effective law for the relevant date.'}
    if args.article is not None:
        result.update(article_result(text, matches, parts, args.article))
    elif args.gecici:
        first, second = parts['temporary']
        start, end = (first, second) if args.gecici == 1 else (
            second, block_start(text, matches, 647))
        result.update({'requested': f'geçici {args.gecici}',
                       'markdown': text[start:end].strip(), 'context_note': TEMPORARY_NOTE})
    elif args.ek:
        result.update({'requested': TAIL_LABEL,
                       'markdown': text[parts['tail']:parts['separator']].strip(),
                       'footnotes': {str(k): v for k, v in sorted(parts['footnotes'].items())},
                       'context_note': TAIL_NOTE})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cli(argv=None, data_root=None):
    """Okuma ve bütünlük hataları kullanım hatasından (2) ayrı olarak 1 koduyla döner."""
    try:
        return main(argv, data_root)
    except (OSError, ValueError, KeyError) as exc:
        print(f'HATA (mevzuat bütünlüğü): {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(cli())
