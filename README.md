# CD Kopyalayıcı

Takılan CD/DVD'yi seçilen klasöre kopyalar, kopyalama bitince diski çıkarır. Ek paket gerekmez.

## Çalıştırma

1. Python 3.8+ kurulu olmalı (python.org; kurulumda "Add python.exe to PATH").
2. `kurulum.bat` → klasörde `.venv` oluşturur, masaüstüne "CD Kopyalayici" kısayolu koyar (bir kez).
3. `baslat.bat` ya da kısayol → pencere açılır.
4. `guncelle.bat` → GitHub'dan son sürümü çeker (`git pull`). Ayarlar korunur.

Klasör başka bilgisayara taşınırsa orada bir kez `kurulum.bat` çalıştırın; çalışmayan `.venv` yeniden kurulur.

## Kullanım

1. **Seç...** ile kopyalanacak klasörü belirleyin (hatırlanır).
2. CD'yi takın; kopyalama kendiliğinden başlar. **İptal** ile durdurulabilir.
3. Bitince CD çıkar, program sıradaki CD'yi bekler.

- Her CD kendi adıyla ayrı klasöre kopyalanır; aynı ad varsa `Ad (2)` açılır, üzerine yazılmaz.
- Okunamayan dosya olursa kalanlar kopyalanır, hatalar listelenir ve CD **çıkarılmaz**.
- Müzik CD'leri ve kopya korumalı film DVD'leri desteklenmez.
- USB okuyucuyu sökmeden önce programı kapatın.

Ayarlar ve hata kaydı: `%USERPROFILE%\CdKopyalama`.

## İkon

`varliklar/ikon.ico`, `tools/ikon_olustur.py` ile çizilir (Pillow gerekir, yalnızca ikonu yeniden üretmek için):

```
python tools\ikon_olustur.py
```

Sonra masaüstü kısayolu için `kurulum.bat` bir kez yeniden çalıştırılır.

## Testler

```
python -B -m unittest discover -s tests -v
```

Testler gerçek CD sürücüsüne dokunmaz.

## Lisans

MIT — ayrıntılar [LICENSE](LICENSE) dosyasında.
