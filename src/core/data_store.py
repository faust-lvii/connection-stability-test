from datetime import datetime
import logging
from typing import Dict, List
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS
import psycopg2
from psycopg2.extras import DictCursor

logger = logging.getLogger(__name__)

class DataStore:
    def __init__(
        self,
        influx_url: str,
        influx_token: str,
        influx_org: str,
        influx_bucket: str,
        postgres_dsn: str
    ):
        """
        Veri depolama sınıfı.
        
        Args:
            influx_url: InfluxDB sunucu adresi
            influx_token: InfluxDB API anahtarı
            influx_org: InfluxDB organizasyon adı
            influx_bucket: InfluxDB bucket adı
            postgres_dsn: PostgreSQL bağlantı bilgileri
        """
        # InfluxDB bağlantısı
        self.influx_client = InfluxDBClient(
            url=influx_url,
            token=influx_token,
            org=influx_org
        )
        self.write_api = self.influx_client.write_api(write_options=ASYNCHRONOUS)
        self.influx_bucket = influx_bucket
        self.influx_org = influx_org

        # PostgreSQL bağlantısı
        self.postgres_dsn = postgres_dsn
        self.pg_conn = None
        self._init_postgres()

    def _init_postgres(self):
        """PostgreSQL tablosunu oluşturur."""
        try:
            with psycopg2.connect(self.postgres_dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS network_events (
                            id SERIAL PRIMARY KEY,
                            timestamp TIMESTAMP WITH TIME ZONE,
                            target VARCHAR(255),
                            event_type VARCHAR(50),
                            details JSONB,
                            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                conn.commit()
        except Exception as e:
            logger.error(f"PostgreSQL başlatma hatası: {str(e)}")

    async def store_metrics(self, data: Dict):
        """
        Metrik verilerini InfluxDB'ye kaydeder.
        Önemli olayları PostgreSQL'e kaydeder.
        """
        try:
            # InfluxDB'ye metrik kaydetme
            point = Point("network_metrics")\
                .tag("target", data['target'])\
                .tag("status", data['status'])\
                .field("latency", data.get('latency', 0))\
                .field("packet_loss", data.get('packet_loss', 0))\
                .time(datetime.fromisoformat(data['timestamp']))

            if 'cpu_usage' in data:
                point = point.field("cpu_usage", data['cpu_usage'])
            if 'memory_usage' in data:
                point = point.field("memory_usage", data['memory_usage'])

            self.write_api.write(bucket=self.influx_bucket, org=self.influx_org, record=point)

            # Önemli olayları PostgreSQL'e kaydet
            if data['status'] != 'OK':
                with psycopg2.connect(self.postgres_dsn) as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO network_events 
                            (timestamp, target, event_type, details)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            datetime.fromisoformat(data['timestamp']),
                            data['target'],
                            data['status'],
                            data
                        ))
                    conn.commit()

        except Exception as e:
            logger.error(f"Veri kaydetme hatası: {str(e)}")

    def close(self):
        """Veritabanı bağlantılarını kapatır."""
        if self.influx_client:
            self.influx_client.close()
        if self.pg_conn:
            self.pg_conn.close() 