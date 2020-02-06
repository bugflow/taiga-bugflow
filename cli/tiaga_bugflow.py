#!/usr/bin/env python
import click

@click.group()
def cli():
    pass

@click.command()
# from, default 1970
# to, default NOW
# project_id, mandatory
@click.option(
    '--since', default='1970-01-01 00:00:01', type=click.DateTime(),
    help="include events since this time")
@click.option('--until', default=None, help="include events up until this time")
@click.argument('project_id')
def kanban(project_id, since, until):
    click.echo("generating kanban activity report")
    click.echo("    project_id: %s" % project_id)
    click.echo("    --since: %s" % since)
    click.echo("    --until: %s" % until)

#click.command()

cli.add_command(kanban)

if __name__ == "__main__":
    cli()
