#!/usr/bin/env python
import re
import calendargenerator
import mwclient
import sys
import json
import md5

if __name__ == "__main__":

	site = mwclient.Site(('https', 'stratum0.org'), path="/mediawiki/")
	termine = site.Pages["Termine"]
	
	entries = calendargenerator.expand_dates(calendargenerator.parse_wiki_page(termine.edit()))
	e = []
	css = []
	for entry in entries:
		data = entry.getJson()
		group = data["class"]
		if group not in css:
			css.append(group)
		e.append(data)
	
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
	css_content = ""
	for group in css:
		color = "".join(map(lambda a: chr(int(a * 2, 16) | 0x1F).encode("hex"), list(md5.new(group).hexdigest()[:3])))
		
		css_content += ".%s, .dh-%s { background-color: #%s; }\n" % (group, group, color)

	if len(sys.argv) > 2:
		f = file(sys.argv[2], "w")
		f.write(css_content)
		f.close()
	else:
		print css_content