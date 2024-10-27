from typing import Iterable, AsyncIterator


async def async_iterator(iterable: Iterable) -> AsyncIterator:
    for item in iterable:
        yield item
