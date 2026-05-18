import asyncio
import json
from typing import Any


class SSEManager:
    def __init__(self) -> None:
        self._clients: list[asyncio.Queue[str]] = []

    def register(self) -> asyncio.Queue[str]:
        queue: asyncio.Queue[str] = asyncio.Queue()
        self._clients.append(queue)
        return queue

    def unregister(self, queue: asyncio.Queue[str]) -> None:
        if queue in self._clients:
            self._clients.remove(queue)

    async def broadcast(self, event: dict[str, Any]) -> None:
        payload = json.dumps(event)
        for queue in list(self._clients):
            await queue.put(payload)


sse_manager = SSEManager()
