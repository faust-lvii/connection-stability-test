import os
import yaml
import logging.config
from typing import Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        """
        Yapılandırma yönetimi sınıfı.
        
        Args:
            config_path: Yapılandırma dosyası yolu
        """
        self.config_path = config_path
        self.config = {}
        self._load_config()
        self._setup_logging()

    def _load_config(self):
        """Yapılandırma dosyasını yükler ve çevre değişkenlerini uygular."""
        try:
            # .env dosyasını yükle
            load_dotenv()

            # Yapılandırma dosyasını oku
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

            # Çevre değişkenlerini uygula
            self.config['influxdb']['url'] = os.getenv('INFLUXDB_URL', self.config['influxdb']['url'])
            self.config['influxdb']['token'] = os.getenv('INFLUXDB_TOKEN', self.config['influxdb']['token'])
            self.config['influxdb']['org'] = os.getenv('INFLUXDB_ORG', self.config['influxdb']['org'])
            self.config['influxdb']['bucket'] = os.getenv('INFLUXDB_BUCKET', self.config['influxdb']['bucket'])

            self.config['postgresql']['dsn'] = os.getenv('POSTGRES_DSN', self.config['postgresql']['dsn'])

        except Exception as e:
            logger.error(f"Yapılandırma yükleme hatası: {str(e)}")
            raise

    def _setup_logging(self):
        """Loglama yapılandırmasını ayarlar."""
        logging.config.dictConfig(self.config['logging'])

    def get(self, key: str, default: Any = None) -> Any:
        """
        Yapılandırma değerini döndürür.
        
        Args:
            key: Yapılandırma anahtarı
            default: Varsayılan değer
        
        Returns:
            Yapılandırma değeri
        """
        try:
            current = self.config
            for k in key.split('.'):
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default

    def get_all(self) -> Dict:
        """Tüm yapılandırmayı döndürür."""
        return self.config.copy() 