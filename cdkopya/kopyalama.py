"""Disk içeriğini hedef klasöre kopyalama (arayüzden bağımsız)."""
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

PARCA = 1024 * 1024  # 1 MB


class Iptal(Exception):
    """Kullanıcı kopyalamayı durdurdu."""


def hedef_olustur(ana_klasor, etiket):
    """Disk adıyla yeni klasör açar; varsa üzerine yazmaz, numara ekler."""
    ad = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", etiket).strip(" .")
    if not ad:
        ad = "CD_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    Path(ana_klasor).mkdir(parents=True, exist_ok=True)
    n = 1
    while True:
        hedef = Path(ana_klasor) / (ad if n == 1 else f"{ad} ({n})")
        try:
            hedef.mkdir()
            return hedef
        except FileExistsError:
            n += 1


def dosya_kopyala(kaynak, hedef, dur, ilerleme):
    """Parça parça kopyalar; hata ya da iptalde yarım dosya bırakmaz."""
    try:
        with open(kaynak, "rb") as k, open(hedef, "wb") as h:
            while parca := k.read(PARCA):
                if dur.is_set():
                    raise Iptal
                h.write(parca)
                ilerleme(len(parca))
    except BaseException:
        Path(hedef).unlink(missing_ok=True)
        raise
    try:
        st = os.stat(kaynak)
        os.utime(hedef, (st.st_atime, st.st_mtime))
    except OSError:
        pass  # tarih aktarılamazsa dosya yine de sağlamdır


def diski_kopyala(kaynak, ana_klasor, etiket, dur, ilerleme):
    """(hedef klasör, dosya sayısı, hata listesi) döndürür.

    ilerleme(kopyalanan bayt, toplam bayt, dosya adı) çağrılır. Okunamayan dosyalar hata listesine
    yazılır, kalanlar kopyalanır. Kopyalamaya hiç başlanamıyorsa RuntimeError verir.
    """
    hatalar, klasorler, dosyalar, toplam = [], [], [], 0
    for kok, dizinler, adlar in os.walk(kaynak, onerror=lambda e: hatalar.append(str(e))):
        if dur.is_set():
            raise Iptal
        klasorler += [os.path.join(kok, d) for d in dizinler]
        for ad in adlar:
            yol = os.path.join(kok, ad)
            try:
                boyut = os.path.getsize(yol)
            except OSError as e:
                hatalar.append(str(e))
                continue
            dosyalar.append((yol, boyut))
            toplam += boyut

    if not dosyalar:
        raise RuntimeError("Diskte okunabilen dosya yok.")
    if all(y.lower().endswith(".cda") for y, _ in dosyalar):
        raise RuntimeError("Bu bir müzik CD'si; program yalnızca veri disklerini kopyalar.")
    Path(ana_klasor).mkdir(parents=True, exist_ok=True)
    if toplam > shutil.disk_usage(ana_klasor).free:
        raise RuntimeError("Hedefte yeterli boş alan yok.")

    hedef = hedef_olustur(ana_klasor, etiket)
    for d in klasorler:
        (hedef / os.path.relpath(d, kaynak)).mkdir(parents=True, exist_ok=True)

    tamam = sayi = 0
    for yol, boyut in dosyalar:
        goreli = os.path.relpath(yol, kaynak)
        baslangic = tamam

        def ekle(n):
            nonlocal tamam
            tamam += n
            ilerleme(tamam, toplam, goreli)

        try:
            dosya_kopyala(yol, hedef / goreli, dur, ekle)
            sayi += 1
        except OSError as e:
            hatalar.append(f"{goreli}: {e}")
        tamam = baslangic + boyut
    return hedef, sayi, hatalar
