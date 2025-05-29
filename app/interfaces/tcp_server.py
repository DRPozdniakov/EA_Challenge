"""
tcp_server.py
-------------
TCP server for handling client connections and sending/receiving messages.
"""

import asyncio
import logging
import json


class TCPServer:
    """
    TCPServer handles incoming TCP connections, receives messages, and sends responses.
    """
    def __init__(self, host='localhost', port=8888, logger=None):
        """
        Initialize the TCPServer.

        Args:
            host (str): Host address to bind the server.
            port (int): Port to listen on.
            logger (logging.Logger): Logger instance.
        """
        self.host = host
        self.port = port
        self.logger = logger
        self.server = None
        self.is_running = False
        self.received_message = None
        self.client_address = None
        self.client_writer = None
        
    async def handle_client(self, reader, writer):
        """
        Handle individual client connections.

        Args:
            reader (StreamReader): Stream reader for the client.
            writer (StreamWriter): Stream writer for the client.
        """
        try:
            self.client_address = writer.get_extra_info('peername')
            self.client_writer = writer
            self.logger.info(f"New client connected from {self.client_address}")
            
            # Read the message from client
            data = await reader.read(1024*1024)  # Read up to 1MB
            if not data:
                self.logger.warning("No data received from client")
                return
                
            # Parse the message
            message = data.decode().strip()
            self.logger.info(f"Received message: {message}")
            
            # Store the message for processing
            self.received_message = message
            
            # Wait for the response to be sent
            while self.client_writer is not None:
                await asyncio.sleep(0.1)
            
        except Exception as e:
            self.logger.error(f"Error handling client: {str(e)}")
        finally:
            writer.close()
            await writer.wait_closed()
            self.logger.info("Client connection closed")

    def send_message(self, answer, address=None):
        """
        Send a message back to the client.

        Args:
            answer (bytes or str): The answer to send (can be text or binary data).
            address: The client address (optional).

        Returns:
            bool: True if message was sent successfully, False otherwise.
        """
        try:
            if self.client_writer and (address is None or address == self.client_address):
                # If answer is string, encode it, otherwise send as is (for binary data)
                data = answer.encode() if isinstance(answer, str) else answer
                self.logger.info(f"Sending data: {len(data)} bytes")
                
                # Send data in chunks to ensure all data is sent
                chunk_size = 1024 * 1024  # 1MB chunks
                for i in range(0, len(data), chunk_size):
                    chunk = data[i:i + chunk_size]
                    self.client_writer.write(chunk)
                    asyncio.create_task(self.client_writer.drain())
                
                # Send end marker
                end_marker = b"<END_OF_AUDIO>"
                self.client_writer.write(end_marker)
                asyncio.create_task(self.client_writer.drain())
                
                self.logger.info(f"Data and end marker sent to client {self.client_address}")
                
                # Clear client state after sending
                self.client_writer = None
                self.client_address = None
                self.received_message = None
                
                return True
            else:
                self.logger.warning(f"No active client connection for address {address}")
                return False
        except Exception as e:
            self.logger.error(f"Error sending message: {str(e)}")
            return False

    async def start(self):
        """
        Start the TCP server and listen for connections.
        """
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        
        self.is_running = True
        self.logger.info(f"Server started on {self.host}:{self.port}")
        
        async with self.server:
            await self.server.serve_forever()

    async def stop(self):
        """
        Stop the TCP server.
        """
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.is_running = False
            self.logger.info("Server stopped")


if __name__ == "__main__":
    """
    Entry point for running the TCPServer as a standalone script.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    
    # Create and start server
    server = TCPServer(logger=logger)
    asyncio.run(server.start()) 