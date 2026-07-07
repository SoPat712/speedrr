from .speedtest_tracker import SpeedtestTrackerClient
from .librespeed_api import LibreSpeedAPIClient
from .sqlite_client import SQLiteClient

def get_client(config):
    if config.type == 'speedtest-tracker':
        return SpeedtestTrackerClient(config)
    elif config.type == 'librespeed-api':
        return LibreSpeedAPIClient(config)
    elif config.type == 'sqlite':
        return SQLiteClient(config)
    else:
        raise ValueError(f"Unknown speedtest tracker type: {config.type}")
