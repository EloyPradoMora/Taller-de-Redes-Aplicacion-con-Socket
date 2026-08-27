import argparse
import logging
import socket
import sys
import threading

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("server")

# Tamaño máximo de un mensaje aceptado, para evitar datos maliciosos
MAX_LINE_BYTES = 1024

VALID_COMMANDS = {"INCREMENT", "GET"}

class Counter:
    #Tiene lock para evitar condicion de carrera
    def __init__(self) -> None:
        self._value = 0
        self._lock = threading.Lock()

    def increment(self) -> int:
        with self._lock:
            self._value += 1
            return self._value

    def get(self) -> int:
        with self._lock:
            return self._value


def recv_line(conn: socket.socket) -> str:
    #Por si el cliente trata de mandar algo nada que ver
    buffer = b""
    while b"\n" not in buffer:
        if len(buffer) >= MAX_LINE_BYTES:
            raise ValueError("mensaje demasiado largo")
        chunk = conn.recv(64)
        if not chunk:
            if buffer:
                raise ConnectionError("conexión cerrada a mitad de mensaje")
            raise ConnectionError("cliente cerró la conexión")
        buffer += chunk
    line, _, _rest = buffer.partition(b"\n")
    return line.decode("utf-8", errors="strict").strip()


def handle_client(conn: socket.socket, addr: tuple, counter: Counter) -> None:
    #Atiende una conexión de cliente en su propio hilo.
    log.info("Cliente conectado: %s:%s", addr[0], addr[1])
    try:
        with conn:
            while True:
                try:
                    line = recv_line(conn)
                except ConnectionError:
                    # Cliente cerró la conexión de forma normal.
                    break
                except (ValueError, UnicodeDecodeError) as exc:
                    log.warning("Mensaje inválido de %s: %s", addr, exc)
                    conn.sendall(f"ERROR {exc}\n".encode("utf-8"))
                    break

                if not line:
                    conn.sendall(b"ERROR mensaje vacio\n")
                    continue

                command = line.strip().upper()

                if command == "INCREMENT":
                    value = counter.increment()
                    log.info("INCREMENT de %s -> contador=%d", addr, value)
                    conn.sendall(f"OK {value}\n".encode("utf-8"))

                elif command == "GET":
                    value = counter.get()
                    log.info("GET de %s -> contador=%d", addr, value)
                    conn.sendall(f"OK {value}\n".encode("utf-8"))

                else:
                    log.warning("Comando desconocido de %s: %r", addr, command)
                    conn.sendall(
                        f"ERROR comando desconocido: {command}\n".encode("utf-8")
                    )

            # Cierre ordenado del lado de escritura antes de cerrar el socket.
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except OSError:
                # Puede fallar si el peer ya cerró su lado. No es fatal.
                pass

    except OSError as exc:
        log.error("Error de socket con %s: %s", addr, exc)
    finally:
        log.info("Cliente desconectado: %s:%s", addr[0], addr[1])


def run_server(host: str, port: int) -> None:
    counter = Counter()
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_sock.bind((host, port))
        server_sock.listen(5)
        log.info("Servidor TCP escuchando en %s:%d", host, port)

        while True:
            try:
                conn, addr = server_sock.accept()
            except OSError as exc:
                log.error("Error en accept(): %s", exc)
                continue

            thread = threading.Thread(
                target=handle_client, args=(conn, addr, counter), daemon=True
            )
            thread.start()

    except KeyboardInterrupt:
        log.info("Apagando servidor (Ctrl+C)...")
    except OSError as exc:
        log.error("No se pudo iniciar el servidor: %s", exc)
        sys.exit(1)
    finally:
        server_sock.close()
        log.info("Socket del servidor cerrado.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Servidor TCP - contador de clicks")
    parser.add_argument("--host", default="0.0.0.0", help="IP a escuchar (default 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5050, help="Puerto a escuchar (default 5050)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_server(args.host, args.port)