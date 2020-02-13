import click
import datetime
import os.path
from data import TaigaDB
from reports import Kanban
import uc

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
@click.option(
    '--output_dir',
    envvar='BUGFLOW_TAIGA_OUTPUT_DIR',
    default='.output/'
)
def kanban(db_host, db_user, db_password, db_port,
           db_name, output_dir, project_id, since, until):
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

    kanban_data = Kanban(data)

    fname = 'flow_summary.csv'
    floc = os.path.join(output_dir, fname)  # output_dir is a param
    uc.make_kanban_summary_report(floc, kanban_data)

    fname = 'flow_details.csv'
    floc = os.path.join(output_dir, fname)
    uc.make_kanban_detail_report(floc, kanban_data)
    
cli.add_command(kanban)
