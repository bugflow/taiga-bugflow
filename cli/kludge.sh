#!/bin/bash
TODAY=`date +"%Y%m%d%H%M%S"`
. .venv/bin/activate
OUTDIR="${TODAY}_daily_report"
echo "DEBUG: $OUTDIR"
taiga-bugflow kanban 11 --output_dir=$OUTDIR
zip -r "$OUTDIR.zip" "$OUTDIR"

# TODO: post to slack
