# debuging
# DUMMY = False
DUMMY = True
DEBUG = False

LOGLEVEL = 'DEBUG' if DEBUG else 'INFO'

#comm settings
AUTHKEY = b'password' # communication password
PORT = 6000
LISTENER_IP = '127.0.0.1' if DUMMY else '192.168.1.103' # for remote access in debug mode
ADDRESS = LISTENER_IP if DEBUG else 'localhost'

# neopixel settings
if not DUMMY:
    import board
    import neopixel
    NEOPIXEL_ORDER = neopixel.RGB
    NEOPIXEL_GPIO = board.D18

# Limit max brightness (1-255)
LED_BRIGHTNESS_LIMIT = 40

# LED strip(s) definitions:
# strip types length definition
LED_STRIP_VERTICAL = 8
LED_STRIP_HORIZONTAL = 14

# Groups definition
LED_GROUPS = [
    LED_STRIP_HORIZONTAL,
    LED_STRIP_VERTICAL,
    LED_STRIP_HORIZONTAL,
    LED_STRIP_VERTICAL
]

# LED range definitions
LED_TOP = range(LED_GROUPS[0])
LED_RIGHT = range(LED_TOP.stop,LED_TOP.stop+LED_GROUPS[1])
LED_BOTTOM = range(LED_RIGHT.stop,LED_RIGHT.stop+LED_GROUPS[2])
LED_LEFT = range(LED_BOTTOM.stop,LED_BOTTOM.stop+LED_GROUPS[3])

NEOPIXEL_LED = sum(LED_GROUPS)
LED_ALL = range(NEOPIXEL_LED)