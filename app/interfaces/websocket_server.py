"""
WebSocket server for handling voice answer requests.
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List, Callable, Awaitable
import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)

class WebSocketServer:
    """WebSocket server for handling voice answer requests."""
    
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 8888,
        message_handler: Optional[Callable[[WebSocketServerProtocol, str], Awaitable[None]]] = None
    ) -> None:
        """
        Initialize the WebSocket server.
        
        Args:
            host (str): Host to bind the server to.
            port (int): Port to bind the server to.
            message_handler (Optional[Callable]): Async function to handle incoming messages.
        """
        self.host = host
        self.port = port
        self.server: Optional[websockets.WebSocketServer] = None
        self.message_handler = message_handler

    async def handle_client(self, websocket: WebSocketServerProtocol) -> None:
        """
        Handle a client connection.
        
        Args:
            websocket (WebSocketServerProtocol): The WebSocket connection.
        """
        try:
            async for message in websocket:
                try:
                    if self.message_handler:
                        await self.message_handler(websocket, message)
                    else:
                        logger.warning("No message handler defined")
                        await websocket.send(json.dumps({"error": "No message handler defined"}))
                        
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"error": "Invalid JSON format"}))
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    await websocket.send(json.dumps({"error": str(e)}))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client connection closed")
        except Exception as e:
            logger.error(f"Error handling client: {str(e)}")

    async def start(self) -> None:
        """Start the WebSocket server."""
        self.server = await websockets.serve(
            self.handle_client,
            self.host,
            self.port
        )
        logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
        await self.server.wait_closed()

    async def stop(self) -> None:
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("WebSocket server stopped")