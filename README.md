# Ağ İzleme Sistemi

Windows tabanlı, düşük kaynak tüketimli profesyonel ağ izleme sistemi.

![Ekran Görüntüsü](docs/screenshot.png)

## Özellikler

- 📊 Gerçek zamanlı ağ performans metrikleri izleme
- 💻 Düşük CPU ve bellek kullanımı
- 🎯 Çoklu hedef desteği
- ⚡ Özelleştirilebilir uyarı sistemi
- 🌐 TR/EN dil desteği
- 📈 Grafana ve yerel dashboard entegrasyonu

## Gereksinimler

- Python 3.11 veya üstü
- Docker ve Docker Compose (veritabanları için)
- Windows 10/11

## Hızlı Başlangıç

1. Repoyu klonlayın:
   ```bash
   git clone https://github.com/kullaniciadi/connection-stability-test.git
   cd connection-stability-test
   ```

2. Sanal ortam oluşturun:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows için
   ```

3. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. Veritabanlarını başlatın:
   ```bash
   docker-compose up -d
   ```

5. Yapılandırma dosyasını oluşturun:
   ```bash
   cp config.example.yaml config.yaml
   ```

6. Uygulamayı başlatın:
   ```bash
   python src/main.py
   ```

## Yapılandırma

`config.yaml` dosyasında şu ayarları özelleştirebilirsiniz:

- Hedef sunucular ve kontrol aralıkları
- Veritabanı bağlantı bilgileri
- Uyarı eşikleri ve bildirimleri
- Loglama seviyeleri

Detaylı yapılandırma için [yapılandırma kılavuzuna](docs/configuration.md) bakın.

## Geliştirme

```bash
# Test ortamını hazırlama
python -m venv venv
.\venv\Scripts\activate   # Windows
pip install -r requirements-dev.txt

# Testleri çalıştırma
pytest

# Kod stil kontrolü
black .
flake8
```

## Performans Optimizasyonları

- ⚡ Asenkron I/O işlemleri
- 📊 Verimli bellek yönetimi
- 💾 Batch işlemler ile veritabanı yazma
- ⏱️ Özelleştirilebilir örnekleme aralıkları

## Katkıda Bulunma

1. Bu repoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'feat: add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

## İletişim

Proje Sahibi - [@github_kullanici](https://github.com/github_kullanici)

Proje Linki: [https://github.com/kullaniciadi/connection-stability-test](https://github.com/kullaniciadi/connection-stability-test) 