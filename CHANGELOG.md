## v1.5.3 (2026-01-02)

**Forked by hangrybear666**

### Fix
- **tests**: Fixed test case package imports
- **types**: Fixed mypy static type definition imports (renamed `types.py` → `type_defs.py`)
- **mypy**: Resolved mypy static typing issues in test cases

### Refactor

- **CI/CD**: Ensured pre-commit hooks and tests run in pipeline `pytest-mypy.yml`
- **CI/CD**: Restructured Deployment pipeline `build-release.yml` for automated releases

## v1.5.2 (2026-01-01)

**Forked by hangrybear666** - Extended and modernized version

### Feat

- **card_classifier**: Extended classification system with Planeswalker as priority type
  - Added Planeswalker to type precedence: Token > Land > Planeswalker > Enchantment > Artifact
  - Planeswalkers now organized by color identity in `Planeswalker/{color}/` folders

- **config.ini**:
  - adds flag to disable multithreading in order to test sequential execution for e.g. debugging

### Fix

- **main.py**: Fixed UnboundLocalError in test mode where `cards_to_process` was undefined
- **card.py**: Added None check for failed HTTP requests in `mtgp_url` property to prevent BeautifulSoup crash
- **tests**: All 51 tests now passing (4 main app + 47 classifier tests)

## v1.5.1 (2026-01-01)

**Forked by hangrybear666**

### Feat

- **card_classifier**:
  - New `CardClassifier` module with type precedence: Token > Land > Enchantment > Artifact
  - Automatic folder organization by color identity (White, Blue, Black, Red, Green, Multicolor, Colorless)
  - Configurable via `Enable.Card.Classification` in config.ini
  - Comprehensive test suite with 37 tests covering edge cases and real MTG cards
- **settings**:
  - New `Min.Image.Width` and `Min.Image.Height` configuration options
  - Logs warnings to `logs/image_warnings.txt` for images below threshold

## v1.5.0 (2025-12-31)

**Forked by hangrybear666** - Major refactoring and modernization

### Feat

- **dependencies**:
  - Updated all package dependencies to latest stable versions
  - Migrated from Python 3.11 to 3.13-3.14 compatibility
- **validation**:
  - Improved card data validation before download
  - Better error handling for malformed card data
- **logging**:
  - Color-coded console output for better visibility
  - Improved log rotation and formatting

### Refactor

- **build**: Removed windows executable build. Linux Development only.
  - Removed pre-commit-config.yaml
  - Removed Commitizen release automation
  - Streamlined and simplified development workflow

---

## v1.3.0 (2023-07-19)

### Fix

- **constants**: Change from Enum to dataclass
- **types**: Fixed return type of naming_convention
- **get_mtgp_page**: Covered more response cases in which card could not be located
- **sets**: Updated some set codes and promo code dictionary

### Feat

- **settings**: Added a setting to allow downloading full Scryfall scans instead of art crop

## v1.2.0 (2023-03-31)

### Feat

- **Downloader**: Move from threads to multiprocessing, complete rewrite with rate limited requests

## v1.1.9 (2022-08-28)

### Fix

- **scryfall**: Fixed scryfall downloading

## v1.1.8 (2022-08-07)

### Fix
- **codes**: Wrote a new comprehensive set replacement library
- **py-test.yml**: Add types-requests to workflow
- **mypy**: Added stronger typing, fixed mypy errors
- **Card-Settings**: Scryfall commands now pass direct scryfall data, improvements to download process
- **core.get_mtgp_code-console**: Added flush to console and fixed pop, get_mtgp_code can now fall back on named search

## 1.1.7 (2022-08-05)

### Fix
- **constants.py**: Add Thread lock to console, fix doubled up print lines
- **main.py**: Fix type error list not subscriptable
- **py-test.yml**: add types-requests to mypy workflow
- **py-test.yml**: fix mypy stub error "requests"
- **py-test.py-core.py-main.py**: Fix poetry usage and pathing
- **py-test.yml-main.py**: Fix type error, fix poetry usage

### Refactor
- **card.py**: Stronger typing, improved download methods, removed bare exceptions
- **core.py-pyproject.toml**: Added stronger typing

## Pre-1.1.7

- **Pre-Commitizen** - See GitHub release history
