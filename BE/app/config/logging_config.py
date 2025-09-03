
import logging
import sys

def setup_logging():
    """
    애플리케이션을 위한 표준 로깅을 설정합니다.
    """
    logger = logging.getLogger("MyChat")
    logger.setLevel(logging.INFO)

    # 이미 핸들러가 설정되어 있다면 중복 추가 방지
    if logger.hasHandlers():
        logger.handlers.clear()

    # 포매터 설정
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 콘솔 핸들러 설정
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger

# 전역 로거 인스턴스
logger = setup_logging()
