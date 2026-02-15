# wifi.py
import network, time, ujson
from config import WIFI_FILE, AP_SSID, AP_PASSWORD

sta = network.WLAN(network.STA_IF)
ap = network.WLAN(network.AP_IF)

def load():
    try:
        with open(WIFI_FILE) as f:
            d = ujson.load(f)
            return d["ssid"], d["password"]
    except:
        return None, None

def connect(timeout=15):
    ssid, pw = load()
    if not ssid:
        return False
    sta.active(True)
    sta.connect(ssid, pw)
    t = time.time()
    while not sta.isconnected():
        if time.time()-t > timeout:
            return False
        time.sleep(0.3)
    return True

def start_ap():
    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASSWORD)
