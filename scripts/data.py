import click

import logging

__version__ = "0.0.0"

@click.group()
def cli():
    """
    This is my command line interface to help interactively explorer and
    munge data for the SoccerHub from a variety of sources.
    """
    pass


def main():
    try:
        cli()
    except Exception:
        logging.error("Something bad happend")
        raise


if __name__ == "__main__":
    main()
