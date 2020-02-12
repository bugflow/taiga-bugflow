#!/usr/bin/env python
import click
import datetime
#from model import KanbanActivity
from data import TaigaDB
from reports import Kanban
import csv


@click.group()
def cli():
    pass

@click.command()
@click.option(
    '--since',
    default='1970-01-01 00:00:00',
    type=click.DateTime(),
    help="include events since this time")
@click.option(
    '--until',
    default=None,
    help="include events up until this time")
@click.argument('project_id')
@click.option(
    '--db_host',
    envvar='BUGFLOW_TAIGA_DB_HOST',
    prompt='no --db_host, no BUGFLOW_TAIGA_DB_HOST envar, please specify'
)
@click.option(
    '--db_user',
    envvar='BUGFLOW_TAIGA_DB_USER',
    prompt='no --db_user, no BUGFLOW_TAIGA_DB_USER envar, please specify'
)
@click.option(
    '--db_password',
    envvar='BUGFLOW_TAIGA_DB_PSX',
    prompt='no --db_password, no BUGFLOW_TAIGA_DB_PSX envar, please specify',
    hide_input=True,
    confirmation_prompt=False
)
@click.option(
    '--db_port',
    envvar='BUGFLOW_TAIGA_DB_PORT',
    default='5432'
)
@click.option(
    '--db_name',
    envvar='BUGFLOW_TAIGA_DB_NAME',
    default='taiga'
)
def kanban(db_host, db_user, db_password, db_port,
           db_name, project_id, since, until):
    click.echo("generating kanban activity report")
    click.echo("    project_id: %s" % project_id)
    click.echo("    --since: %s" % since)
    click.echo("    --until: %s" % until)

    db = TaigaDB(db_host, db_user, db_password, db_port, db_name)
    data = db.kanban_activity(
        project_id=project_id,
        since=since,
        until=until
    )
    click.echo("    %s events found" % len(data))  # DEBUG

    k = Kanban(data)

    with open('flow_summary.csv', 'w', newline='') as csvfile:
        columns = ['transition', 'count', 'unsized', 'story_points']
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for r in k.summary_table():
            writer.writerow(r)
    
    # DEBUG
    #for r in k.summary_table():
    #    click.echo(r)
    
cli.add_command(kanban)
