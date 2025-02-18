import pytest
from datetime import datetime
import os

from src.core.data_store import DataStore

@pytest.fixture
def data_store():
    # Test için geçici veritabanı bağlantıları
    return DataStore(
        influx_url=os.getenv('TEST_INFLUXDB_URL', 'http://localhost:8086'),
        influx_token=os.getenv('TEST_INFLUXDB_TOKEN', 'test-token'),
        influx_org=os.getenv('TEST_INFLUXDB_ORG', 'test-org'),
        influx_bucket=os.getenv('TEST_INFLUXDB_BUCKET', 'test-bucket'),
        postgres_dsn=os.getenv('TEST_POSTGRES_DSN', 'postgresql://admin:adminpassword@localhost:5432/test_db')
    )

@pytest.mark.asyncio
async def test_store_metrics_success(data_store):
    test_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'target': '8.8.8.8',
        'status': 'OK',
        'latency': 100.0,
        'packet_loss': 0,
        'cpu_usage': 5.0,
        'memory_usage': 2.0
    }
    
    try:
        await data_store.store_metrics(test_data)
    except Exception as e:
        pytest.fail(f"Veri kaydetme başarısız: {str(e)}")

@pytest.mark.asyncio
async def test_store_metrics_error_event(data_store):
    test_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'target': '8.8.8.8',
        'status': 'ERROR',
        'error': 'Test error message'
    }
    
    try:
        await data_store.store_metrics(test_data)
    except Exception as e:
        pytest.fail(f"Hata olayı kaydetme başarısız: {str(e)}")

def test_database_connection(data_store):
    try:
        # InfluxDB bağlantısı kontrolü
        assert data_store.influx_client is not None
        assert data_store.write_api is not None
        
        # PostgreSQL bağlantısı kontrolü
        with data_store.pg_conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
            assert result[0] == 1
    except Exception as e:
        pytest.fail(f"Veritabanı bağlantı testi başarısız: {str(e)}")

def test_cleanup(data_store):
    data_store.close()
    assert data_store.influx_client is not None  # InfluxDB client hala var ama kapalı
    assert data_store.pg_conn is None  # PostgreSQL bağlantısı kapatıldı 