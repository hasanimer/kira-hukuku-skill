"""Verify and save an unsigned UDF returned by Legaluga; no drafting, no network."""
import argparse
import base64
import binascii
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile
import zlib

YEDEK = 'https://mcp.legaluga.com/udf-dilekce'
# Zip bombasına karşı yerel üst sınır; sunucunun içerik sınırının kopyası değildir.
ICERIK_SINIRI = 2_000_000
NOT = 'İmzasız UDF taslağı; UYAP kabulü ve e-imza garanti edilmez.'


class UdfError(ValueError):
    """Bütünlük sorunu; dosya yazılmaz."""


def decode_text(raw):
    """PowerShell yönlendirmesi UTF-16 BOM'lu metin üretebilir."""
    try:
        if raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
            return raw.decode('utf-16')
        return raw.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise UdfError(f'Girdi metin olarak okunamadı: {exc}') from None


def check(raw, sha256_hex, target):
    """Yazmadan önce uzantı, base64, SHA-256, zip ve yer tutucu denetimi."""
    if Path(target).suffix.lower() != '.udf':
        raise UdfError('Hedef dosyanın uzantısı .udf olmalı')
    try:
        data = base64.b64decode(''.join(decode_text(raw).split()), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise UdfError(f'Geçersiz base64: {exc}') from None
    digest = hashlib.sha256(data).hexdigest()
    if digest != sha256_hex.strip().lower():
        raise UdfError('SHA-256 tutmadı; veri eksik veya hatalı kopyalanmış olabilir')
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            names = archive.namelist()
            if 'content.xml' not in names:
                raise UdfError('UDF içinde content.xml yok')
            # Sonuna kadar okumak CRC denetimini de çalıştırır.
            with archive.open('content.xml') as handle:
                content = handle.read(ICERIK_SINIRI + 1)
    except (zipfile.BadZipFile, zlib.error, EOFError, RuntimeError, NotImplementedError) as exc:
        raise UdfError(f'Geçerli UDF/zip değil: {exc}') from None
    if len(content) > ICERIK_SINIRI:
        raise UdfError('content.xml yerel boyut sınırını aşıyor')
    if '[DOLDURULACAK' in content.decode('utf-8', errors='replace'):
        raise UdfError('Taslakta [DOLDURULACAK] alanı kaldı; önce doldurulup kullanıcıca onaylanmalı')
    return data, digest, names


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    save = sub.add_parser('kaydet', help='dosya_base64 alanını çöz, doğrula ve .udf olarak yaz')
    save.add_argument('girdi', help="base64 metni içeren dosya; stdin için '-'")
    save.add_argument('--sha256', required=True, help='Araç yanıtındaki sha256 değeri')
    save.add_argument('--cikti', type=Path, required=True,
                      help='Yazılacak .udf yolu; var olan dosyanın üzerine yazılmaz')
    args = parser.parse_args()
    raw = sys.stdin.buffer.read() if args.girdi == '-' else Path(args.girdi).read_bytes()
    try:
        data, digest, names = check(raw, args.sha256, args.cikti)
    except UdfError as exc:
        emit({'kaydedildi': False, 'sorun': str(exc), 'yedek': YEDEK})
        return 2
    with args.cikti.open('xb') as handle:
        handle.write(data)
    emit({'kaydedildi': True, 'dosya': str(args.cikti.resolve()), 'bayt': len(data),
          'sha256': digest, 'zip_icerik': names, 'not': NOT})
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except OSError as exc:
        print(f'UDF kayıt hatası: {exc}', file=sys.stderr)
        sys.exit(1)
