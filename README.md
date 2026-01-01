# MTG Art Downloader
Mass download MTG card arts using MTGPics with Scryfall as a backup source, downloaded images are named according to their card name with the artist in parenthesis, set code in brackets. Arts from mtgpics are put in one folder, scryfall art crops in another folder. If any cards couldn't be found from either source a `logs/failed_downloads.txt` is populated with names of the missing cards so you can manually look for them.

## Setup - Python CLI
We now use [poetry](https://python-poetry.org/docs/) for dependency management:
- Have or Install Python 3.13+
- Have or Install poetry, you can use the following commands or [check out this install guide](https://python-poetry.org/docs/):

```shell
# install fedora python 3.14 package
sudo dnf install python314 python3.14-devel
cd ~/git
git clone git@github.com:hangrybear666/mtg-art-downloader.git
cd mtg-art-downloader
python3.14 -m venv ./.venv
source ./.venv/bin/activate
pip install --upgrade pip
pip install --upgrade pipx
pipx install poetry
poetry install
poetry run python main.py
```

## Commiting - To ensure pipelines on push succeeds

**Run pre-commit hooks for code formatting and standardization**:

```bash
poetry run pre-commit clean
poetry run pre-commit run --all-files
```

## How to use with a Decklist
- Paste a decklist into the cards.txt file in the working directory of MTG Art Downloader
- Run the downloader, hit Enter. You're good to go!
- Remember that you will get best results with clearly defined cards: `Card Name (SET) Number`
- I recommend avoiding random promo sets, and definitely avoid the Pre-release/Promo versions of existing sets. For example if looking for Midnight Hunt
cards make sure to use MID and not PMID!
- To temporarily remove cards from processing simply add "#" at the beginning of the line

## How to use with Scryfall commands?
- After running the app, you can enter commands like so:
`set:mh2, power>:3, type:creature`
- This example will download images for all MH2 creatures with power greater than or equal to 3. Separate arguments with a comma, separate the key and value of the argument with a colon. Refer to the scryfall API documentation for more use cases.

## How to use with Google Sheet Script
- "Make a copy" of this [Google Sheet](https://docs.google.com/spreadsheets/d/1QnVoQ1gvz1N4TKnkJJ44_FHomy0gNoxZlaPSkua4Rmk), this can use Scryfall to create a specialized list of cards based on parameters.
- Open up your copy of the "MTG Art Downloader Script" google sheet.
- In the FX for box A2 you can customize arguments for what cards you want to pull using the first string parameter, for example choose a given set, a given rarity (or range of rarities). Don't change the other parameters, those govern the columns that are generated.
- You can read more about arguments for this scryfall script here: https://github.com/scryfall/google-sheets
- Once your comfortable with the scryfall arguments, press enter and watch it populate. Copy the right most column.
- Paste those rows into the cards.txt file in the working directory, hit save.
- Run the downloader

## Config.ini
- You can choose the download folder and cards.txt naming conventions.
- You can choose whether to download newest card versions or oldest (this applies only to cards for which a set code is not specified).
- You can choose whether to download all available arts or only one art.
- You can choose whether to only download unique art or all art even when duplicats are present.
- You can choose whether to ignore fullarts (supported only when download all is enabled)
- You can choose whether to download scryfall arts as a fallback
- You can choose whether to download ONLY scryfall arts.
- You can choose whether to include extras in the search, this includes un-sets and special championship cards.
- You can increase or decrease threads added per second depending on the speed of your internet.
- You can disable multithreading to force sequential processing for e.g. debugging failure states
- You can choose the naming convention for saving the downloaded images.
- You can limit card dimensions by width and height to issue log file warnings in case of images being too small
- You can toggle a comprehensive card classification system that organizes downloads into types and color identities

## Card Classification System

The MTG Art Downloader now includes an advanced card classification system that automatically organizes downloaded card artwork based on card type and color identity. This system uses data from the Scryfall API (already fetched during the normal download process) to classify cards without making additional API requests.

INFO: can be disabled in `config.ini` via `Enable.Card.Classification = false`

### Type Precedence Rules

- **Type Precedence System**: Organizes cards by type with a strict precedence hierarchy
- **Color Identity Classification**: Separates cards by color within appropriate folders
- **Type Precedence Rules**: Token > Land > Planeswalker > Enchantment > Artifact > Other

### Precedence Examples

1. **Token has absolute priority**
   - All tokens go to `Token/{color_identity}/` regardless of other types

2. **Land takes precedence over Planeswalker, Enchantment and Artifact**
   - "Artifact Land" → `Land/` folder (not `Artifact/`)
   - "Enchantment Land — Saga" (Urza's Saga) → `Land/` folder

3. **Planeswalker takes precedence over Enchantment and Artifact**
   - All Planeswalkers get color identity subfolders `Planeswalker/{color_identity}/`

4. **Enchantment takes precedence over Artifact**
   - "Legendary Artifact Enchantment" → `Enchantment/{color_identity}/` folder

5. **Artifact stands alone**
   - "Artifact — Equipment" → `Artifact/` folder (no color subfolders)

6. **Other cards go to root color folders**
   - Creatures, Sorceries, Instants → `{color_identity}/` folder

### Special Cases

- **Basic Lands**: Always go to `Basic/` folder (not `Land/`)
- **Artifact folder**: Never uses color subfolders (all artifacts together)
- **Land folder**: Never uses color subfolders (all non-basic lands together)

### Example 1: Subtypes separated by Color Identity
```
downloaded/mtgpics/Enchantment/
├── White/          # White token creatures
├── Blue/           # Blue token creatures
├── Black/          # Black token creatures
├── Red/            # Red token creatures
├── Green/          # Green token creatures
├── Multicolor/     # Multicolor tokens
└── Colorless/      # Colorless artifact tokens (Treasure, Clue, etc.)
downloaded/mtgpics/Token/
└──same as above
downloaded/mtgpics/Planeswalker/
└──same as above
```

### Example 2: Root-Level Color Organization
```
downloaded/mtgpics/
├── White/          # White creatures, sorceries, instants
├── Blue/           # Blue spells
├── Black/          # Black spells
├── Red/            # Red spells (Lightning Bolt, etc.)
├── Green/          # Green spells
├── Multicolor/     # Multicolor creatures and spells
├── Colorless/      # Colorless Eldrazi, etc.
├── Artifact/       # All artifacts (no color subfolders)
├── Land/           # All non-basic lands
├── Basic/          # All basic lands
├── Planeswalker/   # (see Example 1)
├── Enchantment/    # (see Example 1)
└── Token/          # (see Example 1)
```

## Testing

- You can test the main app with:

```bash
source .venv/bin/activate
pytest src/tests.py
```
- You can test the card classifier  with:

```bash
source .venv/bin/activate
pytest src/test_card_classifier.py -v
```

- You can run a mypy typechecking test with:
```shell
mypy main.py build.py src
```

## Build Binaries

```shell
# build .exe executable with config in main.spec
poetry run pyinstaller main.spec
```
