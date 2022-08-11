import json
import click

from cli.common import config
from cli.common import tools
from cli.library import topdrawer

@click.group()
def cli():
    """Interact with TopDrawerSoccer data"""
    pass

@cli.group()
def conference():
    """Interact with conferences on TopDrawer"""
    pass

@cli.group()
def player():
    """Interact with players on TopDrawer"""
    pass

@player.group()
def commitment():
    pass

@commitment.command()
@click.option("--gender", "-g", type=click.Choice(["male", "female"]), required=True, help="Specify a gender.")
@click.option("--division", "-d", type=click.Choice(["di", "dii", "diii", "naia", "njcaa"]), required=False, default="di", help="Specify a target division.")
@click.option("--conference", "-c", type=str, required=True, help="The conference name")
@click.option("--year", "-y", type=int, required=True, help="The graduation year of the players")
def list(gender: str, division: str, conference: str, year: int):
    """List player commitments for from TopDrawer"""
    gender = tools.normalize_gender(gender)
    conference = config.translate_conference_name(conference)

    schools = topdrawer.get_conference_commits(gender, division, conference, year)

    if schools is None:
        click.echo("The list of schools returned was undefined!")
        return

    click.echo(f"gender={gender}")
    click.echo(f"division={division}")
    click.echo(f"conference='{conference}'")
    click.echo(f"year={year}")
    click.echo(f"There are {len(schools)} schools in the conference.")

    index = 0
    for school in schools:
        if "players" in school:
            for player in school["players"]:
                index += 1
                click.echo(f'{index}) "{player["name"]}" a {player["position"]} from {player["city"]} {player["state"]} to "{player["commitment"]}"')


@conference.command()
@click.option("--conference", "-c", type=str, required=True, help="The conference name")
def division(conference: str):
    """Lookup the division by conference name"""
    conference = config.translate_conference_name(conference)
    division = topdrawer.lookup_division_by_conference(conference)
    if division is not None:
        division = division.upper()
    else:
        division = "Unknown"
        
    click.echo(division)

@conference.command()
@click.option("--gender", "-g", type=click.Choice(["male", "female"]), required=True, help="Specify a gender.")
@click.option("--division", "-d", type=click.Choice(["di", "dii", "diii", "naia", "njcaa"]), required=False, default="di", help="Specify a target division.")
def list(gender: str, division: str):
    """
    List conferences from TopDrawer

    Note: To list the conferences execute:
    
    dexter tds conference list -g female -d di
    """
    gender = tools.normalize_gender(gender)

    conferences = topdrawer.get_conferences(gender, division)

    index = 0
    for conference in conferences:
        if conference["name"] != "N/A":
            index += 1
            click.echo(f'{index}) {conference["name"]}')

    click.echo()
    click.echo(f"There were {index} {gender} conferences in the {division.upper()} division.")
    click.echo()

@conference.command()
@click.option("--gender", "-g", type=click.Choice(["male", "female"]), required=True, help="Specify a gender.")
@click.option("--division", "-d", type=click.Choice(["di", "dii", "diii", "naia", "njcaa"]), required=False, default="di", help="Specify a target division.")
@click.argument("output", type=click.File(mode="w"))
def export(gender: str, division: str, output):
    """Export conferences from TopDrawer"""
    conferences = topdrawer.get_conferences(gender, division)
    root = { "data": conferences }

    json.dump(root, output, ensure_ascii=False, indent=2, sort_keys=False)

    click.echo(f"Exported {len(conferences)} {gender} conferences from the {division.upper()} division.")

@conference.command()
def sync(gender: str, division: str):
    """Synchronize the data in Cosmos conferences from TopDrawer"""
    click.echo("Todo: Synchronize conference data from TopDrawer to Cosmos DB")

@cli.command()
@click.option("--club-name", "-n", type=str, required=True, help="The name of a club.")        
def league(club_name: str):
    """Lookup the league for a club"""
    click.echo(topdrawer._get_league(club_name))
