import sys
import AtmServer


if __name__ == '__main__':
    server = AtmServer.Server(host="0.0.0.0", port=56789)
    try:
        server.start()
    except KeyboardInterrupt:
        print("Server is shutting down...")
        server.stop()
    finally:
        sys.exit(0)
