import json
import logging
from fastapi import WebSocket, WebSocketDisconnect

from truedhwani.pipeline.stream_orchestrator import StreamPipelineOrchestrator

logger = logging.getLogger(__name__)


async def handle_websocket_stream(websocket: WebSocket, orchestrator: StreamPipelineOrchestrator):
    """
    Handle live audio WebSocket streaming session.
    Accepts raw binary PCM 16-bit 16kHz audio or JSON control commands.
    Streams real-time analysis packets in JSON format back to the client.
    """
    await websocket.accept()
    orchestrator.reset()
    logger.info("WebSocket client connected to TrueDhwani stream.")

    try:
        while True:
            message = await websocket.receive()

            if message.get("type") == "websocket.disconnect":
                logger.info("Client sent websocket disconnect.")
                break

            # Handle binary PCM audio data
            if "bytes" in message and message["bytes"]:
                pcm_bytes = message["bytes"]
                packets = await orchestrator.ingest_pcm_chunk(pcm_bytes)
                for pkt in packets:
                    await websocket.send_json(pkt.to_dict())

            # Handle text/control frames
            elif "text" in message and message["text"]:
                text_data = message["text"].strip()
                try:
                    cmd = json.loads(text_data)
                    action = cmd.get("action")
                    if action == "reset":
                        orchestrator.reset()
                        await websocket.send_json({"status": "reset_complete"})
                    elif action == "flush":
                        last_packet = await orchestrator.flush()
                        if last_packet:
                            await websocket.send_json(last_packet.to_dict())
                        await websocket.send_json({"status": "stream_flushed"})
                    else:
                        await websocket.send_json({"error": f"Unknown action: {action}"})
                except json.JSONDecodeError:
                    await websocket.send_json({"error": "Invalid JSON control message"})

    except (WebSocketDisconnect, RuntimeError):
        logger.info("WebSocket client disconnected normally.")
    except Exception as e:
        logger.error(f"WebSocket session error: {e}", exc_info=True)
