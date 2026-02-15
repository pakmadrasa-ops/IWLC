# main.py
import wifi, relay, web, socket
from config import HTTP_PORT

relay.init()

if not wifi.connect():
    wifi.start_ap()

s = socket.socket()
s.bind(("0.0.0.0", HTTP_PORT))
s.listen(1)

while True:
    conn, _ = s.accept()
    raw = conn.recv(4096)
    req = raw.decode(errors="ignore")
    method, path, _ = req.split(" ", 2)
    web.handle(conn, method, path, raw)
    conn.close()
