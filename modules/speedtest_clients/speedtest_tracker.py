import httpx
from typing import Tuple, Optional
from helpers.log_loader import logger
from .base import BaseSpeedtestClient

class SpeedtestTrackerClient(BaseSpeedtestClient):
    def get_latest_result(self) -> Tuple[Optional[float], Optional[float]]:
        if not self.config.url:
            logger.error("<speedtest_tracker> URL is missing in config.")
            return None, None

        # Try the public/unauthenticated widget endpoint first
        public_url = f"{self.config.url.rstrip('/')}/api/speedtest/latest"
        try:
            with httpx.Client() as client:
                res = client.get(public_url, timeout=10.0)
                if res.status_code == 200:
                    data = res.json()
                    result_data = data.get("data", {})
                    download = result_data.get("download")
                    upload = result_data.get("upload")
                    if download is not None:
                        download = float(download) * 1_000_000  # Convert Mbps to bps
                    if upload is not None:
                        upload = float(upload) * 1_000_000     # Convert Mbps to bps
                    return download, upload
        except Exception as e:
            logger.debug(f"<speedtest_tracker> Public endpoint check failed: {e}")

        # Fallback to the authenticated API v1 endpoint
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
