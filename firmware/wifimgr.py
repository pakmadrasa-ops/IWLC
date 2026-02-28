import network
import socket
import ure
import time
import ujson
import gc

AP_SSID = "MotorSetup"
AP_PASSWORD = "12345678"
AP_AUTHMODE = 3  # WPA2

NETWORK_PROFILES = 'wifi.json'
AP_TIMEOUT = 300  # seconds, AP mode auto-disable
CONNECT_TIMEOUT = 15  # seconds

wlan_ap = network.WLAN(network.AP_IF)
wlan_sta = network.WLAN(network.STA_IF)

server_socket = None

# ==========================
# WiFi connection functions
# ==========================
def get_connection():
    """Return a connected STA interface or start AP for configuration"""
    if wlan_sta.isconnected():
        return wlan_sta

    # Try known networks first
    profiles = read_profiles()
    wlan_sta.active(True)
    networks = wlan_sta.scan()
    AUTHMODE = {0: "open", 1: "WEP", 2: "WPA-PSK", 3: "WPA2-PSK", 4: "WPA/WPA2-PSK"}

    for ssid_bytes, bssid, channel, rssi, authmode, hidden in sorted(networks, key=lambda x: x[3], reverse=True):
        ssid = ssid_bytes.decode('utf-8')
        encrypted = authmode > 0
        print("ssid: {} chan: {} rssi: {} authmode: {}".format(ssid, channel, rssi, AUTHMODE.get(authmode, '?')))
        if encrypted:
            if ssid in profiles:
                password = profiles[ssid]
                if do_connect(ssid, password):
                    return wlan_sta
        else:
            if do_connect(ssid, None):
                return wlan_sta

    # If no network connected, start AP mode
    if start_ap():
        return wlan_sta if wlan_sta.isconnected() else None
    return None

def do_connect(ssid, password, timeout=CONNECT_TIMEOUT):
    wlan_sta.active(True)
    if wlan_sta.isconnected():
        return True
    print("Trying to connect to '{}'...".format(ssid))
    wlan_sta.connect(ssid, password)
    start = time.time()
    while (time.time() - start) < timeout:
        if wlan_sta.isconnected():
            print("Connected. Network config:", wlan_sta.ifconfig())
            return True
        time.sleep(0.2)
        print('.', end='')
    print("\nFailed to connect to '{}'".format(ssid))
    return False

# ==========================
# Profiles read/write
# ==========================
def read_profiles():
    try:
        with open(NETWORK_PROFILES, "r") as f:
            return ujson.load(f)
    except (OSError, ValueError):
        return {}

def write_profiles(profiles):
    try:
        with open(NETWORK_PROFILES, "w") as f:
            ujson.dump(profiles, f)
    except OSError as e:
        print("Error writing profiles:", e)

# ==========================
# HTTP response helpers
# ==========================
def send_header(client, status_code=200, content_length=None):
    client.sendall("HTTP/1.0 {} OK\r\n".format(status_code))
    client.sendall("Content-Type: text/html\r\n")
    if content_length is not None:
        client.sendall("Content-Length: {}\r\n".format(content_length))
    client.sendall("\r\n")

def send_response(client, payload, status_code=200):
    if isinstance(payload, str):
        payload = payload.encode('utf-8')
    send_header(client, status_code, len(payload))
    client.sendall(payload)
    client.close()

def unquote(s):
    res = s.split('%')
    for i in range(1, len(res)):
        try:
            res[i] = chr(int(res[i][:2], 16)) + res[i][2:]
        except ValueError:
            res[i] = '%' + res[i]
    return "".join(res)

# ==========================
# HTTP handlers
# ==========================
def handle_root(client):
    wlan_sta.active(True)
    ssids = sorted(ssid.decode('utf-8') for ssid, *_ in wlan_sta.scan())
    html = ["<html><h1>Wi-Fi Client Setup</h1><form action='configure' method='post'><table>"]
    for ssid in ssids:
        html.append('<tr><td colspan="2"><input type="radio" name="ssid" value="{0}">{0}</td></tr>'.format(ssid))
    html.append("""
        <tr><td>Password:</td><td><input name="password" type="text" /></td></tr>
        </table>
        <p><input type="submit" value="Submit" /></p>
        </form>
        <hr />
        <h5>Your ssid and password information will be saved into the '{}' file in your ESP module. Be careful!</h5>
        </html>
    """.format(NETWORK_PROFILES))
    send_response(client, ''.join(html))

def handle_configure(client, request):
    match = ure.search("ssid=([^&]*)&password=(.*)", request.decode('utf-8'))
    if match is None:
        send_response(client, "Parameters not found", 400)
        return False
    ssid = unquote(match.group(1))
    password = unquote(match.group(2))

    if not ssid:
        send_response(client, "SSID must be provided", 400)
        return False

    if do_connect(ssid, password):
        html = "<html><center><h1>ESP successfully connected to WiFi network {}</h1></center></html>".format(ssid)
        send_response(client, html)
        wlan_ap.active(False)
        profiles = read_profiles()
        profiles[ssid] = password
        write_profiles(profiles)
        time.sleep(2)
        return True
    else:
        html = "<html><center><h1>ESP could not connect to WiFi network {}</h1><br><form><input type='button' value='Go back!' onclick='history.back()'></form></center></html>".format(ssid)
        send_response(client, html)
        return False

def handle_not_found(client, url):
    send_response(client, "Path not found: {}".format(url), 404)

# ==========================
# AP server
# ==========================
def stop():
    global server_socket
    if server_socket:
        server_socket.close()
        server_socket = None
    wlan_ap.active(False)

import uos

# ==========================
# WiFi reset
# ==========================
def reset_wifi():
    """Delete stored WiFi credentials and disconnect"""
    global wlan_sta, wlan_ap

    # Delete credentials file
    try:
        uos.remove(NETWORK_PROFILES)
        print("Deleted WiFi credentials file '{}'".format(NETWORK_PROFILES))
    except OSError:
        print("WiFi credentials file not found. Nothing to delete.")

    # Disconnect STA
    if wlan_sta.isconnected():
        wlan_sta.disconnect()
        print("Disconnected from WiFi network.")
    wlan_sta.active(False)

    # Disable AP if active
    if wlan_ap.active():
        wlan_ap.active(False)
        print("AP mode disabled.")

    # Clear cached networks (ESP8266/ESP32 stores networks in memory on restart)
    wlan_sta.active(True)
    wlan_sta.disconnect()
    wlan_sta.active(False)
    print("WiFi reset completed.")
    
def start_ap(port=80, timeout=AP_TIMEOUT):
    global server_socket
    addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
    stop()
    wlan_ap.active(True)
    wlan_ap.config(essid=AP_SSID, password=AP_PASSWORD)
    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(1)
    print("AP mode active. Connect to SSID '{}', password '{}'".format(AP_SSID, AP_PASSWORD))
    start_time = time.time()

    while (time.time() - start_time) < timeout:
        if wlan_sta.isconnected():
            print("STA connected. Stopping AP mode.")
            stop()
            return True
        try:
            client, addr = server_socket.accept()
            handle_client(client)
        except Exception as e:
            print("Client handling error:", e)
        finally:
            gc.collect()
    print("AP mode timeout.")
    stop()
    return False

def handle_client(client):
    try:
        request = client.recv(1024)
        if not request:
            client.close()
            return
        try:
            url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request.decode('utf-8')).group(1).rstrip("/")
        except Exception:
            url = ""
        if url == "":
            handle_root(client)
        elif url == "configure":
            handle_configure(client, request)
        else:
            handle_not_found(client, url)
    except Exception as e:
        print("Error in client:", e)
        client.close()
