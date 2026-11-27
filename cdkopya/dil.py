"""Arayüz dilleri (Türkçe / İngilizce).

Tüm kullanıcıya görünen metinler buradadır. Seçili dil ayarlarda (`dil`) saklanır; ayar yoksa Windows arayüz
dili Türkçe ise Türkçe, değilse İngilizce açılır. Yeni metin eklerken her iki dile de yazılır (test denetler).
"""
import ctypes

DILLER = {"tr": "Türkçe", "en": "English"}

METINLER = {
    "tr": {
        "baslik": "CD Kopyalayıcı",
        "hedef_etiket": "Kopyalanacak klasör:",
        "sec": "Seç...",
        "iptal": "İptal",
        "baslatiliyor": "Başlatılıyor...",
        "cd_hedef_olamaz": "Hedef olarak CD sürücüsü seçilemez.",
        "ayar_kaydedilemedi": "Ayar kaydedilemedi: {hata}",
        "cikis_onay": "Kopyalama sürüyor. Yine de çıkılsın mı?",
        "surucu_yok": "CD sürücüsü bulunamadı.",
        "klasor_secin": "Önce kopyalanacak klasörü seçin.",
        "bekleniyor": "CD bekleniyor... ({suruculer})",
        "hata": "HATA: {hata}",
        "okunuyor": "{harf} okunuyor...",
        "disk_bulundu": "Disk bulundu: {harf} {etiket}",
        "hesaplaniyor": "kalan süre hesaplanıyor...",
        "kaldi": "~{sure} kaldı ({hiz}/sn)",
        "ilerleme": "%{yuzde} - {sure} - {ad}",
        "hatali_bitti": "{sayi} dosya kopyalandı ({ozet}), {hata_sayisi} hata var. Disk çıkarılmadı. Klasör: {hedef}",
        "tamamlandi": "Tamamlandı: {sayi} dosya ({ozet}) -> {hedef}",
        "cikariliyor": "Disk çıkarılıyor...",
        "cikarildi": "Disk çıkarıldı.",
        "cikarilamadi": "Disk çıkarılamadı, elle çıkarın.",
        "iptal_edildi": "İptal edildi. Kopyalanan dosyalar hedefte kaldı.",
        "hata_cikarilmadi": "HATA: {hata} Disk çıkarılmadı.",
        "bos_disk": "Diskte okunabilen dosya yok.",
        "muzik_cd": "Bu bir müzik CD'si; program yalnızca veri disklerini kopyalar.",
        "yer_yok": "Hedefte yeterli boş alan yok.",
        "sure_sn": "{sn} sn",
        "sure_dk": "{dk} dk",
        "sure_dk_sn": "{dk} dk {sn:02d} sn",
        "sure_sa_dk": "{sa} sa {dk:02d} dk",
        "ondalik": ",",
    },
    "en": {
        "baslik": "CD Copier",
        "hedef_etiket": "Destination folder:",
        "sec": "Browse...",
        "iptal": "Cancel",
        "baslatiliyor": "Starting...",
        "cd_hedef_olamaz": "A CD drive cannot be the destination.",
        "ayar_kaydedilemedi": "Could not save settings: {hata}",
        "cikis_onay": "Copying is in progress. Quit anyway?",
        "surucu_yok": "No CD drive found.",
        "klasor_secin": "Choose a destination folder first.",
        "bekleniyor": "Waiting for a disc... ({suruculer})",
        "hata": "ERROR: {hata}",
        "okunuyor": "Reading {harf}...",
        "disk_bulundu": "Disc found: {harf} {etiket}",
        "hesaplaniyor": "estimating time left...",
        "kaldi": "~{sure} left ({hiz}/s)",
        "ilerleme": "{yuzde}% - {sure} - {ad}",
        "hatali_bitti": "{sayi} files copied ({ozet}), {hata_sayisi} errors. Disc was not ejected. Folder: {hedef}",
        "tamamlandi": "Done: {sayi} files ({ozet}) -> {hedef}",
        "cikariliyor": "Ejecting disc...",
        "cikarildi": "Disc ejected.",
        "cikarilamadi": "Could not eject the disc; please eject it manually.",
        "iptal_edildi": "Cancelled. Files copied so far remain in the destination.",
        "hata_cikarilmadi": "ERROR: {hata} Disc was not ejected.",
        "bos_disk": "No readable files on the disc.",
        "muzik_cd": "This is an audio CD; only data discs can be copied.",
        "yer_yok": "Not enough free space at the destination.",
        "sure_sn": "{sn} s",
        "sure_dk": "{dk} min",
        "sure_dk_sn": "{dk} min {sn:02d} s",
        "sure_sa_dk": "{sa} h {dk:02d} min",
        "ondalik": ".",
    },
}

_secili = "tr"


def sistem_dili():
    """Windows arayüz dili Türkçe ise 'tr', değilse 'en'."""
    try:
        return "tr" if ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF == 0x1F else "en"
    except Exception:
        return "en"


def dil_sec(kod):
    global _secili
    _secili = kod if kod in METINLER else "en"


def secili():
    return _secili


def t(anahtar, **degerler):
    """Seçili dildeki metin; {alan}'lar degerler ile doldurulur."""
    metin = METINLER[_secili].get(anahtar) or METINLER["tr"][anahtar]
    return metin.format(**degerler) if degerler else metin
