#!/usr/bin/env python3
# -.- encoding: utf-8 -.-
import mwclient
import config
import calendargenerator
import datetime

import pytz

site = mwclient.Site((config.protocol, config.server), path="/mediawiki/")

termine = site.Pages["Termine"]
termine_archiv = site.Pages["Termine/Archiv"]

termine_text = termine.text()
termine_archiv_text = termine_archiv.text()

threshold_date = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(calendargenerator.tz) - datetime.timedelta(days=config.archive_threshold_days)


new_termine_text, new_termine_archiv_text, n = calendargenerator.move_to_archive(termine_text, termine_archiv_text, threshold_date)


termine_changed = False
archiv_changed = False

if termine_text != new_termine_text:
	print("termine changed")
	termine_changed = True

if termine_archiv_text != new_termine_archiv_text:
	print("archiv changed")
	archiv_changed = True

comment = u"Termine cleanup"
if n > 0:
	comment = u"%d Termine ins Archiv verschoben" % n

minor_edit = n == 0

if termine_changed or archiv_changed:
	print(">", comment)
	print("minor:", minor_edit)

if config.write_wiki and (termine_changed or archiv_changed):
	if not site.logged_in:
		site.login(config.user, config.password)
	if termine_changed:
		termine.save(new_termine_text, comment, minor=minor_edit)
	if archiv_changed:
		termine_archiv.save(new_termine_archiv_text, comment, minor=minor_edit)
