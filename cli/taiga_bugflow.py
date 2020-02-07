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

    def __str__(self):
        return "%s [%s] (%s --> %s) [%s] %s" % (
            self.transition_time,
            self.ticket_id,
            self.from_state,
            self.to_state,
            self.transition_name,
            self.ticket_name
        )


class TaigaDB:
    def __init__(self, db_host, db_user, db_psx, db_name="taiga"):
        self.db_connection = psycopg2.connect(
            host=db_host, user=db_user,
            password=db_psx, database=db_name
        )
        # maybe put this in a jinja2 template,
        # it's an ugly thing to have in the python file
        self.sql_template = """
SELECT
    transition,
    -- TODO: this should be generated from a workflow config object
    CASE
        WHEN (transition ->> 0 != 'New' OR transition ->> 0 != 'Some future sprint')
	AND transition ->> 1 = 'In progress'
        THEN 'Started'

        WHEN (transition ->> 0 = 'In progress' OR transition ->> 0 = 'Backlog' OR transition ->> 0 = 'New')
        AND (transition ->> 1 = 'Some future sprint' OR transition ->> 1 = 'New')
        THEN 'Decreased scope'

        WHEN (transition ->> 0 = 'Some future sprint' OR transition ->> 0 = 'New')
        AND (transition ->> 1 = 'In progress' OR transition ->> 1 = 'Backlog')
        THEN 'Increased scope'

        WHEN transition ->> 0 != 'Failed QA'
        AND transition ->> 1 = 'Ready for review'
        THEN 'Developed'

        WHEN transition ->> 1 = 'Failed QA'
        THEN 'Rejected'

        WHEN transition ->> 0 = 'Failed QA'
        AND transition ->> 1 = 'Ready for review' 
        THEN 'Fixed'

        WHEN transition ->> 0 != 'Backlog'
        AND transition ->> 1 = 'Done'
        THEN 'Delivered'
	
        WHEN transition ->> 0 = 'Backlog'
        AND transition ->> 1 = 'Done'
        THEN 'OTBE'
	
        ELSE 'Unknown'
    END as transition_action,
    user_story_ref,
    user_story_subject,
    created
FROM
    (
        SELECT
		data#>'{{values_diff, status}}' as "transition",  -- CASE statement to swap these for labels
		data#>'{{userstory, id}}' as "user_story_id",
		data#>'{{userstory, ref}}' as "user_story_ref", -- the ticket ID
		data#>'{{userstory, subject}}' as "user_story_subject", -- make join on userstory.ud to get current subject?
		created,
		content_type_id
	FROM timeline_timeline
	-- we care about changes to user stories
	WHERE event_type='userstories.userstory.change'
	-- ignore comments etc, we only want state (column) changes
 	AND (
		data#>'{{values_diff, status}}' ->>0 IS NOT null
		OR data#>'{{values_diff, status}}' ->>1 IS NOT null
	)
	AND namespace = 'project:{project_id}' -- this is the project identifier and place to de-dupe timeline events from users
) q
WHERE
    created < to_timestamp('{until}', 'YYYY-MM-DD-HH24:MI:SS:US')
AND
    created > to_timestamp('{since}', 'YYYY-MM-DD-HH24:MI:SS:US')
ORDER BY
    user_story_ref,
    created DESC;"""

    def sql(self, project_id, since, until):
        if not until:
            until = datetime.datetime.now()        
        return self.sql_template.format(
            project_id=project_id,
            since=since,
            until=until
        )

    def kanban_activity(self, project_id, since, until):
        found = []
        try:
            cur = self.db_connection.cursor()
            cur.execute(self.sql(project_id, since, until))
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

    # TODO: make report here
    for r in data:
        click.echo(r)


cli.add_command(kanban)
