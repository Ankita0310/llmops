
import subprocess
import time
import sys
import socket

from dotenv import load_dotenv
from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

load_dotenv()

HOST = "127.0.0.1"
PORT = 9999


def wait_for_backend(process, timeout=30):
    """Wait until backend is ready."""

    start_time = time.time()

    while time.time() - start_time < timeout:

        if process.poll() is not None:
            raise RuntimeError(
                "Backend process stopped unexpectedly"
            )

        try:
            with socket.create_connection(
                (HOST, PORT), timeout=1
            ):
                logger.info("Backend is ready!")
                return True

        except OSError:
            time.sleep(1)

    raise TimeoutError("Backend startup timed out")


def run_frontend():
    logger.info("Starting frontend service...")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app/frontend/ui.py"
        ],
        check=True
    )


if __name__ == "__main__":

    backend_process = None

    try:
        logger.info("Starting backend service...")

        backend_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.backend.api:app",
                "--host", HOST,
                "--port", str(PORT)
            ]
        )

        wait_for_backend(backend_process)

        logger.info("Starting frontend service...")

        run_frontend()

    except Exception as e:
        logger.exception(
            f"Application startup failed: {str(e)}"
        )

    finally:
        if backend_process and backend_process.poll() is None:
            logger.info("Stopping backend service...")
            backend_process.terminate()
            backend_process.wait(timeout=10)

        logger.info("Application stopped.")
