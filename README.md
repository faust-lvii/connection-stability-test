# Ağ İzleme Sistemi

Windows tabanlı, düşük kaynak tüketimli profesyonel ağ izleme sistemi.

## Özellikler

- Gerçek zamanlı ağ performans metrikleri izleme
- Düşük CPU ve bellek kullanımı
- Çoklu hedef desteği
- Özelleştirilebilir uyarı sistemi
- TR/EN dil desteği
- Grafana ve yerel dashboard entegrasyonu

## Kurulum

1. Python 3.11 veya üstü sürümü yükleyin
2. Gerekli bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
3. InfluxDB ve PostgreSQL veritabanlarını kurun (Docker compose dosyası ile)
4. Yapılandırma dosyasını düzenleyin:
   ```bash
   cp config.example.yaml config.yaml
   ```
5. Uygulamayı başlatın:
   ```bash
   python src/main.py
   ```

## Geliştirme

```bash
# Test ortamı hazırlama
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Testleri çalıştırma
pytest

# Kod stil kontrolü
black .
flake8
```

## Performans Optimizasyonları

- Asenkron I/O işlemleri
- Verimli bellek yönetimi
- Batch işlemler ile veritabanı yazma
- Özelleştirilebilir örnekleme aralıkları

## Lisans

MIT 