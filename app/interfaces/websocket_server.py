import asyncio
import websockets
import logging

class WebSocketServer:
    def __init__(self, host='0.0.0.0', port=8888, logger=None, handler=None):
        self.host = host
        self.port = port
        self.logger = logger or logging.getLogger(__name__)
        self.handler = handler  # This should be a coroutine function

    async def _ws_handler(self, websocket):
        async for message in websocket:
            if self.handler:
                await self.handler(websocket, message)
            else:
                self.logger.warning("No handler defined for incoming messages.")

    async def start(self):
        self.logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
        async with websockets.serve(self._ws_handler, self.host, self.port, max_size=None):
            await asyncio.Future()  # Run forever