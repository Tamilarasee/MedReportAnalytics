#!/usr/bin/env python
import socket
from app import app
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def find_available_port(preferred=5000):
    """
    Try binding to the preferred port. If it's in use, find a free one.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(('', preferred))
            return preferred
        except OSError:
            sock.bind(('', 0))  # Bind to any free port
            free_port = sock.getsockname()[1]
            logger.warning(
                f"Port {preferred} in use. Falling back to port {free_port}")
            return free_port


if __name__ == '__main__':
    port = find_available_port(8080)
    app.run(host='0.0.0.0', port=port, debug=True)
