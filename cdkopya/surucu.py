"""Windows CD/DVD sürücü işlemleri (ctypes, ek paket gerekmez)."""
import ctypes
import string
from ctypes import wintypes

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.CreateFileW.restype = wintypes.HANDLE
k32.CreateFileW.argtypes = [
    wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
    wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
k32.DeviceIoControl.argtypes = [
    wintypes.HANDLE, wintypes.DWORD, wintypes.LPVOID, wintypes.DWORD,
    wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD), wintypes.LPVOID]
k32.CloseHandle.argtypes = [wintypes.HANDLE]
k32.SetErrorMode(1)  # "Sürücüde disk yok" pencerelerini engelle

SURUCU_CDROM = 5
GECERSIZ_TUTAMAC = wintypes.HANDLE(-1).value


def cd_suruculeri():
    """Sistemdeki CD/DVD sürücü harfleri, ör. ['E:']."""
    maske = k32.GetLogicalDrives()
    return [f"{h}:" for i, h in enumerate(string.ascii_uppercase)
            if maske >> i & 1 and k32.GetDriveTypeW(f"{h}:\\") == SURUCU_CDROM]


def disk_bilgisi(surucu):
    """Disk takılıysa (etiket, seri no), değilse None. Sürücüde açık tutamaç bırakmaz."""
    etiket = ctypes.create_unicode_buffer(261)
    seri = wintypes.DWORD()
    if k32.GetVolumeInformationW(f"{surucu}\\", etiket, 261, ctypes.byref(seri),
                                 None, None, None, 0):
        return etiket.value, seri.value
    return None


def diski_cikar(surucu):
    """Sürücü tepsisini açar; başarılıysa True."""
    GENERIC_READ, PAYLASIM, OPEN_EXISTING = 0x80000000, 3, 3
    IOCTL_STORAGE_EJECT_MEDIA = 0x2D4808
    tutamac = k32.CreateFileW(rf"\\.\{surucu}", GENERIC_READ, PAYLASIM, None,
                              OPEN_EXISTING, 0, None)
    if tutamac == GECERSIZ_TUTAMAC:
        return False
    try:
        n = wintypes.DWORD()
        return bool(k32.DeviceIoControl(tutamac, IOCTL_STORAGE_EJECT_MEDIA, None, 0,
                                        None, 0, ctypes.byref(n), None))
    finally:
        k32.CloseHandle(tutamac)
