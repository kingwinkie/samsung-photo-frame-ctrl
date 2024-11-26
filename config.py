# debugging
# LOGLEVEL = 'INFO'
LOGLEVEL = 'DEBUG'
IMG_SIZE = (1024, 600)
MODEL = None
LEDSTRIP_ENABLED = True
#MODEL='SPF-107H2' #frame model or None fro autodetect

# IMG_SOURCE_PATH = "data" # for IMG_SOURCE = FOLDER
# IMG_SOURCE_PATH = 'http://localhost:8082' # for IMG_SOURCE = URL
IMG_SOURCE_PATH = "https://random.imagecdn.app/1024/600" # for IMG_SOURCE = URL

# IMG_SOURCE = 1 # 1 = folder, 2 = URL
IMG_SOURCE = 2 # 1 = folder, 2 = URL

HTTP_DOWNLOAD_LIMIT = 10 #min delay between downloads in seconds
IMG_EXT = "jpg" # folder filtering extension
DELAY = 10 # how long show the picture without any effects in second
