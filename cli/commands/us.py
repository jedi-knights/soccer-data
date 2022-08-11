import click

from cli.library import ussoccer


@click.group()
def cli():
    """Interact with US Soccer data"""
    pass

@cli.group()
def player():
    """Interact with US Soccer players"""
    pass

@player.command()
@click.option("--gender", "-g", type=click.Choice(["male", "female"]), required=True, help="Specify a gender.")
def list(gender: str):
    """List the players from the national team."""
    if gender == "male":
        index = 0
        players = ussoccer.get_players("Male")
        for player in players:
            index += 1
            click.echo(f'{index}) {player["name"]}')
    elif gender == "female":
        index = 0
        players = ussoccer.get_players("Female")
        for player in players:
            index += 1
            click.echo(f'{index}) {player["name"]}')

    else:
        click.echo("Unknown gender!")    