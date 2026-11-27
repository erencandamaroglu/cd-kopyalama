"""Uygulama ikonunu çizer: varliklar/ikon.png (512 px) ve varliklar/ikon.ico (16–256 px).

Mavi zemin üzerinde gümüş CD, sağ altta yeşil "kopyala/indir" rozeti.
Pillow yalnızca bu araç için gerekir (program çalışırken gerekmez).
Çalıştırma: python tools\\ikon_olustur.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

VARLIKLAR = Path(__file__).resolve().parent.parent / "varliklar"
OLCEK = 4  # büyük çizip küçültünce kenarlar yumuşak olur
BOYUT = 512 * OLCEK


def s(deger):
    return int(deger * OLCEK)


def zemin():
    """Yukarıdan aşağı açık maviden koyu maviye geçişli yuvarlatılmış kare."""
    gecis = Image.new("RGBA", (BOYUT, BOYUT))
    cizim = Image.new("RGBA", (BOYUT, BOYUT), (0, 0, 0, 0))
    c = ImageDraw.Draw(gecis)
    for y in range(BOYUT):
        o = y / BOYUT
        c.line([(0, y), (BOYUT, y)], fill=(int(59 - 29 * o), int(130 - 66 * o), int(246 - 71 * o), 255))
    maske = Image.new("L", (BOYUT, BOYUT), 0)
    ImageDraw.Draw(maske).rounded_rectangle([s(16), s(16), s(496), s(496)], radius=s(110), fill=255)
    cizim.paste(gecis, mask=maske)
    return cizim


def disk():
    """Ortası delik gümüş CD; yüzeyinde hafif renkli yansıma dilimleri."""
    katman = Image.new("RGBA", (BOYUT, BOYUT), (0, 0, 0, 0))
    c = ImageDraw.Draw(katman)
    mx, my, r = s(236), s(236), s(184)
    kutu = [mx - r, my - r, mx + r, my + r]
    c.ellipse(kutu, fill=(226, 232, 240, 255))
    yansima = [(195, 225, (191, 219, 254, 255)), (225, 245, (251, 207, 232, 255)),
               (15, 35, (254, 240, 138, 255)), (35, 60, (191, 219, 254, 255)),
               (105, 130, (187, 247, 208, 255)), (295, 315, (254, 240, 138, 255))]
    for bas, bit, renk in yansima:
        c.pieslice(kutu, bas, bit, fill=renk)
    c.ellipse(kutu, outline=(148, 163, 184, 255), width=s(6))
    for oran, renk in ((0.36, (203, 213, 225, 255)), (0.30, (241, 245, 249, 255))):
        rr = int(r * oran)
        c.ellipse([mx - rr, my - rr, mx + rr, my + rr], fill=renk, outline=(148, 163, 184, 255), width=s(4))
    # Delik: alfayı sıfırlayan maske, zemin görünür
    delik = Image.new("L", (BOYUT, BOYUT), 255)
    rr = int(r * 0.13)
    ImageDraw.Draw(delik).ellipse([mx - rr, my - rr, mx + rr, my + rr], fill=0)
    alfa = Image.composite(katman.getchannel("A"), Image.new("L", (BOYUT, BOYUT), 0), delik)
    katman.putalpha(alfa)
    return katman


def rozet(c):
    """Sağ altta beyaz kenarlı yeşil daire, içinde aşağı ok (kopyala)."""
    mx, my, r = s(384), s(384), s(88)
    c.ellipse([mx - r - s(12), my - r - s(12), mx + r + s(12), my + r + s(12)], fill=(255, 255, 255, 255))
    c.ellipse([mx - r, my - r, mx + r, my + r], fill=(22, 163, 74, 255))
    c.rounded_rectangle([mx - s(18), my - s(54), mx + s(18), my + s(12)], radius=s(7), fill=(255, 255, 255, 255))
    c.polygon([(mx - s(46), my + s(2)), (mx + s(46), my + s(2)), (mx, my + s(50))], fill=(255, 255, 255, 255))


def ciz():
    gorsel = zemin()
    gorsel.alpha_composite(disk())
    rozet(ImageDraw.Draw(gorsel))
    return gorsel.resize((512, 512), Image.LANCZOS)


def main():
    VARLIKLAR.mkdir(exist_ok=True)
    ikon = ciz()
    ikon.save(VARLIKLAR / "ikon.png")
    ikon.save(VARLIKLAR / "ikon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
              bitmap_format="bmp")  # Explorer PNG sıkıştırmalı küçük ikonları kısayolda göstermiyor
    print(VARLIKLAR / "ikon.ico")


if __name__ == "__main__":
    main()
