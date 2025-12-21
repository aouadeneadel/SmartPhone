# utils/cache.py
from time import time


class TimedCache:
    """
    Cache avec expiration optionnelle (TTL)
    """
    def __init__(self, ttl=None):
        self.ttl = ttl      # en secondes (None = infini)
        self._data = {}

    def get(self, key, default=None):
        item = self._data.get(key)
        if not item:
            return default

        value, timestamp = item

        if self.ttl is not None and (time() - timestamp) > self.ttl:
            self._data.pop(key, None)
            return default

        return value

    def set(self, key, value):
        self._data[key] = (value, time())

    def clear(self):
        self._data.clear()

    def __contains__(self, key):
        return key in self._data


class Cache:
    """
    Cache central de l'application
    """
    def __init__(self):
        # packages : com.example.app -> dict infos
        self.apps = {}

        # propriétés getprop
        self.props = TimedCache(ttl=60)

        # infos device (RAM, stockage, batterie)
        self.device = TimedCache(ttl=30)

        # résultats adb génériques
        self.adb = TimedCache(ttl=10)

    def clear_all(self):
        self.apps.clear()
        self.props.clear()
        self.device.clear()
        self.adb.clear()


# instance unique (singleton simple)
cache = Cache()
