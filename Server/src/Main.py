import sys
from Controller import handle_client
from Server import Server

if __name__ == '__main__':
    server = Server(host="127.0.0.1", port=56789, handler=handle_client)
    try:
        server.start()
    except Exception as e:
        print(str(e))
        server.stop()
    finally:
        sys.exit(0)
