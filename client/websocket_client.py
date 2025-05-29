"""
TCP Audio Client (WebSocket version)
-----------------------------------
A Gradio-based client for sending questions to a WebSocket server and receiving audio responses.
"""
import logging
import tempfile
import gradio as gr
import websockets

class WebSocketClient:
    """
    WebSocketClient handles sending questions to a WebSocket server and receiving audio responses.
    """
    def __init__(self, host='localhost', port=8888, logger=None):
        """
        Initialize the WebSocketClient.

        Args:
            host (str): Server host address.
            port (int): Server port.
            logger (logging.Logger): Logger instance.
        """
        self.host = host
        self.port = port
        self.logger = logger

    async def send_question(self, question):
        """
        Send a question to the server and receive the audio response (as binary).
        """
        uri = f"ws://{self.host}:{self.port}"
        try:
            async with websockets.connect(uri, max_size=None) as websocket:
                # 1. Receive the text from the UI and sends it to the server
                await websocket.send(question)
                self.logger.info(f"Sent question: {question}")
                # 2. Receive the audio from the server
                audio_data = await websocket.recv()  # Should be bytes
                self.logger.info(f"Received audio data: {len(audio_data)} bytes")
                # 3. Receives the audio data and provides for it for playing in the UI.
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                    temp_file.write(audio_data)
                    return temp_file.name
        except Exception as e:
            self.logger.error(f"WebSocket error: {str(e)}")
            return None

    async def send_message(self, message, host, port):
        """
        Send a message to the server and get the audio response.

        Args:
            message (str): The message to send.
            host (str): Server host.
            port (int): Server port.

        Returns:
            tuple: (status message, audio file path or None)
        """
        try:
            # Update client connection details
            self.host = host
            self.port = int(port)
            
            # Send message and get audio response
            audio_file = await self.send_question(message)
            if audio_file:
                return "Message sent successfully! Playing audio response.", audio_file
            else:
                return "Error: Failed to get audio response", None
        except Exception as e:
            return f"Error: {str(e)}", None

    def create_ui(self):
        """
        Create and return the Gradio interface for the client.

        Returns:
            gr.Blocks: The Gradio interface.
        """
        # Create Gradio interface
        with gr.Blocks(title="WebSocket Audio Client") as interface:
            gr.Markdown("# WebSocket Audio Client")
            
            with gr.Row():
                with gr.Column(scale=1):
                    message_input = gr.Textbox(
                        label="Message",
                        placeholder="Enter your message here...",
                        lines=3
                    )
                    with gr.Row():
                        host_input = gr.Textbox(
                            label="Server Host",
                            value=self.host,
                            placeholder="Enter server host (e.g., localhost)"
                        )
                        port_input = gr.Textbox(
                            label="Server Port",
                            value=str(self.port),
                            placeholder="Enter server port"
                        )
                    send_button = gr.Button("Send Message")
                with gr.Column(scale=1.0):
                    status_output = gr.Textbox(label="Status", lines=1, scale=1)
                    audio_output = gr.Audio(
                        label="Response Audio",
                        autoplay=True,
                        scale=2
                    )
            
            send_button.click(
                fn=self.send_message,
                inputs=[message_input, host_input, port_input],
                outputs=[status_output, audio_output]
            )

        return interface


def main():
    """
    Entry point for running the WebSocket Audio Client UI.
    """
    # Configure logging to file
    log_file = "client/logs/tcp_client.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # This will also show logs in console
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting WebSocket Client...")
    
    # Create client and launch UI
    client = WebSocketClient(logger=logger)
    interface = client.create_ui()
    interface.launch()


if __name__ == "__main__":
    main() 