import click

import cli

class Config:
    def __init__(self):
        self.verbose = False
        self.debug = False

pass_config = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option('--verbose', is_flag=True)
@click.option('--debug/--no-debug', is_flag=True, default=False)
@pass_config
def cli(config, verbose, debug):
    config.verbose = verbose
    config.debug = debug 
    
    if verbose:
        click.echo("We are in verbose mode")

    if debug:
        click.echo("We are in debug mode")


@cli.command()
@click.option("--string", default="World", help="This is the thing that is greeted.")
@click.option("--repeat", default=1, type=int, help="How many times this is repeated")
@click.argument("out", type=click.File("w"), default="-", required=False)
@pass_config
def say(config, string, repeat, out):
    """This script greets you"""

    if config.verbose:
        click.echo("I see we are in verbose mode")

    if config.debug:
        click.echo("I see we are debugging")

    for x in range(repeat):
        click.echo(f"Hello {string}!", file=out)


@cli.command()
@pass_config
def ecnl(config):
    pass

@cli.command()
@pass_config
def ga(config):
    pass

@cli.command()
@pass_config
def usys(config):
    pass

if __name__ == "__main__":
    cli.add_command()