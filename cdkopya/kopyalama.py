"""Disk içeriğini hedef klasöre kopyalama (arayüzden bağımsız)."""
import os
import re
import shutil
import time
from collections import deque
from datetime import datetime
from pathlib import Path

PARCA = 1024 * 1024  # 1 MB


class SureTahmini:
    """Son PENCERE_SN saniyedeki hızdan kalan süreyi tahmin eder.

    CD okuma hızı diskin içinden dışına doğru değişir ve okunamayan bölgelerde düşer; baştan beri ortalama yerine
    kayan pencere kullanılır. İlk EN_AZ_SN saniye tahmin verilmez (disk dönmeye başlarken hız yanıltıcı).
    """

    PENCERE_SN = 15
    EN_AZ_SN = 3

    def __init__(self, saat=time.monotonic):
        self.saat = saat
        self.baslangic = saat()
        self.ornekler = deque()

    def guncelle(self, tamam, toplam):
        """(kalan saniye ya da None, bayt/sn hız ya da None)."""
        simdi = self.saat()
        self.ornekler.append((simdi, tamam))
        while len(self.ornekler) > 2 and simdi - self.ornekler[1][0] >= self.PENCERE_SN:
            self.ornekler.popleft()
        ilk_zaman, ilk_bayt = self.ornekler[0]
        aralik = simdi - ilk_zaman
        if simdi - self.baslangic < self.EN_AZ_SN or aralik <= 0 or tamam <= ilk_bayt:
            return None, None
        hiz = (tamam - ilk_bayt) / aralik
        return max(0.0, (toplam - tamam) / hiz), hiz

    def gecen(self):
        return self.saat() - self.baslangic


def sure_metni(saniye):
    """Okunaklı süre: '45 sn', '3 dk 20 sn', '1 sa 05 dk'. Bir dakikadan uzunsa 10 sn'ye yuvarlanır (titremesin)."""
    saniye = int(round(saniye))
    if saniye < 60:
        return f"{saniye} sn"
    saniye = int(round(saniye / 10) * 10)
    sa, kalan = divmod(saniye, 3600)
    dk, sn = divmod(kalan, 60)
    if sa:
        return f"{sa} sa {dk:02d} dk"
    return f"{dk} dk {sn:02d} sn" if sn else f"{dk} dk"


def boyut_metni(bayt):
    """'734 MB', '4,2 GB' (Türkçe ondalık virgül)."""
    for birim, bolen in (("GB", 1024 ** 3), ("MB", 1024 ** 2), ("KB", 1024)):
        if bayt >= bolen:
            deger = bayt / bolen
            metin = f"{deger:.1f}" if deger < 10 else f"{deger:.0f}"
            return f"{metin.replace('.', ',')} {birim}"
    return f"{bayt} B"


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
    """(hedef klasör, dosya sayısı, hata listesi, toplam bayt) döndürür.

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
    return hedef, sayi, hatalar, toplam
