import os
# -------------------------------------- parameters from main.py ------------------------------------------------- #
# different mode for running the plane
cwd = os.getcwd()
DEBUG='DEBUG'
SEARCH='SEARCH'
DEFAULT='DEFAULT'
PAUSE='PAUSE'

SEND='SEND'
RECEIVE='RECEIVE'

HOLD_RATE = 3.0 # the safe region height compared to the hold height

# -------------------------------------- parameters from Communicate.py ------------------------------------------ #
LONGITUDE_TO_METER = 1.0
LATITUDE_TO_METER = 1.0

# -------------------------------------- parameters from loginfo.py ---------------------------------------------- #
DEFAULT_LENGTH=27

# -------------------------------------- parameters from GUI.py -------------------------------------------------- #
# size is 5*3
UNIT_HEI=200
UNIT_WID=200
HEAD_HEI=20
LINE_WID=2
BAR_WID=15

LOGINFO_LINE_LIMIT=10
LOGINFO_PATH='./log/planeInfo'

NUM_BUTTONS=5

NUM_BOTTOM_IMAGES=5

IMAGE_STORE_POSITION = "/log/images/"

# -------------------------------------- parameters from Region.py ----------------------------------------------- #
SR_LENGTH=5.0 # X axis
SR_HEIGHT=3.0 # Y axis
SR_WIDTH=4.0 # Z axis
MIN_HEIGHT = 0.3

SAFE_HEIGHT = 0.25 # the minimum height allowing UAV to fly around

INTERVAL = 0.1 # distance when draw the ply

ENLARGE = 1.5 # plot graph enlarge

DEFAULT_SCALE = 0.2 # this sets the outer-limit region the plane can visit

COMPRESS = '0.5'

# --------------------------------------- parameters from Feature.py --------------------------------------------- #
IMG_WIDTH = 1024
IMG_HEIGHT = 1024
WID_ERROR = 0.2 * IMG_WIDTH
HEI_ERROR = 0.2 * IMG_HEIGHT

IMG_LOG_FILE = "./log/img_proc"
NUM_THREADS=3

# ---------------------------------------- parameters from plate.py ---------------------------------------------- #
PLATE_START=[4.2,0.5,0.0] # the place to take photo
PLATE_REGION_RADIUS=[0.2,0.1,0.1] # the place to make certain region
PLATE_CENTER_BIAS=0.1 # the standard bias allowed for the plate photo to be ideal
PLATE_PHOTO_RATE=0.3

XAXIS_INNER_DISTANCE = 1.5
PLATE_PROPORTION = 1.0