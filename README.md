# CD Kopyalayıcı

Takılan CD/DVD'yi seçilen klasöre kopyalar, kopyalama bitince diski çıkarır. Ek paket gerekmez.

## Çalıştırma

1. Python 3.8+ kurulu olmalı (python.org; kurulumda "Add python.exe to PATH").
2. `baslat.bat` → pencere açılır.

## Kullanım

1. **Seç...** ile kopyalanacak klasörü belirleyin (hatırlanır).
2. CD'yi takın; kopyalama kendiliğinden başlar. **İptal** ile durdurulabilir.
3. Bitince CD çıkar, program sıradaki CD'yi bekler.

- Her CD kendi adıyla ayrı klasöre kopyalanır; aynı ad varsa `Ad (2)` açılır, üzerine yazılmaz.
- Okunamayan dosya olursa kalanlar kopyalanır, hatalar listelenir ve CD **çıkarılmaz**.
- Müzik CD'leri ve kopya korumalı film DVD'leri desteklenmez.
- USB okuyucuyu sökmeden önce programı kapatın.

Ayarlar ve hata kaydı: `%USERPROFILE%\CdKopyalama`.

## Testler

```
python -B -m unittest discover -s tests -v
```

Testler gerçek CD sürücüsüne dokunmaz.

## Lisans

MIT — ayrıntılar [LICENSE](LICENSE) dosyasında.
