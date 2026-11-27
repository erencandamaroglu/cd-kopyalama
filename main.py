"""Uygulama başlangıcı: python main.py [--veri KLASOR]."""
import argparse
import os
import sys


def hata_kaydini_ac():
    """Hatalar %USERPROFILE%\\CdKopyalama\\hata.log'a yazılır (pythonw ile konsol olmadığı için)."""
    import faulthandler
    import traceback
    from datetime import datetime

    from cdkopya.yollar import veri_klasoru

    yol = veri_klasoru() / "hata.log"
    try:
        if yol.exists() and yol.stat().st_size > 1_000_000:  # büyümesin
            yol.replace(yol.with_suffix(".eski.log"))
        dosya = open(yol, "a", encoding="utf-8", buffering=1)
    except OSError:
        return
    dosya.write(f"\n=== {datetime.now():%Y-%m-%d %H:%M:%S} program açıldı ===\n")
    faulthandler.enable(dosya, all_threads=True)

    def yakala(tur, deger, iz):
        dosya.write(f"--- {datetime.now():%Y-%m-%d %H:%M:%S} yakalanmamış hata ---\n")
        dosya.write("".join(traceback.format_exception(tur, deger, iz)))

    sys.excepthook = yakala
    main.hata_dosyasi = dosya  # kapanmasın


def main():
    parser = argparse.ArgumentParser(description="Takılan CD'yi klasöre kopyalar ve çıkarır")
    parser.add_argument("--veri", help="Ayar klasörü (varsayılan: %%USERPROFILE%%\\CdKopyalama)")
    args = parser.parse_args()
    if args.veri:
        os.environ["CDKOPYA_VERI"] = args.veri

    from cdkopya.arayuz import AnaPencere

    hata_kaydini_ac()
    pencere = AnaPencere()
    pencere.report_callback_exception = lambda *hata: sys.excepthook(*hata)
    pencere.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
