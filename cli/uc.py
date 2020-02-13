import csv
import datetime
import os
import os.path


def _ensure_parent_dir_exists(file_location):
    if not os.path.exists(os.path.dirname(file_location)):
        try:
            os.makedirs(os.path.dirname(file_location))
        except OSError as exc: # race!
            print("unable to ensure parent directory exists for: %s" % file_location)
            if exc.errno != errno.EEXIST:
                raise


def make_kanban_summary_report(file_location, kanban_data):
    _ensure_parent_dir_exists(file_location)
    with open(file_location, 'w', newline='') as csvfile:
        columns = ['transition', 'count', 'unsized', 'story_points']
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for r in kanban_data.summary_table():
            writer.writerow(r)

    return True

def make_kanban_detail_report(file_location, kanban_data):
    _ensure_parent_dir_exists(file_location)
    detail_table = kanban_data.detail_table()
    with open(file_location, 'w', newline='') as csvfile:
        columns = detail_table[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for r in detail_table:
            writer.writerow(r)

    return True

def make_query_parameter_report(file_location, metadata):
    print("DEBUG: %s" % file_location)  # DEBUG
    _ensure_parent_dir_exists(file_location)
    with open(file_location, 'w', newline='') as txtfile:
        txtfile.write(
            """
%s

parameters:
--db_host: %s
--db_user: %s
--db_port: %s
--db_password: xxxxx (seemed to work...)
--db_name: %s
--output_dir: %s
--project_id: %s
--since: %s
--until: %s

number of records found: %s

query executed: %s
""" % ( "taiga-bugflow was executed",
        metadata[0], metadata[1], metadata[2],
        metadata[3], metadata[4], metadata[5], metadata[6], metadata[7],
        metadata[8], datetime.datetime.now())
        )
    return True
