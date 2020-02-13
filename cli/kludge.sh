#!/bin/bash
# we want to query from midnight the day before yesterday,
# until midnight just past (i.e. the most recent full 24 hour day)

NOW=`date +"%Y%m%d%H%M%S"`
YESTERDAY=`date --date="1 day ago" +"%Y-%m-%d"`
DAY_BEFORE=`date --date="2 days ago" +"%Y-%m-%d"`

FROM=`date --date=$DAY_BEFORE +"%Y-%m-%d %H:%M:%S"`
UNTIL=`date --date=$YESTERDAY +"%Y-%m-%d %H:%M:%S"`
OUTDIR="${NOW}_daily_report"
. .venv/bin/activate


taiga-bugflow kanban 11 --output_dir=$OUTDIR --since="$FROM" --until="$UNTIL"
zip -r "$OUTDIR.zip" "$OUTDIR"
rm -rf "$OUTDIR"

# TODO: post to slack
