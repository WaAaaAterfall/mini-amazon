from amazon_server import *

if __name__ == '__main__':
    engine = connectDB()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', PORT))
    sock.listen(100)
    web_fd, addr = sock.accept()
    session = getSession(engine)
    process_order(web_fd,session)

