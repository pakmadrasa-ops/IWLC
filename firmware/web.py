# web.py
import relay, uos

def send(conn, path, ctype="text/html"):
    try:
        with open(path,"rb") as f:
            conn.send("HTTP/1.1 200 OK\r\nContent-Type: "+ctype+"\r\n\r\n")
            conn.sendall(f.read())
    except:
        conn.send("HTTP/1.1 404 NOT FOUND\r\n\r\n")

def handle(conn, method, path, raw):
    if path == "/" or path == "/index.html":
        send(conn,"www/index.html")
    elif path == "/relay/on":
        relay.set(1); send(conn,"www/index.html")
    elif path == "/relay/off":
        relay.set(0); send(conn,"www/index.html")
    elif path == "/update":
        send(conn,"www/update.html")
    else:
        send(conn,"www/index.html")
