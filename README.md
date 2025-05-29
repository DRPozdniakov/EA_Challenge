# Voice Service & WebSocket Audio Client

This project provides a **Voice Service** (server) that answers questions using LLM and TTS, and a **WebSocket Audio Client** (client) with a user-friendly Gradio interface for sending questions and receiving audio responses.

---

## Project Structure

```
/app/         # Server-side code (runs in Docker)
  /service/
  /instances/
  /logs/      # Server logs (including memory log)
  ...
/client/      # Client-side code (run natively)
  tcp_client.py
  requirements.txt
  /logs/      # Client logs
docker-compose.yml
requirements.txt   # Server dependencies
```

---

## How to Run

### 1. Start the Voice Service (Server) in Docker

From the project root, run:
```sh
docker-compose up --build -d
```
- The server will listen for WebSocket connections on port **8888**.
- The server logs (including memory log) are stored in `app/logs/voice_service.log` (and other log files in `app/logs/`).

### 2. Start the WebSocket Audio Client (on your host OS)

Open a new terminal, then:
```sh
cd client
pip install -r requirements.txt
python tcp_client.py
```
- The client UI will open in your browser as a small Gradio interface.
- By default, it connects to `ws://localhost:8888`. If running the client on another machine, use the host's LAN IP and port 8888.

---

- Otherwise client folder can be launches on the remote machine as it is.
- Due limitations to work with Audio files from containers client is present in python files instance.

## WebSocket Architecture

- **WebSocket-based communication:** The client and server communicate using the WebSocket protocol, which allows for efficient, real-time, bi-directional messaging.
- **No end markers needed:** Each message (question or audio response) is sent as a complete WebSocket message, so there is no need for manual message framing or end markers.
- **Binary audio transfer:** The server sends audio responses as binary WebSocket messages, which the client saves and plays back.

---

## Voice Service Memory Log

- The server keeps a memory log of all interactions and events in `app/logs/voice_service.log`.
- This log is useful for debugging, auditing, and tracking the conversation history and server activity.

## Test conversation 

For testing service capabilities you can run the following dialog
- "Today date is 29.05.2025"
- "Your name is Lora"
- "Can you present yourself and tell me what is the date today?"
---

## Notes

- **Server and client are fully decoupled:** The server runs in Docker, the client runs natively for best audio playback.
- **No audio playback in Docker:** The server does not attempt to play audio; playback is handled by the client on your host OS.
- **Port configuration:** Ensure port 8888 is open and not blocked by your firewall.
- **WebSocket protocol:** All communication is now handled via WebSockets for modern, real-time, and cross-platform compatibility.
