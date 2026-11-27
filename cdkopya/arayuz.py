"""tkinter ana pencere ve sürücü izleme iş parçacığı."""
import os
import queue
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from cdkopya import dil, surucu
from cdkopya.dil import t
from cdkopya.gorev_cubugu import pencereye_ikon_ver, surece_kimlik_ver
from cdkopya.kopyalama import Iptal, SureTahmini, boyut_metni, diski_kopyala, sure_metni
from cdkopya.yollar import ayar_oku, ayar_yaz, yerel_ikon

YOKLAMA_SN = 2


class AnaPencere(tk.Tk):
    def __init__(self):
        surece_kimlik_ver()
        super().__init__()
        ayarlar = ayar_oku()
        dil.dil_sec(ayarlar.get("dil") or dil.sistem_dili())
        self.geometry("600x360")
        self.minsize(480, 300)
        self.mesajlar = queue.Queue()
        self.dur = threading.Event()
        self.kapan = threading.Event()
        self.kopyalaniyor = False
        self.hedef = str(ayarlar.get("hedef") or "")

        cerceve = ttk.Frame(self, padding=12)
        cerceve.pack(fill="both", expand=True)
        satir = ttk.Frame(cerceve)
        satir.pack(fill="x")
        self.hedef_etiket = ttk.Label(satir)
        self.hedef_etiket.pack(side="left", anchor="s")
        self.dil_kutusu = ttk.Combobox(satir, values=list(dil.DILLER.values()), state="readonly", width=9)
        self.dil_kutusu.set(dil.DILLER[dil.secili()])
        self.dil_kutusu.bind("<<ComboboxSelected>>", self.dil_degisti)
        self.dil_kutusu.pack(side="right")

        satir = ttk.Frame(cerceve)
        satir.pack(fill="x", pady=(4, 10))
        self.yol = tk.StringVar(value=self.hedef)
        ttk.Entry(satir, textvariable=self.yol, state="readonly").pack(
            side="left", fill="x", expand=True)
        self.sec_dugmesi = ttk.Button(satir, command=self.klasor_sec)
        self.sec_dugmesi.pack(side="left", padx=(6, 0))

        self.durum = tk.StringVar()
        ttk.Label(cerceve, textvariable=self.durum).pack(anchor="w")
        satir = ttk.Frame(cerceve)
        satir.pack(fill="x", pady=(4, 10))
        self.cubuk = ttk.Progressbar(satir, maximum=100)
        self.cubuk.pack(side="left", fill="x", expand=True)
        self.iptal = ttk.Button(satir, command=self.dur.set, state="disabled")
        self.iptal.pack(side="left", padx=(6, 0))

        self.kayit = tk.Text(cerceve, height=8, state="disabled", wrap="word",
                             font=("Segoe UI", 9))
        self.kayit.pack(fill="both", expand=True)

        self.metinleri_yaz()
        self.durum.set(t("baslatiliyor"))
        self.ikon_ayarla()
        self.protocol("WM_DELETE_WINDOW", self.kapat)
        threading.Thread(target=self.izle, daemon=True).start()
        self.mesajlari_isle()

    def metinleri_yaz(self):
        """Sabit arayüz metinleri seçili dilde. Durum satırı izleme döngüsünde kendiliğinden yenilenir;
        kayıttaki eski satırlar yazıldıkları dilde kalır."""
        self.title(t("baslik"))
        self.hedef_etiket.config(text=t("hedef_etiket"))
        self.sec_dugmesi.config(text=t("sec"))
        self.iptal.config(text=t("iptal"))

    def dil_degisti(self, _olay=None):
        kod = next(k for k, ad in dil.DILLER.items() if ad == self.dil_kutusu.get())
        dil.dil_sec(kod)
        self.metinleri_yaz()
        try:
            ayar_yaz(dil=kod)
        except OSError as e:
            self.yaz(t("ayar_kaydedilemedi", hata=e))

    def ikon_ayarla(self):
        """Başlık çubuğu, Alt+Tab ve görev çubuğu ikonu. İkon yoksa ya da okunamazsa program yine açılır."""
        try:
            self.iconbitmap(default=str(yerel_ikon()))  # default: açılan diyaloglar da aynı ikonu alır
        except tk.TclError:
            return
        self.update_idletasks()
        pencereye_ikon_ver(int(self.wm_frame(), 16), t("baslik"))

    def klasor_sec(self):
        secilen = filedialog.askdirectory(initialdir=self.hedef or None)
        if not secilen:
            return
        secilen = os.path.normpath(secilen)
        if os.path.splitdrive(secilen)[0].upper() in surucu.cd_suruculeri():
            messagebox.showerror(t("baslik"), t("cd_hedef_olamaz"))
            return
        self.hedef = secilen
        self.yol.set(secilen)
        try:
            ayar_yaz(hedef=secilen)
        except OSError as e:
            self.yaz(t("ayar_kaydedilemedi", hata=e))

    def kapat(self):
        if self.kopyalaniyor and not messagebox.askyesno(t("baslik"), t("cikis_onay")):
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
                    durum = t("surucu_yok")
                elif not self.hedef:
                    durum = t("klasor_secin")
                else:
                    durum = t("bekleniyor", suruculer=", ".join(suruculer))
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
                self.gonder("kayit", t("hata", hata=e))
            self.kapan.wait(YOKLAMA_SN)

    def diski_isle(self, harf, etiket):
        self.dur.clear()
        if self.kapan.is_set():
            return
        self.kopyalaniyor = True
        self.gonder("mesgul", True)
        self.gonder("yuzde", 0)
        self.gonder("durum", t("okunuyor", harf=harf))
        self.gonder("kayit", t("disk_bulundu", harf=harf, etiket=etiket))
        tahmin = SureTahmini()

        def ilerleme(tamam, toplam, ad):
            yuzde = tamam * 100 / toplam if toplam else 100
            kalan, hiz = tahmin.guncelle(tamam, toplam)
            if kalan is None:
                sure = t("hesaplaniyor")
            else:
                sure = t("kaldi", sure=sure_metni(kalan), hiz=boyut_metni(hiz))
            self.gonder("yuzde", yuzde)
            self.gonder("durum", t("ilerleme", yuzde=f"{yuzde:.0f}", sure=sure, ad=ad))

        try:
            hedef, sayi, hatalar, toplam = diski_kopyala(
                f"{harf}\\", self.hedef, etiket, self.dur, ilerleme)
            ozet = f"{boyut_metni(toplam)}, {sure_metni(tahmin.gecen())}"
            for h in hatalar:
                self.gonder("kayit", t("hata", hata=h))
            if hatalar:
                self.gonder("kayit", t("hatali_bitti", sayi=sayi, ozet=ozet, hata_sayisi=len(hatalar), hedef=hedef))
            else:
                self.gonder("yuzde", 100)
                self.gonder("kayit", t("tamamlandi", sayi=sayi, ozet=ozet, hedef=hedef))
                self.gonder("durum", t("cikariliyor"))
                self.gonder("kayit", t("cikarildi") if surucu.diski_cikar(harf) else t("cikarilamadi"))
        except Iptal:
            self.gonder("kayit", t("iptal_edildi"))
        except Exception as e:
            self.gonder("kayit", t("hata_cikarilmadi", hata=e))
        finally:
            self.kopyalaniyor = False
            self.gonder("mesgul", False)
