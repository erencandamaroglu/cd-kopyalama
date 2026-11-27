"""Veri klasörü ve ayar dosyası.

Veriler %USERPROFILE%\\CdKopyalama altında durur (proje klasörü ağ diskinde; AppData değil çünkü
Microsoft Store Python AppData yazmalarını sanallaştırıyor). CDKOPYA_VERI ortam değişkeni klasörü değiştirir.
"""
import json
import os
import shutil
from pathlib import Path

# abspath: sürücü harfli yol (Y:\...) kalır; resolve() UNC yolu verir, cmd UNC klasörüne geçemez
PROJE = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
IKON = PROJE / "varliklar" / "ikon.ico"  # tools/ikon_olustur.py üretir


def veri_klasoru():
    yol = Path(os.environ.get("CDKOPYA_VERI") or Path.home() / "CdKopyalama")
    yol.mkdir(parents=True, exist_ok=True)
    return yol


def yerel_ikon():
    """İkonun yerel diskteki kopyası (veri klasörü/ikon.ico); değiştiyse yenilenir. Explorer ve görev çubuğu
    ağ sürücüsündeki ikonu her zaman okuyamıyor."""
    hedef = veri_klasoru() / "ikon.ico"
    try:
        if not hedef.exists() or hedef.read_bytes() != IKON.read_bytes():
            shutil.copyfile(IKON, hedef)
    except OSError:
        return IKON
    return hedef


def ayar_oku():
    try:
        veri = json.loads((veri_klasoru() / "ayarlar.json").read_text(encoding="utf-8"))
        return veri if isinstance(veri, dict) else {}
    except (OSError, ValueError):
        return {}


def ayar_yaz(**degerler):
    ayarlar = ayar_oku()
    ayarlar.update(degerler)
    (veri_klasoru() / "ayarlar.json").write_text(
        json.dumps(ayarlar, ensure_ascii=False, indent=2), encoding="utf-8")
