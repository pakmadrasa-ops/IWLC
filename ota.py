import urequests, ujson, uos, version, machine

BASE = "https://raw.githubusercontent.com/YOURUSER/esp-firmware/main/"

def check_and_update():
    r = urequests.get(BASE+"manifest.json")
    m = r.json()
    r.close()
    if m["version"] <= version.VERSION:
        return
