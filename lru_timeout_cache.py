import asyncio
from collections import OrderedDict


class LRUTimeoutCache:
    def __init__(self, size, timeout):
        self.event_loop = asyncio.get_event_loop()
        self.cache = OrderedDict()
        self.maxSize = size
        self.timeout = timeout

    def get_all(self):
        return self.cache

    def has_item(self, key):
        return key in self.cache

    def get_item(self, key):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        item = self.cache[key]
        self._update_timer(item, key)
        return item["data"]

    def put_item(self, key, item):
        if key in self.cache:
            existing_item = self.cache[key]
            existing_item["timer"].cancel()
            existing_item["timer"] = None

        cache_item = {
            "timer": None,
            "data": item
        }

        self._update_timer(cache_item, key)
        self.cache[key] = cache_item
        self.cache.move_to_end(key)

        if len(self.cache) > self.maxSize:
            removed_item = self.cache.popitem(last=False)
            removed_item["timer"].cancel()
            removed_item["timer"] = None
            return removed_item["data"]

    def _update_timer(self, item, key):
        timer = item["timer"]
        if timer is not None:
            timer.cancel()
        item["timer"] = self.event_loop.call_later(self.timeout, self._delete_outdated,key)

    def _delete_outdated(self, key):
        del self.cache[key]

    def pop_item(self):
        removed_item = self.cache.popitem(last=True)
        removed_item["timer"].cancel()
        removed_item["timer"] = None
        return removed_item["data"]
