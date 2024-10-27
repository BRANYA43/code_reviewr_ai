from typing import Iterable


async def async_iterator(iterable: Iterable):
    for item in iterable:
        yield item
