"""Tahliye yolları kataloğu: sebebe göre rota kartı, emsal listesi ve ham takvim adayı.

Katalog references/tahliye-yollari.json, rehber references/tahliye.md dosyasıdır. Yalnız standart
kütüphane kullanır. Komutlar: list, yol, emsal, validate. Sebep anahtarla, aksan/büyük harf farkı
gözetmeden veya kısa adla verilebilir (ör. temerrüt, 315, TBK 316/2, İİK 269, 352/2, yeni malik).

`yol --tarih` her kurala aynı tarihi girdi olarak verir; sonuç deadlines.py ile aynı ham takvim
adayıdır, hukuki son gün görüşü değildir. Tatil, adli tatil, arabuluculuk durması ve TBK 353
uzaması uygulanmaz. Her süreyi kendi başlangıç olayının tarihiyle ayrı hesapla.
"""
import argparse
from datetime import date
import functools
import json
import os
from pathlib import Path
import re
import subprocess
import sys

# Kardeş modül içe aktarımı PYTHONSAFEPATH / python -I altında da çalışsın.
_HERE = str(Path(__file__).resolve().parent)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import deadlines  # noqa: E402
import pool  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(_HERE)
CATALOG = 'references/tahliye-yollari.json'
GUIDE = 'references/tahliye.md'
SCHEMA_VERSION = 1
EXIT_OK, EXIT_DATA, EXIT_USAGE, EXIT_NOT_FOUND = 0, 1, 2, 3
EPILOG = (
    'Çıkış kodları: 0 başarılı; 1 veri hatası (katalog okunamadı, yapı bozuk veya validate\n'
    'denetimi başarısız; stderr "HATA:" ile başlar, validate JSON raporu basar); 2 kullanım hatası\n'
    '(geçersiz seçenek veya tarih); 3 bilinmeyen sebep (stderr geçerli anahtarları listeler).')
# Rehberdeki sıra; katalog bu on sebebi tam olarak içermelidir.
GROUNDS = ('ortak_usul', 'temerrut', 'iki_hakli_ihtar', 'taahhut', 'ihtiyac', 'yeni_malik',
           'on_yillik_uzama', 'akde_aykirilik', 'kiracinin_konutu_ve_diger', 'tahliye_sonrasi')
# Kısa adlar canonical() biçiminde: aksansız, küçük harf, ayraçlar tek tire.
_ALIAS_SOURCE = {
    'temerrut': ('temerrüt', 'temerrut', '315', 'odeme', '269', 'ilamsiz', 'ilamsiz-tahliye',
                 '13-ornek'),
    'iki_hakli_ihtar': ('iki-ihtar', 'iki-hakli-ihtar', '352-2'),
    'taahhut': ('taahhüt', 'taahhut', 'taahhutname', '352-1', '272', '14-ornek'),
    'ihtiyac': ('ihtiyaç', 'ihtiyac', 'gereksinim', '350', 'yeniden-insa'),
    'yeni_malik': ('yeni-malik', '351'),
    'on_yillik_uzama': ('on-yil', '10yil', '10-yil', '347', 'uzama'),
    'akde_aykirilik': ('aykirilik', 'ozen', '316', 'komsu'),
    'kiracinin_konutu_ve_diger': ('kiracinin-konutu', '352-3', 'diger'),
    'ortak_usul': ('usul', 'arabuluculuk', 'ortak'),
    'tahliye_sonrasi': ('sonrasi', 'tehir', '355', 'icra'),
}
# Kanun önekli yazım (TBK 350, İİK 269): önek yalnız kendi kanununun madde kısa adında düşer.
IIK_ARTICLES = ('269', '272')
LAW_PREFIX = re.compile(r'(tbk|iik)-?(\d{3}(?:-\d)?)')
# Fıkra veya bent yazımı (316/2, 350/1) maddenin kısa adına iner; 352 fıkraları ayrı sebeptir.
PARAGRAPHS = {'315': 2, '316': 3, '347': 3, '350': 2, '351': 2}
TOP_KEYS = ('schema_version', 'version', 'checked_on', 'note', 'grounds')
ENTRY_KEYS = ('key', 'title', 'guide_heading', 'legal_basis', 'requester', 'scope', 'notice',
              'preconditions', 'deadlines', 'routes', 'tenant_defenses', 'pitfalls', 'decisions',
              'open_questions')
ENTRY_TEXT = ('key', 'title', 'guide_heading', 'requester', 'scope', 'notice')
ENTRY_LISTS = ('legal_basis', 'preconditions', 'tenant_defenses', 'pitfalls', 'open_questions')
DEADLINE_KEYS = ('name', 'start_event', 'duration', 'formula', 'rule', 'command', 'basis',
                 'confidence')
DEADLINE_TEXT = ('name', 'start_event', 'duration', 'formula', 'command', 'basis')
ROUTE_KEYS = ('route', 'forum', 'arabuluculuk', 'arabuluculuk_note', 'procedure')
ROUTE_TEXT = ('route', 'forum', 'arabuluculuk_note', 'procedure')
DECISION_KEYS = ('document_id', 'kunye', 'outcome', 'holding', 'quote', 'caveat')
CONFIDENCE = {'high': 'yüksek', 'medium': 'orta', 'low': 'düşük'}
MEDIATION = {'dava_sarti': 'dava şartı', 'istisna': 'istisna', 'tartismali': 'tartışmalı',
             'uygulanmaz': 'uygulanmaz'}
UNITS = ('gun', 'hafta', 'ay', 'yil')
MAX_DECISIONS = 8
MAX_TEXT = 1000  # kısa alan sınırı; tam karar metni veya uzun pasaj kataloğa girmez
NO_TOOL = 'yok'
COMMAND_PREFIX = 'python scripts/'
PLACEHOLDER = re.compile(r'<[^<>\s]+>')
VERSION = re.compile(r'\d{4}-\d{2}-\d{2}\.[1-9]\d*')
ISO_DAY = re.compile(r'\d{4}-\d{2}-\d{2}')
HEADING = re.compile(r'(#{1,6})\s+(.*?)\s*#*\s*$')
# Katalog doğrulamasında kuralların seçeneklerle çalıştığını sınamak için örnek girdi.
PROBE_DAY = date(2026, 1, 31)


def canonical(text):
    """Aksan, büyük/küçük harf ve ayraç (boşluk, _, -, /, .) farkını giderir."""
    return re.sub(r'[\s_\-/.]+', '-', pool.normalize(text)).strip('-')


ALIASES = {}
for _key, _names in _ALIAS_SOURCE.items():
    for _name in (_key, *_names):
        ALIASES[canonical(_name)] = _key


def _candidates(sebep):
    """Kısa ad adayları: yazıldığı gibi, kanun öneki atılmış ve fıkrası atılmış biçim."""
    wanted = canonical(sebep)
    candidates = [wanted]
    prefixed = LAW_PREFIX.fullmatch(wanted)
    if prefixed:
        law, bare = prefixed.groups()
        if (law == 'iik') == (bare in IIK_ARTICLES):
            candidates.append(bare)
    article, _, paragraph = candidates[-1].partition('-')
    if paragraph.isdigit() and 1 <= int(paragraph) <= PARAGRAPHS.get(article, 0):
        candidates.append(article)
    return candidates


def resolve(sebep, keys=GROUNDS):
    """Sebebi katalog anahtarına çevirir; bulunamazsa None."""
    if sebep in keys:
        return sebep
    for candidate in _candidates(sebep):
        for key in keys:
            if canonical(key) == candidate:
                return key
        if ALIASES.get(candidate) in keys:
            return ALIASES[candidate]
    return None


def slug(heading):
    """GitHub başlık bağlantısı; validate.py heading_slugs ile aynı kural (tekrar eki hariç)."""
    return re.sub(r'[^\w\- ]', '', heading.strip().lower()).replace(' ', '-')


def guide_link(heading):
    return f'{GUIDE}#{slug(heading)}'


def _unique_object(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f'Yinelenen JSON alanı: {key!r}')
        seen[key] = value
    return seen


def read_catalog(root=ROOT):
    """Kataloğu okur; dosya yoksa OSError, JSON bozuksa ValueError verir."""
    path = Path(root) / CATALOG
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=_unique_object)
    except json.JSONDecodeError as exc:
        raise ValueError(f'{CATALOG}: geçersiz JSON ({exc.msg}, satır {exc.lineno})') from None


def _text(value, limit=MAX_TEXT):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= limit


def _member(value, allowed):
    """Değer izinli metin anahtarlarından biri mi; liste veya nesne TypeError doğurmaz."""
    return isinstance(value, str) and value in allowed


def _iso_day(value):
    if not (isinstance(value, str) and ISO_DAY.fullmatch(value)):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def deadline_call(args):
    """deadlines.py argümanlarını (kural, yer tutucu tarih, seçenekler) çözer.
    (kural, seçenekler) döner; seçeneklerde --count yer tutucuysa değeri metin olarak kalır."""
    if len(args) < 2:
        raise ValueError('deadlines.py komutu kural ve <yer-tutucu> tarih içermeli')
    rule, when, *rest = args
    if rule not in deadlines.RULES:
        raise ValueError(f'deadlines.py kuralı bilinmiyor: {rule}')
    if not PLACEHOLDER.fullmatch(when):
        raise ValueError(f'tarih açılı ayraçlı yer tutucu olmalı (ör. <sozlesme-sonu>): {when}')
    options, index = {}, 0
    while index < len(rest):
        flag = rest[index]
        name = {'--count': 'count', '--unit': 'unit', '--geri': 'backward'}.get(flag)
        if name is None:
            raise ValueError(f'deadlines.py için bilinmeyen seçenek: {flag}')
        if name in options:
            raise ValueError(f'{flag} iki kez verilmiş')
        if name == 'backward':
            options[name] = True
            index += 1
            continue
        if index + 1 >= len(rest):
            raise ValueError(f'{flag} değeri eksik')
        value = rest[index + 1]
        if name == 'count':
            if PLACEHOLDER.fullmatch(value):
                options[name] = value
            elif re.fullmatch(r'[1-9][0-9]*', value):
                options[name] = int(value)
            else:
                raise ValueError(f'--count pozitif tam sayı veya <yer-tutucu> olmalı: {value}')
        else:
            if value not in UNITS:
                raise ValueError(f'--unit {"/".join(UNITS)} olmalı: {value}')
            options[name] = value
        index += 2
    if rule == 'takvim':
        if 'count' not in options or 'unit' not in options:
            raise ValueError('takvim komutu --count ve --unit içermeli')
    elif options:
        raise ValueError('--count/--unit/--geri yalnız takvim kuralında kullanılabilir')
    return rule, options


def command_problems(command, rule):
    """Süre komutunun biçim sorunları; boş liste geçerli demektir."""
    if command == NO_TOOL:
        return [] if rule is None else [f"rule {rule!r} verildiğinde komut '{NO_TOOL}' olamaz"]
    if not command.startswith(COMMAND_PREFIX):
        return [f"'{NO_TOOL}' veya '{COMMAND_PREFIX}…' ile başlamalı: {command}"]
    if any(sep in command for sep in (';', '&&', '||', '|', '\n')):
        return ['tek komut olmalı; ;, &&, || veya | kullanma (ek hesabı formula alanına yaz)']
    tokens = command.split()
    script = tokens[1][len('scripts/'):]
    if not script.endswith('.py') or '/' in script or '\\' in script or not (SCRIPTS / script).is_file():
        return [f'betik yok: scripts/{script}']
    if script != 'deadlines.py':
        if rule is not None:
            return [f'rule {rule!r} verildiğinde komut python scripts/deadlines.py {rule} … olmalı']
        return []
    try:
        called, _ = deadline_call(tokens[2:])
    except ValueError as exc:
        return [str(exc)]
    if called != rule:
        return [f'komut deadlines.py {called} kuralını çağırıyor; rule alanı {called!r} olmalı '
                f'(şu an {rule!r})']
    return []


@functools.lru_cache(maxsize=None)
def _help_output(script, subcommand):
    """Betiğin (alt komutunun) --help çıktısı: (çıkış kodu, metin). Süreç başına bir kez çalışır."""
    args = [sys.executable, str(SCRIPTS / script), *([subcommand] if subcommand else []), '--help']
    # Python 3.14 argparse renkli yardım basabilir; renk kodları seçenek aramasını bozmasın.
    env = {name: value for name, value in os.environ.items() if name != 'FORCE_COLOR'}
    env.update(PYTHONIOENCODING='utf-8', COLUMNS='200', NO_COLOR='1', PYTHON_COLORS='0')
    try:
        proc = subprocess.run(args, capture_output=True, timeout=60, env=env, cwd=str(ROOT))
    except (OSError, subprocess.SubprocessError) as exc:
        return None, str(exc)
    return proc.returncode, proc.stdout.decode('utf-8', errors='replace')


def probe_command(command):
    """deadlines.py dışındaki komutun alt komutunu ve seçeneklerini betiğin --help çıktısıyla sınar.
    Biçimi command_problems ile geçerli komut beklenir; boş liste geçerli demektir."""
    tokens = command.split()
    script, args = tokens[1][len('scripts/'):], tokens[2:]
    subcommand = None
    if args and not args[0].startswith('-') and not PLACEHOLDER.fullmatch(args[0]):
        subcommand = args[0]
    shown = ' '.join(['python', tokens[1], *([subcommand] if subcommand else []), '--help'])
    code, text = _help_output(script, subcommand)
    if code != 0:
        return [f'{shown} çalışmadı (çıkış {code}); alt komutu denetle']
    problems = []
    for flag in (token.split('=', 1)[0] for token in args if token.startswith('--')):
        if not re.search(rf'(?<![\w-]){re.escape(flag)}(?![\w-])', text):
            problems.append(f'{flag} seçeneği {shown} çıktısında yok')
    return problems


def _check_keys(item, expected, where, need):
    present = set(item)
    missing = [k for k in expected if k not in present]
    extra = sorted(present - set(expected))
    need(not missing and not extra,
         f'{where}: alanlar uyuşmuyor (eksik: {missing or "-"}; fazla: {extra or "-"})')


def _check_texts(item, fields, where, need):
    for field in fields:
        if field in item:
            need(_text(item[field]),
                 f'{where}.{field}: boş olmayan, en çok {MAX_TEXT} karakterlik metin olmalı')


def _check_list(value, where, need, minimum=1):
    if not need(isinstance(value, list) and len(value) >= minimum,
                f'{where}: en az {minimum} öğeli liste olmalı'):
        return []
    return value


def _check_deadline(item, where, need):
    _check_keys(item, DEADLINE_KEYS, where, need)
    _check_texts(item, DEADLINE_TEXT, where, need)
    rule = item.get('rule')
    rule_ok = need(rule is None or (isinstance(rule, str) and rule in deadlines.RULES),
                   f'{where}.rule: null veya deadlines.py kuralı ({", ".join(deadlines.RULES)}) '
                   f'olmalı: {rule!r}')
    need(_member(item.get('confidence'), CONFIDENCE),
         f'{where}.confidence: {"/".join(CONFIDENCE)} olmalı: {item.get("confidence")!r}')
    command = item.get('command')
    if rule_ok and _text(command):
        for problem in command_problems(command, rule):
            need(False, f'{where}.command: {problem}')


def _check_route(item, where, need):
    _check_keys(item, ROUTE_KEYS, where, need)
    _check_texts(item, ROUTE_TEXT, where, need)
    need(_member(item.get('arabuluculuk'), MEDIATION),
         f'{where}.arabuluculuk: {"/".join(MEDIATION)} olmalı: {item.get("arabuluculuk")!r}')


def _check_decision(item, where, need):
    _check_keys(item, DECISION_KEYS, where, need)
    _check_texts(item, DECISION_KEYS, where, need)
    quote = item.get('quote')
    if isinstance(quote, str):
        need(len(quote.strip()) >= pool.QUOTE_MIN_LENGTH,
             f'{where}.quote: en az {pool.QUOTE_MIN_LENGTH} karakter olmalı')


def _check_entry(entry, where, need):
    _check_keys(entry, ENTRY_KEYS, where, need)
    _check_texts(entry, ENTRY_TEXT, where, need)
    heading = entry.get('guide_heading')
    if _text(heading):
        need('İ' not in heading and '\n' not in heading and not heading.startswith('#'),
             f'{where}.guide_heading: tek satır olmalı, # ve büyük "İ" içermemeli')
    for field in ENTRY_LISTS:
        if field in entry:
            for index, value in enumerate(_check_list(entry[field], f'{where}.{field}', need)):
                need(_text(value), f'{where}.{field}[{index}]: boş olmayan, en çok {MAX_TEXT} '
                                   'karakterlik metin olmalı')
    for field, check in (('deadlines', _check_deadline), ('routes', _check_route)):
        if field in entry:
            for index, item in enumerate(_check_list(entry[field], f'{where}.{field}', need)):
                label = f'{where}.{field}[{index}]'
                if need(isinstance(item, dict), f'{label}: nesne olmalı'):
                    check(item, label, need)
    deadline_items = entry.get('deadlines')
    names = [item['name'] for item in (deadline_items if isinstance(deadline_items, list) else [])
             if isinstance(item, dict) and _text(item.get('name'))]
    repeated = sorted({name for name in names if names.count(name) > 1})
    need(not repeated, f'{where}.deadlines: aynı ad iki kez: {", ".join(repeated)}')
    if 'decisions' in entry:
        decisions = _check_list(entry['decisions'], f'{where}.decisions', need)
        need(len(decisions) <= MAX_DECISIONS, f'{where}.decisions: en çok {MAX_DECISIONS} karar')
        ids = []
        for index, item in enumerate(decisions):
            label = f'{where}.decisions[{index}]'
            if need(isinstance(item, dict), f'{label}: nesne olmalı'):
                _check_decision(item, label, need)
                ids.append(item.get('document_id'))
        repeated = sorted({str(i) for i in ids if ids.count(i) > 1})
        need(not repeated, f'{where}.decisions: aynı karar iki kez: {", ".join(repeated)}')


def _collector():
    errors = []

    def need(condition, message):
        if not condition:
            errors.append(message)
        return bool(condition)
    return errors, need


def _entries(catalog):
    grounds = catalog.get('grounds') if isinstance(catalog, dict) else None
    return [e for e in grounds if isinstance(e, dict)] if isinstance(grounds, list) else []


def _label(entry, index):
    key = entry.get('key')
    return key if isinstance(key, str) and key else f'grounds[{index}]'


def check_structure(catalog):
    """Şema, tür, zorunlu alan, tekillik ve sabit değer denetimi; hata iletileri listesi döner."""
    errors, need = _collector()
    if not need(isinstance(catalog, dict), 'Katalog bir JSON nesnesi olmalı'):
        return errors
    _check_keys(catalog, TOP_KEYS, 'katalog', need)
    # bool int alt türüdür ve 1.0 == 1'dir; şema sürümü tam sayı olarak yazılmalı.
    need(type(catalog.get('schema_version')) is int and catalog['schema_version'] == SCHEMA_VERSION,
         f'schema_version {SCHEMA_VERSION} olmalı: {catalog.get("schema_version")!r}')
    version = catalog.get('version')
    need(isinstance(version, str) and VERSION.fullmatch(version)
         and _iso_day(version.split('.')[0]), f'version YYYY-AA-GG.N olmalı: {version!r}')
    need(_iso_day(catalog.get('checked_on')),
         f'checked_on YYYY-AA-GG olmalı: {catalog.get("checked_on")!r}')
    need(_text(catalog.get('note')), 'note boş olmayan metin olmalı')
    grounds = catalog.get('grounds')
    if not need(isinstance(grounds, list) and grounds, 'grounds boş olmayan liste olmalı'):
        return errors
    keys, headings = [], []
    for index, entry in enumerate(grounds):
        if not need(isinstance(entry, dict), f'grounds[{index}]: nesne olmalı'):
            continue
        where = _label(entry, index)
        _check_entry(entry, where, need)
        if _text(entry.get('key')):
            keys.append(entry['key'])
        if _text(entry.get('guide_heading')):
            headings.append(entry['guide_heading'].strip())
    repeated = sorted({k for k in keys if keys.count(k) > 1})
    need(not repeated, f'Yinelenen sebep anahtarı: {", ".join(repeated)}')
    missing = [k for k in GROUNDS if k not in keys]
    need(not missing, f'Eksik sebep: {", ".join(missing)}')
    unknown = sorted({k for k in keys if k not in GROUNDS})
    need(not unknown, f'Bilinmeyen sebep anahtarı: {", ".join(unknown)} '
                      f'(geçerli: {", ".join(GROUNDS)})')
    repeated = sorted({h for h in headings if headings.count(h) > 1})
    need(not repeated, f'Aynı guide_heading birden çok sebepte: {", ".join(repeated)}')
    return errors


def document_headings(text):
    """Kod blokları dışındaki (düzey, başlık) çiftleri; validate.py heading_slugs ile aynı tarama."""
    found, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith('```'):
            fenced = not fenced
            continue
        match = None if fenced else HEADING.match(line)
        if match:
            found.append((len(match.group(1)), match.group(2).strip()))
    return found


def check_guide(catalog, root=ROOT):
    """Her guide_heading rehberde tam bir kez '## ' başlığı olmalı ve bağlantısı tekil olmalı."""
    errors, need = _collector()
    path = Path(root) / GUIDE
    try:
        text = path.read_text(encoding='utf-8-sig')
    except FileNotFoundError:
        return [f'{GUIDE} bulunamadı; guide_heading başlıkları denetlenemedi']
    except (OSError, UnicodeDecodeError) as exc:
        return [f'{GUIDE} okunamadı ({exc}); guide_heading başlıkları denetlenemedi']
    headings = document_headings(text)
    level2 = [title for level, title in headings if level == 2]
    slugs = [slug(title) for _, title in headings]
    for index, entry in enumerate(_entries(catalog)):
        heading = entry.get('guide_heading')
        if not _text(heading):
            continue
        where = _label(entry, index)
        count = level2.count(heading.strip())
        if need(count == 1, f'{where}.guide_heading: {GUIDE} içinde "## {heading}" satırı '
                            f'{"yok" if not count else f"{count} kez var"}'):
            need(slugs.count(slug(heading)) == 1,
                 f'{where}.guide_heading: #{slug(heading)} bağlantısı rehberde tekil değil')
    return errors


def _gg_aa_yyyy(iso):
    return '.'.join(reversed(iso.split('-'))) if iso else None


def kunye_problems(kunye, row):
    """Katalog künyesini havuz kaydının mahkeme, E., K. ve tarih bilgisiyle karşılaştırır."""
    problems = []
    court = pool.kunye(row).split(', E. ')[0]
    if not kunye.startswith(court + ','):
        problems.append(f'mahkeme "{court}" ile başlamalı')
    for label, value in (('E.', row.get('esas_no')), ('K.', row.get('karar_no'))):
        if value and not re.search(rf'{re.escape(label)} {re.escape(str(value))}(?![\d/])', kunye):
            problems.append(f'"{label} {value}" içermeli')
    days = {_gg_aa_yyyy(row.get('karar_tarihi')), _gg_aa_yyyy(pool.text_decision_date(row))} - {None}
    if days and not any(day in kunye for day in days):
        problems.append(f'karar tarihi ({" veya ".join(sorted(days))}) içermeli')
    return problems


def check_sources(catalog, rows):
    """Her kararın havuzda bulunduğunu, künyesini ve alıntının metinde birebir geçtiğini denetler."""
    errors, need = _collector()
    by_id = {str(row['document_id']): row for row in rows}
    for index, entry in enumerate(_entries(catalog)):
        decisions = entry.get('decisions')
        for number, item in enumerate(decisions if isinstance(decisions, list) else []):
            if not isinstance(item, dict) or not isinstance(item.get('document_id'), str):
                continue
            where = f'{_label(entry, index)}.decisions[{number}]'
            row = by_id.get(item['document_id'])
            if not need(row is not None, f'{where}: karar havuzda yok: {item["document_id"]}'):
                continue
            need(not row.get('out_of_scope'),
                 f'{where}: kayıt kapsam dışı işaretli (python scripts/pool.py get {item["document_id"]})')
            quote = item.get('quote')
            if isinstance(quote, str) and quote.strip():
                count, _ = pool.find_quotes(row['text'], quote)
                need(count > 0, f'{where}.quote: karar metninde birebir bulunamadı '
                                f'(python scripts/pool.py quote {item["document_id"]} -- "…")')
            if isinstance(item.get('kunye'), str):
                for problem in kunye_problems(item['kunye'], row):
                    need(False, f'{where}.kunye: {problem} (havuz: {row["kunye"]})')
    return errors


def schedule(entry, start):
    """Kuralı olan her süre için deadlines.calculate sonucunu üretir (aynı girdi tarihiyle).
    Aynı komutu (aynı kural, yer tutucu ve seçenekler) paylaşan sonraki satırda sonuç tekrarlanmaz:
    sonuc null, sonuc_ayni hesaplanan ilk satırın adıdır."""
    items, computed = [], {}
    for item in entry['deadlines']:
        rule = item['rule']
        if rule is None:
            continue
        tokens = item['command'].split()
        _, options = deadline_call(tokens[2:])
        tokens[3] = start.isoformat()
        row = {'name': item['name'], 'sure': item['duration'], 'rule': rule,
               'baslangic_olayi': item['start_event'], 'guven': item['confidence'],
               'komut': ' '.join(tokens)}
        if isinstance(options.get('count'), str):
            row['sonuc'] = None
            row['atlandi'] = (f'Süre miktarı belgeye bağlı ({options["count"]}); komutu --count '
                              'değeriyle ayrı çalıştır.')
        elif item['command'] in computed:
            row['sonuc'] = None
            row['sonuc_ayni'] = computed[item['command']]
        else:
            row['sonuc'] = deadlines.calculate(rule, start, **options)
            computed[item['command']] = item['name']
        items.append(row)
    return items


def schedule_warning(start):
    return (f'Aynı tarih ({_gg_aa_yyyy(start.isoformat())}) bütün kurallara girdi olarak verildi; her '
            'süre kendi başlangıç olayından (baslangic_olayi) işler ve her kuralın girdi anlamı '
            'sonuc.meaning alanında yazılıdır. Bu tarih çoğu kural için doğru girdi değildir: her süreyi '
            'belgeden belirlediğin kendi başlangıç tarihiyle ayrı çağır (komut alanı). Aynı komutu '
            'paylaşan satırın sonucu bir kez verilir (sonuc_ayni). Ham takvim adayıdır; tatil, adli tatil, '
            'arabuluculuk durması ve TBK 353 uzaması uygulanmadı. Güveni orta veya düşük süreleri ve İİK, '
            'HMK, HUAK veya TMK dayanaklı süreleri resmî metinden ve güncel içtihattan doğrula; her '
            'kuralın kontrolleri sonuc.pending_checks (metinde "Kontrol") satırlarındadır.')


def validate(root=ROOT, pool_dir=None):
    """Kataloğu yapı, rehber başlıkları ve karar havuzuyla doğrular; rapor sözlüğü döner."""
    root = Path(root)
    try:
        catalog = read_catalog(root)
    except FileNotFoundError:
        return {'ok': False, 'errors': [f'{CATALOG} bulunamadı']}
    except (OSError, ValueError) as exc:
        return {'ok': False, 'errors': [f'{CATALOG} okunamadı: {exc}']}
    errors = check_structure(catalog)
    if not errors:
        # Kural ve seçenekler deadlines.py ile gerçekten çalışmalı (ör. kural adı değişirse).
        for entry in catalog['grounds']:
            try:
                schedule(entry, PROBE_DAY)
            except (ValueError, OverflowError, TypeError) as exc:
                errors.append(f'{entry["key"]}: deadlines.py hesabı çalışmadı: {exc}')
            # Diğer betik komutlarının alt komutu ve seçenekleri betiğin --help çıktısında olmalı.
            for index, item in enumerate(entry['deadlines']):
                if item['rule'] is None and item['command'] != NO_TOOL:
                    errors += [f'{entry["key"]}.deadlines[{index}].command: {problem}'
                               for problem in probe_command(item['command'])]
    errors += check_guide(catalog, root)
    try:
        rows, _ = pool.load_pool(Path(pool_dir) if pool_dir else root / 'data')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'Karar havuzu okunamadı: {exc}')
    else:
        errors += check_sources(catalog, rows)
    if errors:
        return {'ok': False, 'errors': errors}
    grounds = catalog['grounds']
    return {'ok': True, 'grounds': len(grounds),
            'decisions': sum(len(e['decisions']) for e in grounds),
            'deadlines': sum(len(e['deadlines']) for e in grounds)}


def load_catalog(root=ROOT):
    """Kataloğu okur ve yapısını doğrular; hata varsa ValueError (rapor için: validate)."""
    catalog = read_catalog(root)
    errors = check_structure(catalog)
    if errors:
        shown = '; '.join(errors[:5]) + (f' (+{len(errors) - 5} hata)' if len(errors) > 5 else '')
        raise ValueError(f'{CATALOG} yapısı geçersiz: {shown}. Ayrıntı: python scripts/tahliye.py validate')
    return catalog


def route_card(entry, catalog):
    card = {}
    for field, value in entry.items():
        card[field] = value
        if field == 'guide_heading':
            card['rehber'] = guide_link(value)
    card['katalog_surumu'] = catalog['version']
    return card


def render_text(card):
    """Rota kartının kısa Türkçe metin görünümü."""
    lines = [f"{card['title']} [{card['key']}]",
             f"Rehber: {card['rehber']}",
             f"Dayanak: {'; '.join(card['legal_basis'])}",
             f"Kim isteyebilir: {card['requester']}",
             f"Kapsam: {card['scope']}",
             f"Bildirim: {card['notice']}"]

    def bullets(title, values):
        lines.extend(['', f'{title}:'] + [f'- {value}' for value in values])

    bullets('Ön koşullar', card['preconditions'])
    lines.extend(['', 'Süreler:'])
    for item in card['deadlines']:
        tool = item['command'] if item['command'] != NO_TOOL else 'araç yok'
        lines.extend([f"- {item['name']} ({item['duration']}; güven: {CONFIDENCE[item['confidence']]})",
                      f"  Başlangıç: {item['start_event']}",
                      f"  Hesap: {item['formula']}",
                      f"  Araç: {tool}",
                      f"  Dayanak: {item['basis']}"])
    lines.extend(['', 'Yollar:'])
    for item in card['routes']:
        lines.extend([f"- {item['route']} — {item['forum']}",
                      f"  Arabuluculuk: {MEDIATION[item['arabuluculuk']]}; {item['arabuluculuk_note']}",
                      f"  Usul: {item['procedure']}"])
    bullets('Kiracı savunmaları', card['tenant_defenses'])
    bullets('Tuzaklar', card['pitfalls'])
    lines.extend(['', 'Emsal kararlar:'])
    for item in card['decisions']:
        lines.extend([f"- {item['kunye']} — {item['outcome']}",
                      f"  Karar: {item['holding']}",
                      f"  Alıntı: “{item['quote']}”",
                      f"  Sınır: {item['caveat']}",
                      f"  Tam metin: python scripts/pool.py get {item['document_id']}"])
    bullets('Açık sorular', card['open_questions'])
    if 'takvim' in card:
        lines.extend(['', f"Ham takvim adayı (girdi {_gg_aa_yyyy(card['tarih'])}):", card['uyari']])
        for item in card['takvim']:
            head = (f"- {item['name']} ({item['sure']}) "
                    f"[{item['rule']}; güven: {CONFIDENCE[item['guven']]}]")
            if 'sonuc_ayni' in item:
                lines.append(f"{head}: sonuç “{item['sonuc_ayni']}” satırındadır (aynı komut).")
            elif item['sonuc'] is None:
                lines.append(f"{head}: hesaplanmadı. {item['atlandi']}")
            else:
                result = item['sonuc']
                shown = ', '.join(f'{name} {_gg_aa_yyyy(value)}'
                                  for name, value in result['raw_dates'].items())
                lines.extend([f'{head}: {shown}', f"  Girdinin anlamı: {result['meaning']}",
                              f"  Araç dayanağı: {result['basis']}"])
                lines.extend(f'  Kontrol: {check}' for check in result['pending_checks'])
            lines.append(f"  Ayrı çağır: {item['komut']}")
    lines.extend(['', f"Katalog sürümü: {card['katalog_surumu']}"])
    return '\n'.join(lines) + '\n'


class Parser(argparse.ArgumentParser):
    """Kullanım hatalarını Türkçe "HATA:" önekiyle ve 2 çıkış koduyla bildirir."""

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(EXIT_USAGE, f'HATA: {message}\n')


def build_parser():
    root_help = 'Skill kökü (varsayılan: bu betiğin üst klasörü); katalog ve rehber buradan okunur'
    parser = Parser(description=__doc__, epilog=EPILOG,
                    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=ROOT, help=root_help)
    # --root alt komuttan sonra da yazılabilir; verilmezse üst ayrıştırıcının değeri korunur.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--root', type=Path, default=argparse.SUPPRESS, help=root_help)
    sebep_help = ('Sebep anahtarı veya kısa adı (ör. temerrut, ihtiyaç, TBK 316/2, İİK 269, 352/2, '
                  'yeni malik); liste için: python scripts/tahliye.py list')
    sub = parser.add_subparsers(dest='command', required=True, parser_class=Parser)
    sub.add_parser('list', parents=[common], help='Sebepleri, dayanaklarını ve rehber bağlantısını listeler')
    yol = sub.add_parser('yol', parents=[common], help='Sebebin rota kartı (koşullar, süreler, yollar, emsaller)')
    yol.add_argument('sebep', help=sebep_help)
    yol.add_argument('--tarih', type=deadlines._arg_date,
                     help='YYYY-AA-GG, GG.AA.YYYY veya GG/AA/YYYY; kuralı olan her süreye aynı tarih '
                          'girdi olarak verilir (ham takvim adayı; her süreyi ayrıca kendi tarihiyle hesapla)')
    yol.add_argument('--metin', action='store_true', help='JSON yerine kısa Türkçe metin bas')
    emsal = sub.add_parser('emsal', parents=[common], help='Sebebin doğrulanmış emsal kararları ve tam metin komutu')
    emsal.add_argument('sebep', help=sebep_help)
    check = sub.add_parser('validate', parents=[common],
                           help='Kataloğu şema, rehber başlıkları ve karar havuzuyla doğrular')
    check.add_argument('--havuz', type=Path,
                       help='Karar havuzu klasörü (varsayılan: <root>/data)')
    return parser


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == 'validate':
        report = validate(args.root, args.havuz)
        emit(report)
        return EXIT_OK if report['ok'] else EXIT_DATA
    key = None
    if args.command in ('yol', 'emsal'):
        # Girdi hatası katalog okunmadan bildirilir.
        key = resolve(args.sebep)
        if key is None:
            print(f'HATA: Bilinmeyen tahliye sebebi: {args.sebep!r}. Geçerli anahtarlar: '
                  f'{", ".join(GROUNDS)}. Kısa adlar da kabul edilir (ör. temerrüt, TBK 316/2, '
                  'İİK 269, 352/2, yeni malik, 10yil, tehir); 352 için fıkrayı yaz (352/1, 352/2, '
                  '352/3).', file=sys.stderr)
            return EXIT_NOT_FOUND
    catalog = load_catalog(args.root)
    if args.command == 'list':
        emit({'version': catalog['version'], 'checked_on': catalog['checked_on'],
              'note': catalog['note'],
              'grounds': [{'key': e['key'], 'title': e['title'], 'legal_basis': e['legal_basis'],
                           'rehber': guide_link(e['guide_heading'])} for e in catalog['grounds']]})
        return EXIT_OK
    entry = next(e for e in catalog['grounds'] if e['key'] == key)
    if args.command == 'emsal':
        emit({'key': key, 'title': entry['title'],
              'decisions': [{**d, 'komut': f'python scripts/pool.py get {d["document_id"]}'}
                            for d in entry['decisions']]})
        return EXIT_OK
    card = route_card(entry, catalog)
    if args.tarih is not None:
        try:
            plan = schedule(entry, args.tarih)
        except (ValueError, OverflowError) as exc:
            print(f'HATA: --tarih {args.tarih.isoformat()} ile süre hesaplanamadı: {exc}', file=sys.stderr)
            return EXIT_USAGE
        card.update(tarih=args.tarih.isoformat(), uyari=schedule_warning(args.tarih), takvim=plan)
    if args.metin:
        sys.stdout.write(render_text(card))
    else:
        emit(card)
    return EXIT_OK


if __name__ == '__main__':
    for stream, errors in ((sys.stdout, 'strict'), (sys.stderr, 'backslashreplace')):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors=errors)
    try:
        code = main()
        sys.stdout.flush()
    except BrokenPipeError:
        # Çıktıyı okuyan süreç (ör. `| head`) erken kapandı; veri hatası değildir.
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(EXIT_DATA)
    except FileNotFoundError as exc:
        print(f'HATA: Dosya bulunamadı: {exc.filename}', file=sys.stderr)
        sys.exit(EXIT_DATA)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'HATA: {exc}', file=sys.stderr)
        sys.exit(EXIT_DATA)
    sys.exit(code)
