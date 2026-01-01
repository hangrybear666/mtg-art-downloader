"""
CORE FUNCTIONS
"""

import json
import os
from collections.abc import Sequence
from typing import Optional, Union

import requests
from difflib import SequenceMatcher
from pathlib import Path
from colorama import Style, Fore
from unidecode import unidecode
from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from requests import RequestException
from src import settings as cfg
from src.fetch import get_cards_paged, get_mtgp_page

cwd = os.getcwd()


"""
PRE-PROCESS DATA
"""


def normalize_card_list(cards: Sequence[Union[str, dict]]) -> list[Union[str, dict]]:
    """
    Normalizes a list of cards, correcting for inconsistencies.
    @param cards: List of card names, with optional tags.
    @return: Normalized list of card names.
    """
    result: list[Union[str, dict]] = []

    # Convert to list to allow modifications
    cards_list = list(cards)

    # Remove empty lines
    if "" in cards_list:
        cards_list.remove("")
    if " " in cards_list:
        cards_list.remove(" ")

    # Use the mutable list for iteration
    cards = cards_list

    # Format each card
    for c in cards:
        # Analyze string card
        if isinstance(c, str):
            # Trim extra spaces and newline
            c = c.strip().replace("\n", "")

            # Remove inappropriate leading number
            terms = c.split(" ")
            if len(terms[0]) < 4 and terms[0].isdigit():
                c = " ".join(terms[1:])
        result.append(c)
    return result


"""
COMMANDS
"""


def get_command(command: str) -> Optional[dict]:
    """
    See if the command is listed in links.json
    @param command: String representing a pre-programmed command from links.json.
    @return: The appropriate link, None if nothing matches
    """
    for k, v in cfg.links.items():
        if command in v:
            return v[command]
    return None


def get_list_from_link(command: dict) -> list[dict]:
    """
    Webscrape to create list of cards to download from a given list.
    @param command: Command array including name, and url
    @return: Filename of the newly created list
    """
    try:
        # Grab the card list from JSON supported API
        cards = requests.get(command["url"]).json()
    except (RequestException, json.JSONDecodeError):
        # Invalid data or bad request
        return []
    # Navigate to list using keys defined by command
    for k in command.get("keys", []):
        cards = cards.get(k, {})
    return cards if isinstance(cards, list) else []


def get_list_from_scryfall(command: str) -> Optional[list]:
    """
    Use Scryfall API compliant query to return a list.
    @param command: Command string containing scryfall arguments.
    @return: Return path to the list file
    """
    query = "https://api.scryfall.com/cards/search"
    commands = [com.strip() for com in command.split(",")]

    # Recognized parameters
    params = {
        "unique": cfg.unique,
        "include_extras": cfg.include_extras,
        "q": " ".join(commands),
    }

    # Query paged results
    return get_cards_paged(query, params=params, keys=["data"])


"""
MTGP Functions
"""


def get_mtgp_code(set_code: str, num: str, name: str) -> Optional[str]:
    """
    Webscrape to find the correct MTG Pics code for the card.
    @param set_code: Set code of this card, ex: MH2
    @param num: Collector number of this card, ex: 220
    @param name: Name of this card, ex: Damnation
    @return: Accurate mtgp linkage for this card.
    """
    try:

        # Crawl the mtgpics site to find correct set code
        r = get_mtgp_page(f"https://www.mtgpics.com/card?ref={set_code}001")
        soup = BeautifulSoup(r, "html.parser")
        soup_td = soup.find("td", {"width": "170", "align": "center"})
        if soup_td is None:
            return None
        soup_a = soup_td.find("a")
        if soup_a is None:
            return None
        href = soup_a.get("href", "")
        if not isinstance(href, str):
            return None
        replaced = href.replace("set?", "set_checklist?")
        mtgp_link = f"https://mtgpics.com/{replaced}"

        # Crawl the set page to find the correct link
        r = get_mtgp_page(mtgp_link)
        soup = BeautifulSoup(r, "html.parser")
        rows = soup.find_all(
            "div",
            {
                "style": "display:block;margin:0px 2px 0px 2px;border-top:1px #cccccc dotted;"
            },
        )

        # Look for collector number and name match
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue
            if cols[0].text == num and name in cols[2].text:
                col_link = cols[2].find("a")
                if col_link is None:
                    continue
                href = col_link.get("href", "")
                if not isinstance(href, str):
                    continue
                return href.replace("card?ref=", "")

        # Collector number doesn't match, look only for the name
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue
            if name in cols[2].text:
                col_link = cols[2].find("a")
                if col_link is None:
                    continue
                href = col_link.get("href", "")
                if not isinstance(href, str):
                    continue
                return href.replace("card?ref=", "")

    except (KeyError, TypeError, IndexError, AttributeError):
        pass
    return None


def get_mtgp_code_pmo(
    name: str, artist: str, set_name: str, promo: str = "pmo"
) -> Optional[str]:
    """
    Webscrape to find the correct MTG Pics code for a promo card.
    @param name: Name of the card.
    @param artist: Artist of the card.
    @param set_name: Name of the card set.
    @param promo: Type of promo set.
    @return: Accurate mtgp linkage for this card.
    """
    try:
        # Track matches
        matches = []

        # Which promo set?
        if promo == "dci":
            url = "https://mtgpics.com/set_checklist?set=18"
        elif promo == "a22":
            url = "https://mtgpics.com/set_checklist?set=375"
        elif promo == "uni":
            url = "https://mtgpics.com/set_checklist?set=201"
        else:
            url = "https://mtgpics.com/set_checklist?set=72"

        # Crawl the set page to find the correct link
        r = get_mtgp_page(url)
        soup = BeautifulSoup(r, "html.parser")
        rows = soup.find_all(
            "div",
            {
                "style": "display:block;margin:0px 2px 0px 2px;border-top:1px #cccccc dotted;"
            },
        )
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 7:
                continue
            if (
                artist in unidecode(cols[6].text)
                and name.lower() in cols[2].text.lower()
            ):
                col_link = cols[2].find("a") if len(cols) > 2 else None
                if col_link is None:
                    continue
                href = col_link.get("href", "")
                code = href.replace("card?ref=", "") if isinstance(href, str) else ""
                if not code:
                    continue
                matches.append(
                    {
                        "code": code,
                        "match": SequenceMatcher(
                            a=cols[2].text.replace(name, ""), b=set_name
                        ).ratio(),
                    }
                )
        if not matches:
            return None
        # Type-safe sorting: cast to appropriate type
        from typing import cast

        sorted_matches = sorted(
            matches, key=lambda i: cast(float, i["match"]), reverse=True
        )
        code_value = sorted_matches[0]["code"]
        return str(code_value) if code_value else None
    except (KeyError, TypeError, IndexError, AttributeError):
        pass
    return None


def get_card_face(entries: ResultSet[Tag], back: bool = False) -> Optional[str]:
    """
    Determine which image URL is most likely correct on MTGP.
    @param entries: Image URLs available for this card on MTGP.
    @param back: True if this is the back face of a card, False if front face.
    @return: Our best guess which image is correct to download, None if zero found.
    """

    # Return none if entry list empty
    if len(entries) == 0:
        return None

    # Format the image path
    arr = []
    first_src = entries[0].get("src", "")
    if not isinstance(first_src, str):
        return None
    path = f"https://mtgpics.com/{os.path.dirname(first_src)}"
    path = path.replace("art_th", "art")

    # Isolate the image code
    for e in entries:
        src = e.get("src", "")
        if isinstance(src, str):
            arr.append(os.path.basename(src).replace(".jpg", ""))

    # Strategy based on number of entries
    if len(arr) == 1:
        if back:
            # Only one image, assume back is missing
            return None
        return f"{path}/{arr[0]}.jpg"
    if len(arr) == 2:
        if back:
            return f"{path}/{sorted(arr)[1]}.jpg"
        return f"{path}/{sorted(arr)[0]}.jpg"
    if len(arr) > 2:

        # Separate into string array and int array, sorted
        img_i = []
        img_s = []
        arr.sort()

        for i in arr:
            if len(i) == 3:
                img_i.append(i)
            elif len(i) > 3:
                img_s.append(i)

        # Try comparing ints
        if len(img_i) > 1:
            if back:
                return f"{path}/{img_i[1]}.jpg"
            return f"{path}/{img_i[0]}.jpg"

        # Try comparing strings
        if len(img_s) > 1:
            if back:
                return f"{path}/{img_s[1]}.jpg"
            return f"{path}/{img_s[0]}.jpg"

        # Or just go in order
        if back:
            return f"{path}/{img_i[0]}.jpg"
        return f"{path}/{img_s[0]}.jpg"

    # Finally, couldn't match anything
    return None


"""
VERY BASIC LOGGING
"""


def log_info(message: str) -> None:
    """
    INFO Logging utility
    """
    if not cfg.log_level == "NONE":
        print(f"{Fore.CYAN}{Style.NORMAL}INFO:{Style.RESET_ALL} {message}", flush=True)


def log_debug(message: str) -> None:
    """
    Debug logging for development purposes
    """
    if cfg.log_level == "DEBUG" and not cfg.log_level == "NONE":
        print(
            f"{Fore.LIGHTMAGENTA_EX}{Style.DIM}DEBUG:{Style.RESET_ALL} {message}",
            flush=True,
        )


def log_warning(message: str) -> None:
    """
    WARNING messages to notify of errors in e.g. cards.txt
    """
    if not cfg.log_level == "NONE":
        print(
            f"{Fore.YELLOW}{Style.BRIGHT}WARNING:{Style.RESET_ALL} {message}",
            flush=True,
        )


def log_mtgp(label: str) -> None:
    """
    Log card that was successfully downloaded from MTGP.
    """
    if not cfg.log_level == "NONE":
        print(
            f"{Fore.GREEN}{Style.BRIGHT}MTGP SUCCESS:{Style.RESET_ALL} {label}",
            flush=True,
        )


def log_scryfall(message: str, is_fallback: bool) -> None:
    """
    Log card that was successfully downloaded from Scryfall.

    @param message: Card Label to output in log msg
    @param is_fallback: whether Scryfall is the only download source or just the backup on miss
    """
    if not cfg.log_level == "NONE":
        if is_fallback:
            print(
                f"{Fore.LIGHTGREEN_EX}{Style.DIM}SCRY [Fallback] SUCCESS:{Style.RESET_ALL} {message}",
                flush=True,
            )
        else:
            print(
                f"{Fore.GREEN}{Style.BRIGHT}SCRY SUCCESS:{Style.RESET_ALL} {message}",
                flush=True,
            )


def log_failed(
    label: str,
    print_out: bool = True,
    write_log: bool = True,
    filename: str = "failed_downloads",
    action: str = "MTGP",
) -> None:
    """
    Log card that couldn't be found.
    @param label: MTG card name and other details.
    @param print_out: Whether to print the failure.
    @param write_log: Whether to write failure to log file.
    @param filename: Name of the log file.
    @param action: The particular action that failed (MTGP or SCRY)
    """
    if write_log:
        Path(os.path.join(cwd, "logs")).mkdir(mode=511, parents=True, exist_ok=True)
        with open(
            os.path.join(cwd, f"logs/{filename}.txt"), "a", encoding="utf-8"
        ) as f:
            f.write(f"{action}: {label}\n")
    if print_out:
        print(f"{Fore.RED}{action} FAILED:{Style.RESET_ALL} {label}", flush=True)


def log_size_warning(
    file: str,
    size: int,
    width: int,
    height: int,
    print_out: bool = True,
    write_log: bool = True,
    filename: str = "insufficient_dimensions",
    action: str = "MTGP",
) -> None:
    """
    Log card that has insufficient width and/or height for printing.
    @param file: MTG card file with insufficient size.
    @param size: file size in kilobytes
    @param width: width in pixels
    @param height: height in pixels
    @param print_out: Whether to print the failure.
    @param write_log: Whether to write failure to log file.
    @param filename: Name of the log file.
    @param action: The particular action that failed (MTGP or SCRY)
    """
    if write_log:
        Path(os.path.join(cwd, "logs")).mkdir(mode=511, parents=True, exist_ok=True)
        with open(
            os.path.join(cwd, f"logs/{filename}.txt"), "a", encoding="utf-8"
        ) as f:
            f.write(f"{file}\n[{size}kb] [{width}x{height}]\n")
    if print_out:
        print(
            f"{Fore.YELLOW}{Style.BRIGHT}{action} INSUFFICIENT DIMENSIONS:{Style.RESET_ALL} {width}px x {height}px for {file}",
            flush=True,
        )
