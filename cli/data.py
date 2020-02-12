import click  # TODO factor this out somehow
import psycopg2
import sys
import datetime
from model import KanbanActivity


class TaigaDB:

    QUERY_TEMPLATE_FILE = './templates/taiga-status-updates.sql'

    def __init__(self, db_host, db_user,
                 db_psx, db_port='5432',
                 db_name="taiga"):
        # print("DEBUG: db_host=%s" % db_host)
        # print("DEBUG: db_user=%s" % db_user)
        # print("DEBUG: db_psx=%s" % db_psx)
        # print("DEBUG: db_port=%s" % db_port)
        # print("DEBUG: db_name=%s" % db_name)
        self.db_connection = psycopg2.connect(
            host=db_host, user=db_user,
            password=db_psx, database=db_name,
            port=db_port
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
            #click.echo(query)  # DEBUG
            cur.execute(query)
            for row in cur.fetchall():
                found.append(
                    KanbanActivity(row)
                )
            return found
        except psycopg2.DatabaseError as e:
            click.echo(f'Error {e}')
            sys.exit(1)
