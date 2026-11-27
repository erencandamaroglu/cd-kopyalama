"""Kopyalama mantığı ve sahte sürücüyle izleme döngüsü testleri (gerçek CD'ye dokunmaz)."""
import os
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path

GECICI = tempfile.mkdtemp(prefix="cdkopya-test-")
os.environ["CDKOPYA_VERI"] = os.path.join(GECICI, "veri")
KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK))

from cdkopya import kopyalama, surucu, yollar  # noqa: E402


def ornek_disk():
    """İç içe klasör, boş klasör, Türkçe adlı ve salt okunur dosya içeren sahte disk."""
    kaynak = Path(tempfile.mkdtemp(dir=GECICI))
    (kaynak / "a" / "bos").mkdir(parents=True)
    (kaynak / "a" / "şarkı.bin").write_bytes(os.urandom(3_500_000))
    (kaynak / "b.txt").write_bytes(b"")
    os.chmod(kaynak / "b.txt", 0o444)
    return kaynak


def hic(*_):
    pass


class KopyalamaTesti(unittest.TestCase):
    def test_icerik_aynen_kopyalanir(self):
        kaynak, hedef_kok = ornek_disk(), Path(GECICI) / "hedef1"
        hedef, sayi, hatalar = kopyalama.diski_kopyala(
            str(kaynak), hedef_kok, "DISK", threading.Event(), hic)
        self.assertEqual((sayi, hatalar), (2, []))
        self.assertEqual((hedef / "a" / "şarkı.bin").read_bytes(),
                         (kaynak / "a" / "şarkı.bin").read_bytes())
        self.assertTrue((hedef / "a" / "bos").is_dir())

    def test_ayni_ad_uzerine_yazilmaz_gecersiz_karakter_temizlenir(self):
        kaynak, hedef_kok = ornek_disk(), Path(GECICI) / "hedef2"
        adlar = [kopyalama.diski_kopyala(str(kaynak), hedef_kok, "TE:ST", threading.Event(), hic)[0].name
                 for _ in range(2)]
        self.assertEqual(adlar, ["TE_ST", "TE_ST (2)"])

    def test_iptal_yarim_dosya_birakmaz(self):
        kaynak, hedef_kok = ornek_disk(), Path(GECICI) / "hedef3"
        dur = threading.Event()

        def ilk_parcada_durdur(*_):
            dur.set()

        with self.assertRaises(kopyalama.Iptal):
            kopyalama.diski_kopyala(str(kaynak), hedef_kok, "X", dur, ilk_parcada_durdur)
        self.assertFalse(any(p.name == "şarkı.bin" for p in hedef_kok.rglob("*")))

    def test_muzik_cd_reddedilir(self):
        kaynak = Path(tempfile.mkdtemp(dir=GECICI))
        (kaynak / "Track01.cda").write_bytes(b"x" * 44)
        with self.assertRaisesRegex(RuntimeError, "müzik"):
            kopyalama.diski_kopyala(str(kaynak), Path(GECICI) / "hedef4", "M", threading.Event(), hic)

    def test_ayar_kaydedilir(self):
        yollar.ayar_yaz(hedef=r"C:\deneme")
        self.assertEqual(yollar.ayar_oku()["hedef"], r"C:\deneme")


class IzlemeTesti(unittest.TestCase):
    def test_takilan_disk_kopyalanir_ve_cikarilir(self):
        """Disk takılır → kopyalanır → çıkarılır; aynı disk yeniden takılınca yeni klasöre kopyalanır."""
        from cdkopya import arayuz

        kaynak, hedef_kok = ornek_disk(), Path(GECICI) / "hedef5"
        takili, cikarilan = {"var": True}, []

        def cikar(harf):
            cikarilan.append(harf)
            takili["var"] = False
            return True

        eski = (surucu.cd_suruculeri, surucu.disk_bilgisi, surucu.diski_cikar, arayuz.diski_kopyala)
        surucu.cd_suruculeri = lambda: ["Q:"]
        surucu.disk_bilgisi = lambda harf: ("DISK", 1) if takili["var"] else None
        surucu.diski_cikar = cikar
        arayuz.diski_kopyala = lambda _k, *a: kopyalama.diski_kopyala(str(kaynak), *a)
        yollar.ayar_yaz(hedef=str(hedef_kok))
        try:
            pencere = arayuz.AnaPencere()
            pencere.after(3000, lambda: takili.update(var=True))
            pencere.after(7000, pencere.kapat)
            pencere.mainloop()
        finally:
            surucu.cd_suruculeri, surucu.disk_bilgisi, surucu.diski_cikar, arayuz.diski_kopyala = eski
        self.assertEqual(cikarilan, ["Q:", "Q:"])
        self.assertEqual(sorted(os.listdir(hedef_kok)), ["DISK", "DISK (2)"])


def tearDownModule():
    for kok, dizinler, dosyalar in os.walk(GECICI):
        for d in dosyalar:
            os.chmod(os.path.join(kok, d), 0o666)
    shutil.rmtree(GECICI, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
