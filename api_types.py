from dataclasses import dataclass, field
from enum import Enum

### http://auth.mconly.net/serverauth/a.php
@dataclass
class Session:
    unused: int
    unused2: int
    username: str
    session: str
    unk: str
    md5hash: str
    authhash: str
    launcher_hash: str
    checkh_hash: str

### http://auth.mconly.net/launcher/getServers.php
@dataclass
class Servers_Server:
    name: str
    type: str
    ip: str
    another_ips_str: str
    port_str: str
    launch_type: int
    newJava: Optional[str] = None
    java_version_str: str = "8"

    port: int = field(default_factory=int)
    another_ips: list[str] = field(default_factory=list)
    java_version: int = field(default_factory=int)

    def __post_init__(self):
        self.another_ips = self.another_ips_str.split(";")
        self.port = int(self.port_str)
        self.java_version = int(self.java_version_str)


### http://auth.mconly.net/serverauth/updates.php
class UpdateType(Enum):
    FileExists = 0
    VerifyHash = 1
    Optional = 2


@dataclass
class Updater_Entry:
    path: str
    md5: str
    type: UpdateType
