"""Windows görev çubuğunda programın kendi ikonu (kesit projesindeki yöntem).

pythonw ile açılan pencere görev çubuğunda Python ikonuyla görünür. Pencerenin özellik deposuna kendi
AppUserModelID'si, ikonu ve yeniden açma komutu yazılınca kendi düğmesinde bu ikonla görünür; görev çubuğuna
sabitlenirse de baslat.bat ile açılır. Microsoft Store Python'unda süreç düzeyindeki kimlik yok sayıldığı için
pencere düzeyinde yazılır. Explorer ağ sürücüsündeki ikonu okumayabildiğinden ikonun yerel kopyası kullanılır.
"""
import ctypes
import os
import sys
from ctypes import HRESULT, POINTER, WINFUNCTYPE, Structure, byref, c_ubyte, c_ulong, c_ushort, c_void_p, c_wchar_p

from .yollar import PROJE, yerel_ikon

KIMLIK = "CdKopyalayici.Uygulama"
GORUNEN_AD = "CD Kopyalayıcı"


class _GUID(Structure):
    _fields_ = [("a", c_ulong), ("b", c_ushort), ("c", c_ushort), ("d", c_ubyte * 8)]


class _PROPERTYKEY(Structure):
    _fields_ = [("fmtid", _GUID), ("pid", c_ulong)]


class _PROPVARIANT(Structure):
    _fields_ = [("vt", c_ushort), ("r1", c_ushort), ("r2", c_ushort), ("r3", c_ushort), ("p", c_void_p), ("p2", c_void_p)]


def _guid(metin):
    g = _GUID()
    ctypes.oledll.ole32.CLSIDFromString(c_wchar_p(metin), byref(g))
    return g


def surece_kimlik_ver():
    """python.org Python'unda yeterli; pencere oluşmadan çağrılır. Hata olursa sessiz geçer."""
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(c_wchar_p(KIMLIK))
    except Exception:
        pass


def pencereye_ikon_ver(hwnd):
    """Pencereye görev çubuğu kimliği, ikonu ve yeniden açma komutu verir. Hata olursa sessiz geçer."""
    if sys.platform != "win32":
        return False
    try:
        magaza = c_void_p()
        ctypes.oledll.shell32.SHGetPropertyStoreForWindow(
            c_void_p(hwnd), byref(_guid("{886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99}")), byref(magaza))
        tablo = ctypes.cast(magaza, POINTER(POINTER(c_void_p))).contents
        deger_yaz = WINFUNCTYPE(HRESULT, c_void_p, POINTER(_PROPERTYKEY), POINTER(_PROPVARIANT))(tablo[6])
        kaydet = WINFUNCTYPE(HRESULT, c_void_p)(tablo[7])
        birak = WINFUNCTYPE(c_ulong, c_void_p)(tablo[2])
        fmt = _guid("{9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3}")  # PKEY_AppUserModel_*
        tamponlar = []
        # 2: yeniden açma komutu, 3: ikon, 4: görünen ad, 5: kimlik.
        # baslat.bat sürücü harfiyle (Y:\...) verilir: cmd UNC klasörüne geçemez.
        baslat = os.path.join(str(PROJE), "baslat.bat")
        for pid, deger in ((2, f'{os.environ.get("ComSpec", "cmd.exe")} /c "{baslat}"'), (3, f"{yerel_ikon()},0"),
                           (4, GORUNEN_AD), (5, KIMLIK)):
            tamponlar.append(ctypes.create_unicode_buffer(deger))
            deger_yaz(magaza, byref(_PROPERTYKEY(fmt, pid)),
                      byref(_PROPVARIANT(vt=31, p=ctypes.cast(tamponlar[-1], c_void_p))))
        kaydet(magaza)
        birak(magaza)
        return True
    except Exception:
        return False
