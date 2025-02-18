import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.core.network_probe import NetworkProbe

@pytest.fixture
def network_probe():
    return NetworkProbe(target="8.8.8.8", timeout=1.0)

@pytest.mark.asyncio
async def test_perform_check_success(network_probe):
    with patch('src.core.network_probe.ping', return_value=0.1):
        with patch('src.core.network_probe.psutil.cpu_percent', return_value=5.0):
            with patch('src.core.network_probe.psutil.Process') as mock_process:
                mock_process.return_value.memory_percent.return_value = 2.0
                
                result = await network_probe.perform_check()
                
                assert result['status'] == 'OK'
                assert result['latency'] == 100.0  # 0.1 saniye = 100 ms
                assert result['packet_loss'] == 0
                assert isinstance(result['timestamp'], str)
                assert result['target'] == '8.8.8.8'

@pytest.mark.asyncio
async def test_perform_check_failure(network_probe):
    with patch('src.core.network_probe.ping', return_value=None):
        result = await network_probe.perform_check()
        
        assert result['status'] == 'FAIL'
        assert result['latency'] is None
        assert result['packet_loss'] == 100
        assert isinstance(result['timestamp'], str)
        assert result['target'] == '8.8.8.8'

@pytest.mark.asyncio
async def test_perform_check_error(network_probe):
    with patch('src.core.network_probe.ping', side_effect=Exception("Test error")):
        result = await network_probe.perform_check()
        
        assert result['status'] == 'ERROR'
        assert 'error' in result
        assert result['error'] == "Test error"
        assert isinstance(result['timestamp'], str)
        assert result['target'] == '8.8.8.8'

@pytest.mark.asyncio
async def test_continuous_monitor(network_probe):
    with patch('src.core.network_probe.ping', return_value=0.1):
        network_probe._running = True
        counter = 0
        
        async for result in network_probe.continuous_monitor(interval=0.1):
            assert result['status'] == 'OK'
            assert result['latency'] == 100.0
            counter += 1
            if counter >= 2:  # İki veri noktası al
                network_probe.stop()
                break
        
        assert counter == 2

def test_stop(network_probe):
    network_probe._running = True
    network_probe.stop()
    assert not network_probe._running 