from dataclasses import dataclass, field
from typing import List, Optional, Union, Literal
try:
    from dataclass_wizard import YAMLWizard # type: ignore
except ImportError:
    from dataclass_wizard.mixins.yaml import YAMLWizard # type: ignore


@dataclass(frozen=True)
class ClientConfig(YAMLWizard):
    type: Literal['qbittorrent', 'deluge', 'transmission']
    url: str
    username: str
    password: str
    https_verify: bool
    download_shares: int = 1
    upload_shares: int = 1


@dataclass(frozen=True)
class IgnoreStreamConfig(YAMLWizard):
    local: bool
    ip_networks: Optional[tuple[str, ...]]
    paused_after: int

@dataclass(frozen=True)
class StreamBasedSpeedsConfig(YAMLWizard):
    enabled: bool
    speeds: dict[int, Union[int, float, str]]
    default: Optional[Union[int, float, str]] = None

@dataclass(frozen=True)
class MediaServerConfig(YAMLWizard):
    type: Literal['plex', 'tautulli', 'jellyfin', 'emby']
    url: str
    https_verify: bool
    bandwidth_multiplier: float
    update_interval: int
    ignore_streams: IgnoreStreamConfig
    token: Optional[str] = None
    api_key: Optional[str] = None
    stream_based_speeds: Optional[StreamBasedSpeedsConfig] = None
    download_reduction_multiplier: float = 0.0

    def __hash__(self) -> int:
        return super().__hash__()

@dataclass(frozen=True)
class ScheduleConfig(YAMLWizard):
    start: str
    end: str
    days: tuple[Literal['all', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'], ...]
    upload: Union[int, str]
    download: Union[int, str]

@dataclass(frozen=True)
class ModulesConfig(YAMLWizard):
    media_servers: Optional[List[MediaServerConfig]]
    schedule: Optional[List[ScheduleConfig]]

@dataclass(frozen=True)
class SpeedtestTrackerConfig(YAMLWizard):
    enabled: bool
    type: Literal['speedtest-tracker', 'librespeed-api', 'sqlite']
    url: Optional[str] = None
    api_key: Optional[str] = None
    database_path: Optional[str] = None
    query: Optional[str] = None
    download_column: Optional[str] = None
    upload_column: Optional[str] = None
    speed_unit: Optional[str] = 'bit'
    update_interval: int = 300

@dataclass(frozen=True)
class SpeedrrConfig(YAMLWizard):
    logs_path: Optional[str]
    units: Literal[
        'bit',
        'B',
        'byte',
        'Kbit',
        'kilobit',
        'Kibit',
        'kibibit',
        'KB',
        'kilobyte',
        'KiB',
        'kibibyte',
        'Mbit',
        'megabit',
        'Mibit',
        'mebibit',
        'MB',
        'megabyte',
        'MiB',
        'mebibyte',
        'Gbit',
        'gigabit',
        'Gibit',
        'gibibit',
        'GB',
        'gigabyte',
        'GiB',
        'gibibyte',
    ]
    min_upload: int
    max_upload: int
    min_download: int
    max_download: int
    clients: List[ClientConfig]
    modules: ModulesConfig
    manual_speed_algorithm_share: Optional[bool] = False
    speedtest_tracker: Optional[SpeedtestTrackerConfig] = None

def load_config(config_file: str) -> SpeedrrConfig:
    config = SpeedrrConfig.from_yaml_file(config_file)
    if isinstance(config, list):
        raise ValueError("Config can't be a list")
    return config
