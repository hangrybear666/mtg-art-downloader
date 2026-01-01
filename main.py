"""
APP TO EXECUTE THE SEARCH
"""

import os
import re
import sys
from zoneinfo import ZoneInfo
from datetime import datetime
from functools import cached_property
from multiprocessing import cpu_count, freeze_support
from multiprocessing.pool import Pool
from src.core import log_debug, log_info, log_warning
from pathlib import Path
from typing import Union, Optional
from time import perf_counter
from src import card as dl
from src import settings as cfg
from src.__version__ import version
from colorama import Style, Fore

from src.core import (
    normalize_card_list,
    get_list_from_link,
    get_list_from_scryfall,
    get_command,
)
from src.fetch import (
    get_scryfall_card_named,
    get_scryfall_card_numbered,
    get_scryfall_card_search,
)
from src.type_defs import DownloadResult

# Core variables
detailed_reg = re.compile(r"(.*) \((.*)\) ?(.*)")
cwd = os.getcwd()
os.system("")


class Download:
    def __init__(
        self,
        command: Optional[str] = None,
        card_list: Optional[Union[str, list]] = None,
        testing: bool = False,
    ):
        self._testing: bool = testing
        self._time: float = perf_counter()
        self._list = cfg.cardlist if not card_list else card_list
        self._command: Optional[str] = command
        self.fails: list = []

    """
    PROPERTIES
    """

    @property
    def is_test(self):
        return self._testing

    @cached_property
    def cards(self) -> list[Union[dict, str]]:
        """
        Return a card list either from given command or text file.
        """
        if self.command and ":" in self.command:
            result = get_list_from_scryfall(self.command)
            return result if result is not None else []
        if self.command:
            if link := get_command(self.command):
                return normalize_card_list(get_list_from_link(link))
        if isinstance(self._list, list):
            return self._list
        if os.path.isfile(self._list):
            with open(self._list, "r", encoding="utf-8") as f:
                # Remove blank lines, print total cards
                return normalize_card_list(f.readlines())
        return []

    @cached_property
    def command(self) -> str:
        return self._command or ""

    @cached_property
    def time(self) -> float:
        return perf_counter() - self._time

    #           ___ ___       __   __   __
    #     |\/| |__   |  |__| /  \ |  \ /__`
    #     |  | |___  |  |  | \__/ |__/ .__/

    @staticmethod
    def rotate_log_files():
        """
        Checks for existence of prior logfiles containing failed cards and insufficient dimensions.
        If the prior log file contains card entries (more than 1 line), it is rotated with a timestamp.
        If it only contains a header or is empty, it is deleted.
        Finally, new log files are created with the current Berlin timestamp.
        """
        log_dir = os.path.join(cwd, "logs")
        log_file_path = os.path.join(log_dir, "failed_downloads.txt")
        dimensions_file_path = os.path.join(log_dir, "insufficient_dimensions.txt")

        # Ensure directory exists to prevent errors
        Path(log_dir).mkdir(mode=511, parents=True, exist_ok=True)

        # Generate shared header for all log files
        current_time = datetime.now(ZoneInfo("Europe/Berlin"))
        header_time = current_time.strftime("### %Y-%m-%d %H:%M:%S ###")

        # 1. Handle existing failed_downloads.txt log file
        if os.path.isfile(log_file_path):
            try:
                # Check content length (ignoring empty lines)
                with open(log_file_path, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip()]

                if len(lines) > 1:
                    # File has actual failures (Header + Content) -> Rotate
                    mtime = os.path.getmtime(log_file_path)
                    timestamp_str = datetime.fromtimestamp(mtime).strftime(
                        "%Y-%m-%d_%H-%M-%S"
                    )
                    new_name = os.path.join(
                        log_dir, f"failed_downloads-{timestamp_str}.txt"
                    )
                    os.rename(log_file_path, new_name)
                else:
                    # File is empty or only has header -> Delete
                    os.remove(log_file_path)
            except OSError as e:
                print(f"{Fore.RED}Error handling old log file: {e}{Style.RESET_ALL}")

        # 2. Handle existing insufficient_dimensions.txt - hard delete
        if os.path.isfile(dimensions_file_path):
            try:
                os.remove(dimensions_file_path)
            except OSError as e:
                print(
                    f"{Fore.RED}Error deleting dimensions log file: {e}{Style.RESET_ALL}"
                )

        # 3. Create new log files with Europe/Berlin Timezone Header
        try:
            with open(log_file_path, "w", encoding="utf-8") as f:
                f.write(f"{header_time}\n")
            with open(dimensions_file_path, "w", encoding="utf-8") as f:
                f.write(f"{header_time}\n")
        except Exception as e:
            print(f"{Fore.RED}Could not initialize log files: {e}{Style.RESET_ALL}")

    def start(self) -> list[tuple[bool, str]]:
        """
        Using our card list, generate a download for each card that is not commented out.

        Skips the following lines:
            - empty lines.
            - lines with only spaces
            - # at the beginning of the line

        @return: List of tuples, each containing success/fail state and name of the card.
        """
        # Do we have a valid card list?
        if not self.cards:
            print(f"{Fore.RED}---- NO CARD LIST FOUND! ----{Style.RESET_ALL}")
            return []

        cards_to_process: list[Union[dict, str]]
        if not self.is_test:
            # filter out empty lines and commented out lines
            remove_empty_and_commented_lines = [
                line
                for line in self.cards
                if isinstance(line, str)
                and len(line.strip()) > 1
                and line.strip()[:1] != "#"
            ]
            # remove lines including hashtags e.g. Moxfield tags
            remove_lines_with_tags = [
                line for line in remove_empty_and_commented_lines if not "#" in line
            ]
            if len(remove_lines_with_tags) < len(remove_empty_and_commented_lines):
                log_warning(
                    f"Removed {len(remove_empty_and_commented_lines) - len(remove_lines_with_tags)} lines."
                )
                log_warning(
                    f"Removed lines contain a hashtag in the midst - these are invalid:\n"
                    f"{set(remove_empty_and_commented_lines) - set(remove_lines_with_tags)}"
                )
            from typing import cast

            cards_to_process = cast(list[Union[dict, str]], remove_lines_with_tags)
            # log all filtered out cards if log level is set to DEBUG
            if len(cards_to_process) < len(self.cards):
                log_debug(
                    f"Filtered out {len(self.cards) - len(cards_to_process)} lines."
                )
                log_debug(
                    f"Filtered out lines (empty lines only counted once):\n"
                    f"{set(self.cards) - set(cards_to_process)}"
                )
        else:
            # In test mode, use cards as-is without filtering
            cards_to_process = self.cards

        # Create a pool to execute these downloads
        with Pool(processes=1 if cfg.disable_multithreading else cpu_count()) as pool:
            log_info(f"===== Downloading {len(cards_to_process)} cards! =====")
            downloads = pool.map(self.stage_download, cards_to_process)

        # Build results list
        results = []
        for res in list(downloads):
            results.extend(res)

        # Output completion time
        if not self.is_test:
            self.complete()
        return results

    def stage_download(self, card: Union[str, dict]) -> DownloadResult:
        """
        Choose the appropriate method to call to download this card, then call that method.
        @param card: Card details or name.
        @return: Tuple containing success/fail state and name of the card.
        """
        # Associate the proper download method
        if isinstance(card, dict):
            log_debug(f"Processing JSON formatted card: {card}")
            return self.download_dict(card)
        elif isinstance(card, str):
            log_debug(f"Processing card: {card}")
            return (
                self.download_detailed(card)
                if " (" in card
                else self.download_normal(card)
            )
        log_info(f"Unknown card: {str(card)}")
        return [(False, str(card))]

    def complete(self):
        """
        Tell the user the download process is complete.
        """
        if self.time < 10:
            width = 35
        elif self.time < 100:
            width = 36
        else:
            width = 37
        border = "=" * width

        log_info(
            f"\n{border}\n"
            f"Downloads finished in {Fore.CYAN}{Style.BRIGHT}{round(self.time, 2)}{Style.RESET_ALL} seconds!\n"
            f"All available files downloaded.\n"
            f"Check {Fore.CYAN}{Style.NORMAL}logs/failed_downloads.txt{Style.RESET_ALL}\n"
            f"Check {Fore.YELLOW}{Style.NORMAL}logs/insufficient_dimensions.txt{Style.RESET_ALL}\n"
            f"Press enter to exit."
        )
        input()
        sys.exit()

    """
    DOWNLOAD METHODS
    """

    def download_normal(self, card: str, disable_all: bool = False) -> DownloadResult:
        """
        Download a card with no defined set code.
        Relevant flags in config are:
            - Download.All: set True to download multiple artworks
            - Only.Search.Unique.Art: Only set true if specific artwork has low resolution
        @param card: Card name
        @param disable_all: Disable download all
        """
        # Prepare our return data
        results: DownloadResult = []

        # Retrieve scryfall data
        res = get_scryfall_card_search(
            params={
                "unique": cfg.unique,
                "include_extras": cfg.include_extras,
                "order": "released",
                "dir": cfg.release_sorting,
                "q": f'!"{card}"',
            }
        )

        # Valid card data returned?
        if not res:
            return [(False, card)]

        # Remove full art entries if necessary
        cards = [c for c in res if not cfg.exclude_fullart or not c.get("full_art")]

        # Loop through prints of this card
        for c in cards:
            # Download the card
            result = self.download_dict(c)

            # Break if result is successful and we only need one
            if (not cfg.download_all or disable_all) and all(
                [res[0] for res in result]
            ):
                return result
            results.extend(result)
        return results

    def download_detailed(self, item: str) -> DownloadResult:
        """
        Download card with defined set code, possibly number.
        @param item: Card name (SET) number
        @return: True if successful, False if unsuccessful.
        """
        # Setup card details (Array destructuring)
        name, code, number = detailed_reg.findall(item)[0]

        # Was collector number given?
        card = (
            get_scryfall_card_numbered(code=code.lower(), number=number)
            if number
            else get_scryfall_card_named(name=name, code=code.lower())
        )

        # Valid card data found?
        if not card:

            return [(False, item)]

        # Try to download the card
        return self.download_dict(card)

    def download_dict(self, card: dict) -> DownloadResult:
        """
        Downloads a card using fetched scryfall data.
        @param card: Dict of card data
        @return: True if succeeded, False if not
        """
        # Ensure this is a real card
        if not card.get("name"):
            return [(False, "No Card Specified")]

        # Try to download the card
        card_class = dl.get_card_class(card)
        return card_class(card).download(not self.is_test)


#    ___  ___  ___  _____ _   _
#    |  \/  | / _ \|_   _| \ | |
#    | .  . |/ /_\ \ | | |  \| |
#    | |\/| ||  _  | | | | . ` |
#    | |  | || | | |_| |_| |\  |
#    \_|  |_/\_| |_/\___/\_| \_/

if __name__ == "__main__":

    # Add necessary directories
    freeze_support()
    Path(cfg.download_folder).mkdir(mode=511, parents=True, exist_ok=True)
    Path(cfg.mtgp).mkdir(mode=511, parents=True, exist_ok=True)
    Path(cfg.scry).mkdir(mode=511, parents=True, exist_ok=True)

    # Welcome page
    print(f"{Fore.MAGENTA}{Style.NORMAL}\n")
    print("  ██████╗ ███████╗████████╗   ███╗   ███╗████████╗ ██████╗ ")
    print(" ██╔════╝ ██╔════╝╚══██╔══╝   ████╗ ████║╚══██╔══╝██╔════╝ ")
    print(" ██║  ███╗█████╗     ██║      ██╔████╔██║   ██║   ██║  ███╗")
    print(" ██║   ██║██╔══╝     ██║      ██║╚██╔╝██║   ██║   ██║   ██║")
    print(" ╚██████╔╝███████╗   ██║      ██║ ╚═╝ ██║   ██║   ╚██████╔╝")
    print("  ╚═════╝ ╚══════╝   ╚═╝      ╚═╝     ╚═╝   ╚═╝    ╚═════╝ ")
    print("  █████╗ ██████╗ ████████╗    ███╗   ██╗ ██████╗ ██╗    ██╗ ")
    print(" ██╔══██╗██╔══██╗╚══██╔══╝    ████╗  ██║██╔═══██╗██║    ██║ ")
    print(" ███████║██████╔╝   ██║       ██╔██╗ ██║██║   ██║██║ █╗ ██║ ")
    print(" ██╔══██║██╔══██╗   ██║       ██║╚██╗██║██║   ██║██║███╗██║ ")
    print(" ██║  ██║██║  ██║   ██║       ██║ ╚████║╚██████╔╝╚███╔███╔╝ ")
    print(" ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝  ")
    print(f"{Style.BRIGHT}MTG Art Downloader by Mr Teferi v1.3.0")
    print(f"Additional thanks to Trix are for Scoot, Chilli, and Gikkman")
    print(
        f"Forked in Dec 2025 and modified by hangrybear666 v{version}{Style.RESET_ALL}\n"
    )

    # Does the user want to use Google Sheet queries or cards from txt file?
    choice = input(
        f"{Fore.CYAN}{Style.NORMAL}You can change Settings in config.ini.\n"
        f"Please view the README for detailed instructions.\n"
        f"Cards can either be listed as 'Phyrexian Tower' or 'Phyrexian Tower (MH3) 303'{Style.RESET_ALL}\n"
        f"\nPress ENTER to proceed downloading the following cardlist: \n"
        f"{cfg.cardlist}\n"
    )

    # If the command is valid, download based on that, otherwise cards.txt
    if choice != "":
        print()  # Add newline gap

    # Rotate log files
    Download.rotate_log_files()

    # Start the Download
    Download(choice).start()
