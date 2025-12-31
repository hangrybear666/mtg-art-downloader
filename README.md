# MTG Art Downloader
Mass download MTG card arts using MTGPics with Scryfall as a backup source, downloaded images are named according to their card name with the artist in parenthesis, set code in brackets. Arts from mtgpics are put in one folder, scryfall art crops in another folder. If any cards couldn't be found from either source a `logs/failed_downloads.txt` is populated with names of the missing cards so you can manually look for them.

# Setup - Python CLI
We now use [poetry](https://python-poetry.org/docs/) for dependency management:
- Have or Install Python 3.9+
- Have or Install poetry, you can use the following commands or [check out this install guide](https://python-poetry.org/docs/):

```shell
# install fedora python 3.11 package
sudo dnf install python311
cd ~/git
git clone git@github.com:hangrybear666/mtg-art-downloader.git
cd mtg-art-downloader
python3.11 -m venv ./.venv
source ./.venv/bin/activate
pip install pipx
pipx install poetry
poetry install
python main.py
```

- Alternatively you can get PyCharm which has native support for Poetry and can automatically start the app for you!

# How to use with a Decklist
- Paste a decklist into the cards.txt file in the working directory of MTG Art Downloader
- Run the downloader, hit Enter. You're good to go!
- Remember that you will get best results with clearly defined cards: `Card Name (SET) Number`
- I recommend avoiding random promo sets, and definitely avoid the Pre-release/Promo versions of existing sets. For example if looking for Midnight Hunt
cards make sure to use MID and not PMID!

# How to use with Scryfall commands?
- After running the app, you can enter commands like so:
`set:mh2, power>:3, type:creature`
- This example will download images for all MH2 creatures with power greater than or equal to 3. Separate arguments with a comma, separate the key and value of the argument with a colon. Refer to the scryfall API documentation for more use cases.

# How to use with Google Sheet Script
- "Make a copy" of this [Google Sheet](https://docs.google.com/spreadsheets/d/1QnVoQ1gvz1N4TKnkJJ44_FHomy0gNoxZlaPSkua4Rmk), this can use Scryfall to create a specialized list of cards based on parameters.
- Open up your copy of the "MTG Art Downloader Script" google sheet.
- In the FX for box A2 you can customize arguments for what cards you want to pull using the first string parameter, for example choose a given set, a given rarity (or range of rarities). Don't change the other parameters, those govern the columns that are generated.
- You can read more about arguments for this scryfall script here: https://github.com/scryfall/google-sheets
- Once your comfortable with the scryfall arguments, press enter and watch it populate. Copy the right most column.
- Paste those rows into the cards.txt file in the working directory, hit save.
- Run the downloader

# Config.ini
- You can choose the download folder and cards.txt naming conventions.
- You can choose whether to download newest card versions or oldest (this applies only to cards for which a set code is not specified).
- You can choose whether to download all available arts or only one art.
- You can choose whether to only download unique art or all art even when duplicats are present.
- You can choose whether to ignore fullarts (supported only when download all is enabled)
- You can choose whether to download scryfall arts as a fallback
- You can choose whether to download ONLY scryfall arts.
- You can choose whether to include extras in the search, this includes un-sets and special championship cards.
- You can increase or decrease threads added per second depending on the speed of your internet.
- You can choose the naming convention for saving the downloaded images.

# Testing
- You can test the app for consistency with:
```shell
pytest src/tests.py
```
- You can run a mypy typechecking test with:
```shell
mypy main.py build.py src
```