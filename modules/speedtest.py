import threading
import time
import traceback
from helpers.config import SpeedrrConfig, SpeedtestTrackerConfig
from helpers.log_loader import logger
from helpers.bit_convert import bit_conv
from .speedtest_clients import get_client

class SpeedtestModule(threading.Thread):
    def __init__(self, config: SpeedrrConfig, tracker_config: SpeedtestTrackerConfig, update_event: threading.Event) -> None:
        threading.Thread.__init__(self)
        self._config = config
        self._tracker_config = tracker_config
        self._update_event = update_event
        self._client = get_client(tracker_config)
        self.daemon = True

    def run(self) -> None:
        logger.info("<speedtest_module> Starting speedtest tracker sync thread")
        while True:
            try:
                download_bits, upload_bits = self._client.get_latest_result()
                if download_bits is not None and upload_bits is not None:
                    # Convert to config units
                    new_max_download = int(round(bit_conv(download_bits, 'bit', self._config.units), 0))
                    new_max_upload = int(round(bit_conv(upload_bits, 'bit', self._config.units), 0))
                    
                    # Prevent setting speed limits to 0 or negative
                    new_max_download = max(1, new_max_download)
                    new_max_upload = max(1, new_max_upload)
                    
                    if new_max_download != self._config.max_download or new_max_upload != self._config.max_upload:
                        logger.info(
                            f"<speedtest_module> Speedtest update: "
                            f"max_download: {self._config.max_download} -> {new_max_download}{self._config.units}, "
                            f"max_upload: {self._config.max_upload} -> {new_max_upload}{self._config.units}"
                        )
                        # SpeedrrConfig is frozen=True, we use object.__setattr__ to bypass it
                        object.__setattr__(self._config, 'max_download', new_max_download)
                        object.__setattr__(self._config, 'max_upload', new_max_upload)
                        self._update_event.set()
            except Exception:
                logger.error("<speedtest_module> Error in speedtest sync loop:\n" + traceback.format_exc())
                
            time.sleep(self._tracker_config.update_interval)
