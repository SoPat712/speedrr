from typing import Tuple, Optional

class BaseSpeedtestClient:
    def __init__(self, config) -> None:
        self.config = config

    def get_latest_result(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Get the latest download and upload speed.
        Returns a tuple of (download, upload) in bits/sec, or (None, None) on failure/no results.
        """
        raise NotImplementedError()
