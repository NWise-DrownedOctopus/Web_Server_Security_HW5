"""
simple_web_server.py
Translation of SimpleWebServer.java for CS 483/5583 HW5.
Supports GET and PUT commands over a raw TCP socket (not full HTTP).
"""

import socket
import os
import datetime

PORT = 8080
MAX_FILE_SIZE = 50 * 1024  # 50 KB  (Question 3)


def log_entry(filename: str, record: str) -> None:
    """Append a timestamped record to a log file. (Question 2)"""
    with open(filename, "a") as f:
        f.write(f"{datetime.datetime.now()} {record}\n")


def serve_file(conn: socket.socket, pathname: str) -> None:
    """Send a file to the client, enforcing a max size limit. (Question 3)"""

    # Strip leading slash
    if pathname.startswith("/"):
        pathname = pathname[1:]

    # Default to index.html
    if pathname == "":
        pathname = "index.html"

    # Question 3 – enforce max file size
    if os.path.exists(pathname):
        file_size = os.path.getsize(pathname)
        if file_size > MAX_FILE_SIZE:
            log_entry(
                "error_log.txt",
                f"{pathname} exceeds max size limit: {MAX_FILE_SIZE}"
            )
            conn.sendall(b"HTTP/1.0 403 Forbidden\n\n")
            return

    try:
        with open(pathname, "rb") as f:
            data = f.read()
        conn.sendall(b"HTTP/1.0 200 OK\n\n")
        conn.sendall(data)
    except FileNotFoundError:
        conn.sendall(b"HTTP/1.0 404 Not Found\n\n")


def store_file(conn: socket.socket, pathname: str, file_content: str) -> None:
    """Save uploaded file content to pathname. (Question 2)"""
    try:
        with open(pathname, "w") as f:
            f.write(file_content)
        conn.sendall(b"HTTP/1.0 201 Created\n\n")
        print(f"{pathname} is saved!")
    except Exception as e:
        print(f"Error saving file: {e}")
        conn.sendall(b"HTTP/1.0 500 Internal Server Error\n\n")


def process_request(conn: socket.socket) -> None:
    """Read one request from the client and dispatch to the right handler."""
    with conn:
        # Read all data sent by the client
        raw = b""
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            raw += chunk

        if not raw:
            return

        text = raw.decode("utf-8", errors="replace")
        lines = text.splitlines()

        if not lines:
            return

        first_line = lines[0].strip()
        print(first_line)

        parts = first_line.split(" ", 2)
        if len(parts) < 2:
            conn.sendall(b"HTTP/1.0 400 Bad Request\n\n")
            return

        command = parts[0]
        pathname = parts[1]

        log_entry("log.txt", f"{command} {pathname}")

        if command == "GET":
            print(f"Path name: {pathname}")
            serve_file(conn, pathname)

        elif command == "PUT":
            print(f"Path name: {pathname}")
            # Everything after the first line is the file content
            file_content = "\n".join(lines[1:])
            store_file(conn, pathname, file_content)

        else:
            conn.sendall(b"HTTP/1.0 501 Not Implemented\n\n")


def run() -> None:
    """Start the server and accept connections forever."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("", PORT))
        server.listen(5)
        print(f"Server listening on port {PORT} ...")

        while True:
            conn, addr = server.accept()
            print(f"Connection from {addr}")
            process_request(conn)


if __name__ == "__main__":
    run()