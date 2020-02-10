#!/usr/bin/env python
import click
import psycopg2
import sys
import datetime


class KanbanActivity:
    # This is hard-coded against the hand-rolled query.
    # Deal with it.
    
    def __init__(self, row):
        self.raw = row

    @property
    def transition(self):
        return str(self.raw[0])

    @property
    def from_state(self):
        return self.raw[0][0]

    @property
    def to_state(self):
        return self.raw[0][1]

    @property
    def transition_name(self):
        return self.raw[1]

    @property
    def ticket_id(self):
        return self.raw[2]

    @property
    def ticket_name(self):
        return self.raw[3]

    @property
    def transition_time(self):
        return self.raw[4]

    @property
    def story_points(self):
        return self.raw[5]

    def __str__(self):
        if not self.story_points:
            p = '-'
        else:
            p = "%s points" % self.story_points
        return "%s [%s] [%s] (%s --> %s) [%s] %s" % (
            self.transition_time,
            self.ticket_id,
            p,
            self.from_state,
            self.to_state,
            self.transition_name,
            self.ticket_name
        )


class TaigaDB:

    QUERY_TEMPLATE_FILE = './templates/taiga-status-updates.sql'

    def __init__(self, db_host, db_user, db_psx, db_name="taiga"):
        self.db_connection = psycopg2.connect(
            host=db_host, user=db_user,
            password=db_psx, database=db_name
        )

    def sql(self, project_id, since, until):
        if not until:
            until = datetime.datetime.now()

        sql_template = open(self.QUERY_TEMPLATE_FILE, 'r').read()
        return sql_template.format(
            project_id=project_id,
            since=since,
            until=until
        )

    def kanban_activity(self, project_id, since, until):
        found = []
        try:
            cur = self.db_connection.cursor()
            query = self.sql(project_id, since, until)
            #  click.echo(query)  # DEBUG
            cur.execute(query)
            for row in cur.fetchall():
                found.append(
                    KanbanActivity(row)
                )
            return found
        except psycopg2.DatabaseError as e:
            click.echo(f'Error {e}')
            sys.exit(1)


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
def kanban(db_host, db_user, db_password, project_id, since, until):
    click.echo("generating kanban activity report")
    click.echo("    project_id: %s" % project_id)
    click.echo("    --since: %s" % since)
    click.echo("    --until: %s" % until)

    db = TaigaDB(db_host, db_user, db_password)

    data = db.kanban_activity(
        project_id=project_id,
        since=since,
        until=until
    )

    click.echo("    %s events found" % len(data))
    # TODO: make report here

    transitions = {}
    for r in data:
        if r.transition_name not in transitions.keys():
            transitions[r.transition_name]=[]
        transitions[r.transition_name].append(r)
    
    for t in transitions.keys():
        name = t
        count = len(transitions[t])
        sp_missing = 0
        size = 0
        for r in transitions[t]:
            if r.story_points:
                size += r.story_points
            else:
                sp_missing += 1
        if sp_missing:
            sp_msg = "%s - %s stories unsized" % (size, sp_missing)
        else:
            sp_msg = "%s" % size
        click.echo("%s: %s (%s)" % (t, count, sp_msg))

cli.add_command(kanban)
