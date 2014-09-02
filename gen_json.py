#!/usr/bin/env python
import re
import calendargenerator
import mwclient
import sys
import json

if __name__ == "__main__":

	site = mwclient.Site(('https', 'stratum0.org'), path="/mediawiki/")
	termine = site.Pages["Termine"]
	
	entries = calendargenerator.parse_wiki_page(termine.edit())
	e = []
	for entry in entries:
		e.append(entry.getJson())
	
	result = {
			"success": 1,
			"result": e
	}

	if len(sys.argv) > 1:
		f = file(sys.argv[1], "w")
		f.write(json.dumps(result).encode("utf8"))
		f.close()
	else:
		print json.dumps(result).encode("utf8")