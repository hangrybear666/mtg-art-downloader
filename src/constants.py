"""
GLOBAL CONSTANTS
"""
from dataclasses import dataclass

@dataclass
class Constants:
    promo_sets = [
        "pre",
        "pmo",
        "dci",
        "fnm",
        # TODO: Investigate: 30a and p30a are really weird
        "pst",
        "30a",
        "slc",
    ]


con = Constants
