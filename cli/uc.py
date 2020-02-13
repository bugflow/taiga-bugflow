import csv
import os
import os.path


def _ensure_parent_dir_exists(file_location):
    if not os.path.exists(os.path.dirname(file_location)):
        try:
            os.makedirs(os.path.dirname(file_location))
        except OSError as exc: # race!
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
