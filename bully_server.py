import socket
import threading

port = 1250
header = 64

# server = '192.168.175.1'
s = socket.gethostbyname(socket.gethostname())
ADDR = (s, port)

disconnect_message = 'DISCONNECTING!'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    server.bind(ADDR)
except socket.error as e:
    print(str(e))


messages = list()


def client_handler(conn, addr):
    print(f'{addr} connected.\n')
    connected = True

    while connected:

        if len(messages) > 0:

            conn.sendall(messages[0].encode('utf-8'))
            messages.clear()
            connected=False

        else:
            message_length = conn.recv(header).decode('utf-8')

            if message_length:
                l = int(message_length)
                message = conn.recv(l).decode('utf-8')
                if message == disconnect_message:
                    connected = False
                else:
                    messages.append(message)
                    connected=False

    conn.close()


def start():
    server.listen()

    print('Server is listening on:', s)

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=client_handler, args=(conn, addr))

        thread.start()
        print(f'[ACTIVE CONNECTIONS:]  {threading.activeCount() - 1}')


print('server is starting...\n')
start()
