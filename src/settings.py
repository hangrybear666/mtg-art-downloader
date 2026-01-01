"""
ESTABLISH USER SETTINGS
"""

import os
import configparser
import hjson
import json

cwd = os.getcwd()
with open("config.ini", "r", encoding="utf-8") as f:
    config = configparser.ConfigParser()
    config.read_file(f)

# Sets log level for the application. Valid Values are INFO | DEBUG | NONE
log_level = config.get("LOG_LEVEL", "Log.Level", fallback="INFO")

#     __   __        __  ___           ___  __
#    /  ` /  \ |\ | /__`  |   /\  |\ |  |  /__`
#    \__, \__/ | \| .__/  |  /~~\ | \|  |  .__/

with open(os.path.join(cwd, "src/codes.hjson"), "r", encoding="utf-8") as js:
    replace_sets = hjson.load(js)
with open(os.path.join(cwd, "src/links.json"), "r", encoding="utf-8") as js:
    links = json.load(js)

#     ___         ___  __
#    |__  | |    |__  /__`
#    |    | |___ |___ .__/

# Card list text file
cardlist = os.path.join(cwd, config.get("FILES", "Card.List", fallback="cards.txt"))

# Parent folder of all images
download_folder = os.path.join(
    cwd, config.get("FILES", "Download.Folder", fallback="downloaded")
)

# Scryfall sub folder
scry = os.path.join(
    cwd,
    download_folder
    + "/"
    + config.get("FILES", "Scryfall.Art.Folder", fallback="scryfall"),
)

# MTG Pics sub folder
mtgp = os.path.join(
    cwd,
    download_folder
    + "/"
    + config.get("FILES", "MTGPics.Art.Folder", fallback="mtgpics"),
)

# Output naming convention
naming = config.get(
    "FILES", "Naming.Convention", fallback="NAME (ARTIST) [SET] {NUMBER}"
)

#     __   ___ ___ ___         __   __
#    /__` |__   |   |  | |\ | / _` /__`
#    .__/ |___  |   |  | | \| \__> .__/

# Download full card image from Scryfall?
download_scryfall_full = config.getboolean(
    "SETTINGS", "Download.Scryfall.Full", fallback=False
)

# Download scryfall if MTGPics missing?
download_scryfall_fallback = config.getboolean(
    "SETTINGS", "If.Missing.Download.Scryfall", fallback=True
)

# ONLY download scryfall?
only_scryfall = config.getboolean("SETTINGS", "Only.Download.Scryfall", fallback=False)

# Overwrite previous files
overwrite = config.getboolean("SETTINGS", "Overwrite.Same.Name", fallback=True)

# Download all images available or just most recent?
download_all = config.getboolean("SETTINGS", "Download.All", fallback=False)

# Enable card classification by type and color identity?
enable_classification = config.getboolean(
    "SETTINGS", "Enable.Card.Classification", fallback=True
)

# Hardcodes simultaneous Pool processes to 1 to enable sequential processing
disable_multithreading = config.getboolean(
    "SETTINGS", "Disable.Multithreading.Parallelism", fallback=False
)

#     __   ___       __   __
#    /__` |__   /\  |__) /  ` |__|
#    .__/ |___ /~~\ |  \ \__, |  |

# In which direction should the sorting by release date occur (this applies only to cards for which no set is specified)?
release_sorting = (
    "desc"
    if config.getboolean("SEARCH", "If.No.Set.Code.Get.Newest", fallback=True)
    else "asc"
)

# Exclude full arts?
exclude_fullart = config.getboolean("SEARCH", "Exclude.Fullart", fallback=False)

# Download unique or ALL?
unique = (
    "art"
    if config.getboolean("SEARCH", "Only.Search.Unique.Art", fallback=True)
    else "prints"
)

# Include extras in search
include_extras = str(config.getboolean("SEARCH", "Include.Extras", fallback=True))

# log output warnings when card dimensions are not sufficient for printing
card_width_warning_limit = int(
    config.getint("SEARCH", "Card.Dimension.Warning.Width", fallback=633)
)
card_height_warning_limit = int(
    config.getint("SEARCH", "Card.Dimension.Warning.Height", fallback=471)
)
