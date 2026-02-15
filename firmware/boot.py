# boot.py
import time, machine, uos
import version

BOOT_GRACE = 10
BOOT_FLAG = "boot_fail.flag"
MAX_FAILS = 3

print("Bootloader starting")
print("Version:", version.VERSION)


# Option 2: Check for interrupt more frequently
t0 = time.time()
while time.time() - t0 < BOOT_GRACE:
    try:
        time.sleep(0.5)
    except KeyboardInterrupt:
        import sys
        sys.exit()


fails = 0
if BOOT_FLAG in uos.listdir():
    with open(BOOT_FLAG) as f:
        fails = int(f.read())

fails += 1
with open(BOOT_FLAG, "w") as f:
    f.write(str(fails))

if fails >= MAX_FAILS:
    print("Rollback triggered")
    if "rollback" in uos.listdir():
        for fn in uos.listdir("rollback"):
            with open("rollback/"+fn,"rb") as s, open(fn,"wb") as d:
                d.write(s.read())
    machine.reset()

try:
    import ota
    ota.check_and_update()
except:
    pass

uos.remove(BOOT_FLAG)
