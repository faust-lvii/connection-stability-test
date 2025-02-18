import asyncio
from datetime import datetime
import logging
from typing import Dict, Optional
from ping3 import ping
import psutil

logger = logging.getLogger(__name__)

class NetworkProbe:
    def __init__(self, target: str = "8.8.8.8", timeout: float = 1.0):
        """
        Ağ izleme sınıfı.
        
        Args:
            target: Hedef IP adresi veya alan adı
            timeout: Ping timeout süresi (saniye)
        """
        self.target = target
        self.timeout = timeout
        self._running = False
        self._last_cpu_check = 0
        self._cpu_check_interval = 60  # CPU kullanımını her 60 saniyede bir kontrol et

    async def perform_check(self) -> Dict:
        """Tek bir ağ kontrolü gerçekleştirir."""
        try:
            # Ping işlemi
            latency = ping(self.target, timeout=self.timeout)
            
            # Sonuçları hazırla
            result = {
                'timestamp': datetime.utcnow().isoformat(),
                'target': self.target,
                'status': 'OK' if latency else 'FAIL',
                'latency': round(latency * 1000, 2) if latency else None,  # ms cinsinden
                'packet_loss': 0 if latency else 100
            }

            # Her 60 saniyede bir CPU kullanımını kontrol et
            current_time = datetime.utcnow().timestamp()
            if current_time - self._last_cpu_check >= self._cpu_check_interval:
                result['cpu_usage'] = psutil.cpu_percent(interval=0.1)
                result['memory_usage'] = psutil.Process().memory_percent()
                self._last_cpu_check = current_time

            return result

        except Exception as e:
            logger.error(f"Ağ kontrolü sırasında hata: {str(e)}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'target': self.target,
                'status': 'ERROR',
                'error': str(e)
            }

    async def continuous_monitor(self, interval: float = 1.0):
        """
        Sürekli ağ izleme işlemi.
        
        Args:
            interval: Kontroller arası bekleme süresi (saniye)
        """
        self._running = True
        while self._running:
            yield await self.perform_check()
            await asyncio.sleep(interval)

    def stop(self):
        """İzleme işlemini durdurur."""
        self._running = False 