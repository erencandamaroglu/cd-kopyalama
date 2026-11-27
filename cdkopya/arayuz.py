"""tkinter ana pencere ve sürücü izleme iş parçacığı."""
import os
import queue
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from cdkopya import surucu
from cdkopya.gorev_cubugu import pencereye_ikon_ver, surece_kimlik_ver
from cdkopya.kopyalama import Iptal, SureTahmini, boyut_metni, diski_kopyala, sure_metni
from cdkopya.yollar import ayar_oku, ayar_yaz, yerel_ikon

BASLIK = "CD Kopyalayıcı"
YOKLAMA_SN = 2


class AnaPencere(tk.Tk):
    def __init__(self):
        surece_kimlik_ver()
        super().__init__()
        self.title(BASLIK)
        self.ikon_ayarla()
        self.geometry("580x360")
        self.minsize(460, 300)
        self.mesajlar = queue.Queue()
        self.dur = threading.Event()
        self.kapan = threading.Event()
        self.kopyalaniyor = False
        self.hedef = str(ayar_oku().get("hedef") or "")

        cerceve = ttk.Frame(self, padding=12)
        cerceve.pack(fill="both", expand=True)
        ttk.Label(cerceve, text="Kopyalanacak klasör:").pack(anchor="w")
        satir = ttk.Frame(cerceve)
        satir.pack(fill="x", pady=(2, 10))
        self.yol = tk.StringVar(value=self.hedef)
        ttk.Entry(satir, textvariable=self.yol, state="readonly").pack(
            side="left", fill="x", expand=True)
        ttk.Button(satir, text="Seç...", command=self.klasor_sec).pack(
            side="left", padx=(6, 0))

        self.durum = tk.StringVar(value="Başlatılıyor...")
        ttk.Label(cerceve, textvariable=self.durum).pack(anchor="w")
        satir = ttk.Frame(cerceve)
        satir.pack(fill="x", pady=(4, 10))
        self.cubuk = ttk.Progressbar(satir, maximum=100)
        self.cubuk.pack(side="left", fill="x", expand=True)
        self.iptal = ttk.Button(satir, text="İptal", command=self.dur.set, state="disabled")
        self.iptal.pack(side="left", padx=(6, 0))

        self.kayit = tk.Text(cerceve, height=8, state="disabled", wrap="word",
                             font=("Segoe UI", 9))
        self.kayit.pack(fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self.kapat)
        threading.Thread(target=self.izle, daemon=True).start()
        self.mesajlari_isle()

    def ikon_ayarla(self):
        """Başlık çubuğu, Alt+Tab ve görev çubuğu ikonu. İkon yoksa ya da okunamazsa program yine açılır."""
        try:
            self.iconbitmap(default=str(yerel_ikon()))  # default: açılan diyaloglar da aynı ikonu alır
        except tk.TclError:
            return
        self.update_idletasks()
        pencereye_ikon_ver(int(self.wm_frame(), 16))

    def klasor_sec(self):
        secilen = filedialog.askdirectory(initialdir=self.hedef or None)
        if not secilen:
            return
        secilen = os.path.normpath(secilen)
        if os.path.splitdrive(secilen)[0].upper() in surucu.cd_suruculeri():
            messagebox.showerror(BASLIK, "Hedef olarak CD sürücüsü seçilemez.")
            return
        self.hedef = secilen
        self.yol.set(secilen)
        try:
            ayar_yaz(hedef=secilen)
        except OSError as e:
            self.yaz(f"Ayar kaydedilemedi: {e}")

    def kapat(self):
        if self.kopyalaniyor and not messagebox.askyesno(
                BASLIK, "Kopyalama sürüyor. Yine de çıkılsın mı?"):
            return
        self.kapan.set()
        self.dur.set()
        self.destroy()

    def yaz(self, metin):
        self.kayit.config(state="normal")
        self.kayit.insert("end", f"[{datetime.now():%H:%M:%S}] {metin}\n")
        self.kayit.see("end")
        self.kayit.config(state="disabled")

    def mesajlari_isle(self):
        son = {}  # durum/ilerleme için yalnızca en son değer gerekir
        try:
            while True:
                tur, veri = self.mesajlar.get_nowait()
                if tur == "kayit":
                    self.yaz(veri)
                else:
                    son[tur] = veri
        except queue.Empty:
            pass
        if "durum" in son:
            self.durum.set(son["durum"])
        if "yuzde" in son:
            self.cubuk["value"] = son["yuzde"]
        if "mesgul" in son:
            self.iptal.config(state="normal" if son["mesgul"] else "disabled")
        self.after(100, self.mesajlari_isle)

    # Aşağısı arka plan iş parçacığında çalışır; arayüze yalnızca kuyrukla erişir.
    def gonder(self, tur, veri):
        self.mesajlar.put((tur, veri))

    def izle(self):
        islenen = {}  # sürücü -> işlenmiş disk (çıkarılana dek tekrar kopyalanmaz)
        while not self.kapan.is_set():
            try:
                suruculer = surucu.cd_suruculeri()
                if not suruculer:
                    durum = "CD sürücüsü bulunamadı."
                elif not self.hedef:
                    durum = "Önce kopyalanacak klasörü seçin."
                else:
                    durum = "CD bekleniyor... (" + ", ".join(suruculer) + ")"
                self.gonder("durum", durum)
                for s in list(islenen):
                    if s not in suruculer:
                        del islenen[s]
                for s in suruculer:
                    disk = surucu.disk_bilgisi(s)
                    if disk is None:
                        islenen.pop(s, None)
                    elif self.hedef and islenen.get(s) != disk:
                        islenen[s] = disk
                        self.diski_isle(s, disk[0])
                    if self.kapan.is_set():
                        break
            except Exception as e:
                self.gonder("kayit", f"HATA: {e}")
            self.kapan.wait(YOKLAMA_SN)

    def diski_isle(self, harf, etiket):
        self.dur.clear()
        if self.kapan.is_set():
            return
        self.kopyalaniyor = True
        self.gonder("mesgul", True)
        self.gonder("yuzde", 0)
        self.gonder("durum", f"{harf} okunuyor...")
        self.gonder("kayit", f"Disk bulundu: {harf} {etiket}")

        tahmin = SureTahmini()

        def ilerleme(tamam, toplam, ad):
            yuzde = tamam * 100 / toplam if toplam else 100
            kalan, hiz = tahmin.guncelle(tamam, toplam)
            if kalan is None:
                sure = "kalan süre hesaplanıyor..."
            else:
                sure = f"~{sure_metni(kalan)} kaldı ({boyut_metni(hiz)}/sn)"
            self.gonder("yuzde", yuzde)
            self.gonder("durum", f"%{yuzde:.0f} - {sure} - {ad}")

        try:
            hedef, sayi, hatalar, toplam = diski_kopyala(
                f"{harf}\\", self.hedef, etiket, self.dur, ilerleme)
            ozet = f"{boyut_metni(toplam)}, {sure_metni(tahmin.gecen())}"
            for h in hatalar:
                self.gonder("kayit", f"HATA: {h}")
            if hatalar:
                self.gonder("kayit", f"{sayi} dosya kopyalandı ({ozet}), {len(hatalar)} hata var. "
                                     f"Disk çıkarılmadı. Klasör: {hedef}")
            else:
                self.gonder("yuzde", 100)
                self.gonder("kayit", f"Tamamlandı: {sayi} dosya ({ozet}) -> {hedef}")
                self.gonder("durum", "Disk çıkarılıyor...")
                self.gonder("kayit", "Disk çıkarıldı." if surucu.diski_cikar(harf)
                            else "Disk çıkarılamadı, elle çıkarın.")
        except Iptal:
            self.gonder("kayit", "İptal edildi. Kopyalanan dosyalar hedefte kaldı.")
        except Exception as e:
            self.gonder("kayit", f"HATA: {e} Disk çıkarılmadı.")
        finally:
            self.kopyalaniyor = False
            self.gonder("mesgul", False)
