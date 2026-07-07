import httpx
from typing import Tuple, Optional
from helpers.log_loader import logger
from .base import BaseSpeedtestClient

class LibreSpeedAPIClient(BaseSpeedtestClient):
    def get_latest_result(self) -> Tuple[Optional[float], Optional[float]]:
        if not self.config.url:
            logger.error("<librespeed-api> URL is missing in config.")
            return None, None

        headers = {"Accept": "application/json"}
        if self.config.api_key:
            headers["X-API-Key"] = self.config.api_key

        try:
            with httpx.Client() as client:
                res = client.get(self.config.url, headers=headers, timeout=10.0)
                res.raise_for_status()
                data = res.json()
                
                # Check different common telemetry result formats
                # LibreSpeed commonly stores dl and ul as strings representing Mbps
                dl = data.get("dl") or data.get("download")
                ul = data.get("ul") or data.get("upload")
                
                if dl is None or ul is None:
                    logger.error(f"<librespeed-api> Invalid response format: {data}")
                    return None, None
                
                # Convert Mbps to bits/sec
                download = float(dl) * 1_000_000
                upload = float(ul) * 1_000_000
                
                return download, upload
        except Exception as e:
            logger.error(f"<librespeed-api> Error fetching latest result from LibreSpeed API: {e}")
            return None, None
