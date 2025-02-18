# Yapılandırma Kılavuzu

Bu dokümanda, Ağ İzleme Sistemi'nin yapılandırma seçenekleri detaylı olarak açıklanmaktadır.

## Yapılandırma Dosyası

Sistem, `config.yaml` dosyası üzerinden yapılandırılır. Örnek bir yapılandırma dosyası `config.example.yaml` olarak sunulmuştur.

## Yapılandırma Bölümleri

### 1. Ağ İzleme Hedefleri

```yaml
targets:
  - name: "Google DNS"
    address: "8.8.8.8"
    interval: 1.0  # saniye
```

- `name`: Hedefin görünen adı
- `address`: IP adresi veya alan adı
- `interval`: Kontrol aralığı (saniye)

### 2. InfluxDB Yapılandırması

```yaml
influxdb:
  url: "http://localhost:8086"
  token: "your-token-here"
  org: "your-org"
  bucket: "network-metrics"
  batch_size: 100
  flush_interval: 10
```

- `url`: InfluxDB sunucu adresi
- `token`: API anahtarı
- `org`: Organizasyon adı
- `bucket`: Veri deposu adı
- `batch_size`: Toplu yazma boyutu
- `flush_interval`: Yazma aralığı (saniye)

### 3. PostgreSQL Yapılandırması

```yaml
postgresql:
  dsn: "postgresql://user:password@localhost:5432/network_monitor"
```

- `dsn`: Veritabanı bağlantı bilgileri

### 4. Uygulama Ayarları

```yaml
app:
  language: "tr"
  cpu_check_interval: 60
  ui:
    update_interval: 1.0
    theme: "light"
    chart_points: 100
```

- `language`: Arayüz dili (tr/en)
- `cpu_check_interval`: CPU kullanım kontrolü aralığı (saniye)
- `ui.update_interval`: Arayüz güncelleme aralığı (saniye)
- `ui.theme`: Tema (light/dark)
- `ui.chart_points`: Grafiklerde gösterilecek nokta sayısı

### 5. Loglama Yapılandırması

```yaml
logging:
  version: 1
  disable_existing_loggers: false
  formatters:
    standard:
      format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
  handlers:
    console:
      class: logging.StreamHandler
      level: INFO
      formatter: standard
      stream: ext://sys.stdout
    file:
      class: logging.handlers.RotatingFileHandler
      level: DEBUG
      formatter: standard
      filename: network_monitor.log
      maxBytes: 10485760
      backupCount: 3
  root:
    level: INFO
    handlers: [console, file]
```

- `formatters`: Log mesaj formatları
- `handlers`: Log hedefleri (konsol/dosya)
- `root.level`: Ana log seviyesi
- `handlers.file.maxBytes`: Log dosyası maksimum boyutu
- `handlers.file.backupCount`: Yedek log dosyası sayısı

### 6. Uyarı Yapılandırması

```yaml
alerts:
  latency_threshold: 100
  packet_loss_threshold: 5
  notification_cooldown: 300
  methods:
    - type: "email"
      enabled: false
      smtp_server: "smtp.gmail.com"
      smtp_port: 587
      username: "your-email@gmail.com"
      password: "your-app-password"
      recipients: ["admin@example.com"]
```

- `latency_threshold`: Gecikme eşiği (ms)
- `packet_loss_threshold`: Paket kaybı eşiği (%)
- `notification_cooldown`: Bildirimler arası bekleme süresi (saniye)
- `methods`: Bildirim yöntemleri yapılandırması

## Çevre Değişkenleri

Hassas bilgiler için çevre değişkenleri kullanılabilir:

- `INFLUXDB_URL`
- `INFLUXDB_TOKEN`
- `INFLUXDB_ORG`
- `INFLUXDB_BUCKET`
- `POSTGRES_DSN`

## Örnek .env Dosyası

```env
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-super-secret-token
INFLUXDB_ORG=network-monitor
INFLUXDB_BUCKET=network-metrics
POSTGRES_DSN=postgresql://admin:adminpassword@localhost:5432/network_monitor
``` 