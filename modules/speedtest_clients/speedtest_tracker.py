import httpx
from typing import Tuple, Optional
from helpers.log_loader import logger
from .base import BaseSpeedtestClient

class SpeedtestTrackerClient(BaseSpeedtestClient):
    def get_latest_result(self) -> Tuple[Optional[float], Optional[float]]:
        if not self.config.url:
            logger.error("<speedtest_tracker> URL is missing in config.")
            return None, None

        url = f"{self.config.url.rstrip('/')}/api/v1/results/latest"
        headers = {"Accept": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        try:
            with httpx.Client() as client:
                res = client.get(url, headers=headers, timeout=10.0)
                if res.status_code == 404:
                    logger.debug("<speedtest_tracker> No speedtest results found on server.")
                    return None, None
                res.raise_for_status()
                data = res.json()
                
                result_data = data.get("data", {})
                download = result_data.get("download")  # bits/sec
                upload = result_data.get("upload")      # bits/sec
                
                if download is not None:
                    download = float(download)
                if upload is not None:
                    upload = float(upload)
                    
                return download, upload
        except Exception as e:
            logger.error(f"<speedtest_tracker> Error fetching latest result from Speedtest Tracker: {e}")
            return None, None
