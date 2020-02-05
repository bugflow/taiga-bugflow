# taiga-bugflow

Bugflow routines for taiga projects.

## Vision

* As a software team using https://taiga.io/
* I need a magical robot assistant
* so that the humans get more done

More specifically...

... Taiga has a brilliant, opinionated data model. Epics are collectons of stories, tasks belong to stories (except when they don't), and issues are not the same as tasks or stories. Taiga has a suite of APIs that seem good (no problems so far), but we haven't used them extensively (except through the app). Taiga is a django system so it's maintainagble and supportable. Taiga has a functional web UI that's not as slick as some things (like GitHub); but despite the less-slick UI, we use tiaga because we love the data it generates.

Maybe one day, we will have integrations between GitHub (or Gogs, or whatever) with Taiga, that allows users to spend most of their time in the front end environment they like best, but still gives us the data we love in the taiga. Or maybe we will develop specific tools that support our workflow and use the taiga APIs. Or maybe even we will have a nice open source mobile app that uses the tiaga APIs and is slick and a joy to use. Or maybe we will push on with the custy angular SPA and polish out some of the annoyances. Or maybe, as we do today, we will continue to use the SPA and quit moaning.

But what we need is:
 * handy reports that expose the lovely taiga data and help us monitor and manage our projects better
 * automate actions that we get sick of doing manually...
 
## Current state
 
We have some SQL that pulls interesting data out of taiga for us. We are actively developing that stuff, and will continue to push it up here so we don't loose it.

## Next steps

Maybe something like this:

* A cron job on a "almost always on" developer workstation
* runs a script that queries taiga DB through a ssh tunnel
* uses the query data to create some handy reports
* post the reports into slack so everyone on the team has access to them

And iterate:
* better and different reports
* reports that only get posted under exceptional circumstances (warnings, etc)

## Distant Future

Maybe an [errbot](https://errbot.readthedocs.io) daemon, that (in addition to running scheduled reports and posting them to a reports channel) performs interactive analysis of the state of a project in taiga. And a django "companion app" that can be deployed independantly to taiga (with access to the same DB) or deployed along side it (possibly using a DB read-replica with django routing to write upstream if required) that provides interactive and dynamic analysis of project metrics.

Our technical approach is to prototype potentially useful reports using vanilia "cli/cron; SQL + python => csv" methodology until such time as we are sick of maintaining SQL (move to django ORM), actually need something better than csv output (move to jinja+html, PDF, etc) and want something more interactive.
