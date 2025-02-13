import json
import sqlite3
import time
from asyncio import Lock
from typing import Dict, Optional, List

from attr import dataclass


@dataclass
class GeoLocation:
    country: str
    region: str
    city: str
    lat: float
    lon: float


@dataclass
class AttackerInfo:
    timestamp: str
    ip: str
    mac: str
    hostname: Optional[str]
    open_ports: List[int]
    geolocation: Optional[GeoLocation]
    isp: Optional[str]
    tor_exit_node: bool
    vpn_detected: bool
    whois: Optional[Dict]
    network_stats: Optional[Dict]
    shodan_info: Optional[Dict]


class Cache:
    def __init__(self, db_path="cache.db"):
        self.db_path = db_path
        self.lock = Lock()
        self.init_db()

    def init_db(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ip_cache (
                    ip TEXT PRIMARY KEY,
                    data TEXT,
                    timestamp FLOAT
                )
            """)

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def get(self, ip: str, max_age: int = 3600) -> Optional[Dict]:
        with self.lock:
            with self.get_connection() as conn:
                result = conn.execute(
                    "SELECT data, timestamp FROM ip_cache WHERE ip = ?",
                    (ip,)
                ).fetchone()

                if result and (time.time() - result[1]) < max_age:
                    return json.loads(result[0])
        return None

    def set(self, ip: str, data: Dict):
        with self.lock:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO ip_cache (ip, data, timestamp) VALUES (?, ?, ?)",
                    (ip, json.dumps(data), time.time())
                )
