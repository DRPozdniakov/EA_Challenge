from app.services.service_voice_answer import VoiceAnswerService
import logging
import asyncio

if __name__ == "__main__":
    # Configure logging
    log_file = "./app/logs/voice_service.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger(__name__)
    voice_answer = VoiceAnswerService(logger)
    asyncio.run(voice_answer.run())