
from . import ga
from . import ecnl

import reactivex as rx
from reactivex import operators as ops

def get_clubs():
    """Get as many clubs as we know about."""
    clubs = []

    ga_clubs = ga.get_clubs()
    ecnl_clubs = ecnl.get_clubs()

    # Now we need to process each club from both lists to construct a total list.

