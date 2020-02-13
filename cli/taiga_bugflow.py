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

    db = TaigaDB(db_host, db_user, db_password, db_port, db_name)
    data = db.kanban_activity(
        project_id=project_id,
        since=since,
        until=until
    )
    # TODO: rename this into set-like class name
    kanban_data = Kanban(data)

    num_found = len(data)
    metadata = [
        db_host, db_user, db_port, # password removed
        db_name, output_dir, project_id, since, until,
        num_found
    ]
    # output_dir is a param
    floc = os.path.join(output_dir, 'report_parameters.txt')
    print("DEBUG floc: %s" % floc)
    print("DEBUG output_dir: %s" % output_dir)
    uc.make_query_parameter_report(floc, metadata)

    floc = os.path.join(output_dir, 'flow_summary.csv')
    uc.make_kanban_summary_report(floc, kanban_data)

    floc = os.path.join(output_dir, 'flow_details.csv')
    uc.make_kanban_detail_report(floc, kanban_data)
    
cli.add_command(kanban)
