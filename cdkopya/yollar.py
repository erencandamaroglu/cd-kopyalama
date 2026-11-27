"""Veri klasörü ve ayar dosyası.

Veriler %USERPROFILE%\\CdKopyalama altında durur (proje klasörü ağ diskinde; AppData değil çünkü
Microsoft Store Python AppData yazmalarını sanallaştırıyor). CDKOPYA_VERI ortam değişkeni klasörü değiştirir.
"""
import json
import os
from pathlib import Path


def veri_klasoru():
    yol = Path(os.environ.get("CDKOPYA_VERI") or Path.home() / "CdKopyalama")
    yol.mkdir(parents=True, exist_ok=True)
    return yol


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
