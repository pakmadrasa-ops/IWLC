# relay.py
import time
from machine import Pin
from config import LED_PIN, RELAY_PIN, MIN_RELAY_INTERVAL

led = Pin(LED_PIN, Pin.OUT, value=1)
relay = Pin(RELAY_PIN, Pin.OUT, value=0)

_state = 0
_last = 0

def init():
    relay.value(0)
    led.value(1)

def set(state):
    global _state, _last
    now = time.time()
    if state != _state and now - _last < MIN_RELAY_INTERVAL:
        return False
    relay.value(state)
    led.value(0 if state else 1)
    _state = state
    _last = now
    return True
