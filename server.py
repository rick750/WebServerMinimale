# -*- coding: utf-8 -*-
"""
Created on Thu May  8 17:24:21 2025

@author: Riccardo CARTA (riccardo.carta2@studio.unibo.it), Matricola 0001115294
"""

import socket
import os
import threading
import logging
from urllib.parse import unquote
import mimetypes

# Server configuration
HOST = '127.0.0.1'
PORT = 8080
FOLDER_ROOT = os.path.abspath('www')
# Configure basic logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s'
)

'''
Function to handle a single client
'''
def handle_client(conn, addr):
    data = conn.recv(1024)
    if not data:        # If no data, client has closed connection
        conn.close()
        return

    # Decode bytes to string, ignoring decoding errors
    request = data.decode(errors='ignore')
    # Extract the first line of the HTTP request
    first_line = request.split('\r\n', 1)[0]
    parts = first_line.split()
    if len(parts) < 2:       # Wrong request, it misses the method or the path
        conn.close()
        return
    method, raw_path = parts[0], parts[1]
    
    path = unquote(raw_path)
    if path == '/':
        path = '/index.html'
    full_path = os.path.abspath(os.path.join(FOLDER_ROOT, path.lstrip('/')))

    if os.path.isfile(full_path):
        # Read file content in binary mode
        with open(full_path, 'rb') as f:
            body = f.read()
        # Determine MIME type based on file extension, fallback to octet-stream
        mime_type, _ = mimetypes.guess_type(full_path)
        content_type = mime_type or 'application/octet-stream'

        # Build HTTP 200 OK response header
        header = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(body)}\r\n"
            "\r\n"
        ).encode()
        status = 200

    else:
        body = b'<h1>404 Not Found</h1>\
            <a href=\"/\">Go to Home<//a>'
        header = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(body)}\r\n"
            "\r\n"
        ).encode()
        status = 404

    conn.sendall(header + body)
    conn.close()
    logging.info(f"{addr} {method} {path} -> {status}")


def run():
    with socket.socket() as server_sock:
        # Socket set-up
        server_sock.bind((HOST, PORT))
        server_sock.listen()
        print(f"Serving on http://{HOST}:{PORT}")

        # Loop of execution
        while True:
            conn, addr = server_sock.accept()
            threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            ).start()


if __name__ == '__main__':
    run()  # Entry point: start the server
