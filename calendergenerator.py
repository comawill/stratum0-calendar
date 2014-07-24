#!/usr/bin/env python
# -.- encoding: utf-8 -.-
import re
import datetime
from dateutil import rrule
import icalendar as ical
import pytz

tz = pytz.timezone('Europe/Berlin')


entry = re.compile("^\|\s*(.*?)\s*\|\|\s*(.*?)\s*\|\|\s*(.*?)\s*$")

single_date = re.compile("^(\d+)\.(\d+)\.(\d+)$")
single_date_time = re.compile("^(\d+)\.(\d+)\.(\d+)\s+(\d+)[:\.](\d+)$")
single_date_time_range = re.compile("^(\d+)\.(\d+)\.(\d+)\s+(\d+)[:\.](\d+)\s*\-\s*(\d+)[:\.](\d+)$")
date_range = re.compile("^(\d+)\.(\d+)\.(\d+)\s*\-\s*(\d+)\.(\d+)\.(\d+)$")
date_range_time = re.compile("^(\d+)\.(\d+)\.(\d+)\s+(\d+)[:\.](\d+)\s*\-\s*(\d+)\.(\d+)\.(\d+)\s+(\d+)[:\.](\d+)$")
weekday_time = re.compile("^([a-zA-Z0-9]+),?\s*(\d+)[:\.](\d+)$")
weekday_time_range = re.compile("^([a-zA-Z0-9]+),?\s*(\d+)[:\.](\d+)\s*\-\s*(\d+)[:\.](\d+)$")

mediawiki_intern_link = re.compile(r"(\[\[(.*?)\|?(.*)\]\])")
mediawiki_extern_link = re.compile(r"(\[([^\ ]+)\s+(.*)\])")

dow_regex = re.compile(r"^((\d+)x|)(\w+)")
dow_index = {"mo":0,
	"mon":0,
	"di":1,
	"tue":1,
	"mi":2,
	"wed":2,
	"do":3,
	"thu":3,
	"fr":4,
	"fri":4,
	"sa":5,
	"sat":5,
	"so":6,
	"sun":6}

DOW_STR = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

DEFAULT_DURATION = 3 #3h
MAX_NEXT_UP_REPEATED = 3
MAX_IN_BEFORE_REPEATED = 1

def make_extern(intern_url):
	return "https://stratum0.org/wiki/%s" % intern_url.replace(" ", "_")

class DatePrinter(object):
	def __init__(self, name):
		self.name = name
		self.rule = None
		pass

	def getIcal(self):
		event = ical.Event()
		event.add('summary', self.getPlainName().encode("utf8"))
		url = self.getURL()
		if url:
			event.add('url', url.encode("utf8"))
		event.add('dtstart', self.getStartDate())
		event.add('dtend', self.getEndDate())
		return event
	
	def getMediawikiEntry(self):
		raise Exception("not implemented")
	
	def getStartDate(self):
		raise Exception("not implemented")

	def getEndDate(self):
		raise Exception("not implemented")

	def getMediawikiName(self):
		return self.name

	def getPlainName(self):
		name = mediawiki_intern_link.sub(r"\3", self.name)
		name = mediawiki_extern_link.sub(r"\3", name)
		return name

	def getURL(self):
		urls_intern = mediawiki_intern_link.findall(self.name)
		urls_extern = mediawiki_extern_link.findall(self.name)
		extern_url = None
		intern_url = None
		if urls_extern:
			extern_url = urls_extern[0]
		if urls_intern:
			intern_url = urls_intern[0]
		if extern_url and intern_url:
			if self.name.index(extern_url[0]) < self.name.index(intern_url[0]):
				intern_url = None
			else:
				extern_url = None
		if intern_url:
			if intern_url[1]:
				return make_extern(intern_url[1])
			return make_extern(intern_url[2])
		if extern_url:
			return extern_url[1]

		return None

	def __lt__(self, other):
		return other > self.getStartDate()

	def __gt__(self, other):
		return other < self.getEndDate()


class SingleDate(DatePrinter):
	def __init__(self, name, values):
		DatePrinter.__init__(self, name)
		day, month, year = map(int, values)
		self.date = datetime.datetime(year, month, day, 0 , 0, tzinfo=tz)
	
	def getMediawikiEntry(self):
		dow = DOW_STR[self.date.weekday()]
		return "* %s, %02d.%02d.: %s" % (dow, self.date.day, self.date.month, self.getMediawikiName())

	def getStartDate(self):
		return self.date
	
	def getEndDate(self):
		return self.date + datetime.timedelta(days=1)

class SingleDateTime(DatePrinter):
	def __init__(self, name, values):
		DatePrinter.__init__(self, name)
		day, month, year, hour, minute = map(int, values)
		self.date = datetime.datetime(year, month, day, hour, minute, tzinfo=tz)
	
	def getMediawikiEntry(self):
		dow = DOW_STR[self.date.weekday()]
		return "* %s, %02d.%02d. %02d:%02d: %s" % (dow, self.date.day, self.date.month, self.date.hour, self.date.minute, self.getMediawikiName())

	def getStartDate(self):
		return self.date

	def getEndDate(self):
		return self.date + datetime.timedelta(hours=DEFAULT_DURATION)

class SingleDateTimeRange(DatePrinter):
	def __init__(self, name, values):
		DatePrinter.__init__(self, name)
		day, month, year, hour, minute, hour2, minute2 = map(int, values)
		self.date = datetime.datetime(year, month, day, hour, minute, tzinfo=tz)
		self.date2 = datetime.datetime(year, month, day, hour2, minute2, tzinfo=tz)
	
	def getMediawikiEntry(self):
		dow = DOW_STR[self.date.weekday()]
		return "* %s, %02d.%02d. %02d:%02d - %02d:%02d: %s" % (dow, self.date.day, self.date.month, self.date.hour, self.date.minute, self.date2.hour, self.date2.minute, self.getMediawikiName())

	def getStartDate(self):
		return self.date

	def getEndDate(self):
		return self.date2


class DateRange(DatePrinter):
	def __init__(self, name, values):
		DatePrinter.__init__(self, name)
		day, month, year, day2, month2, year2 = map(int, values)
		self.date = datetime.datetime(year, month, day, 0, 0, tzinfo=tz)
		self.date2 = datetime.datetime(year2, month2, day2, 0, 0, tzinfo=tz)
	
	def getMediawikiEntry(self):
		dow = DOW_STR[self.date.weekday()]
		dow2 = DOW_STR[self.date2.weekday()]
		return "* %s, %02d.%02d. bis %s, %02d.%02d.: %s" % (dow, self.date.day, self.date.month, dow2, self.date2.day, self.date2.month, self.getMediawikiName())

	def getStartDate(self):
		return self.date

	def getEndDate(self):
		return self.date2 + datetime.timedelta(days=1)

class DateRangeTime(DatePrinter):
	def __init__(self, name, values):
		DatePrinter.__init__(self, name)
		day, month, year, hour, minute, day2, month2, year2, hour2, minute2 = map(int, values)
		self.date = datetime.datetime(year, month, day, hour, minute, tzinfo=tz)
		self.date2 = datetime.datetime(year2, month2, day2, hour2, minute2, tzinfo=tz)
	
	def getMediawikiEntry(self):
		dow = DOW_STR[self.date.weekday()]
		dow2 = DOW_STR[self.date2.weekday()]
		return "* %s, %02d.%02d. %02d:%02d bis %s, %02d.%02d. %02d:%02d: %s" % (dow, self.date.day, self.date.month, self.date.hour, self.date.minute, dow2, self.date2.day, self.date2.month, self.date2.hour, self.date2.minute, self.getMediawikiName())\

	def getStartDate(self):
		return self.date

	def getEndDate(self):
		return self.date2

class Generator:
	def __init__(self):
		pass

class WeekdayTimeRangeGenerator(Generator):
	def __init__(self, name, values, rep):
		Generator.__init__(self)
		nonetime = False
		self.entries = []
		rep = date_range.match(rep)
		if not rep:
			return
		kind, hour, minute, hour2, minute2 = values
		if hour:
			hour = int(hour)
		if minute:
			minute = int(minute)
		if hour2:
			hour2 = int(hour2)
		else:
			hour2 = (hour + DEFAULT_DURATION) % 24
			nonetime = True
		if minute2:
			minute2 = int(minute2)
		else:
			minute2 = minute
		dow = dow_regex.match(kind)
		if not dow:
			return
		_, interval, wd = dow.groups()
		if interval:
			interval = int(interval)
		else:
			interval = 1
		if wd.lower() not in dow_index:
			return
		wd = dow_index[wd.lower()]
		day, month, year, day2, month2, year2 = map(int, rep.groups())
		start = datetime.datetime(year, month, day, hour, minute, tzinfo=tz)
		start2 = datetime.datetime(year, month, day, hour2, minute2, tzinfo=tz)
		if start2 < start:
			start2 += datetime.timedelta(days=1)
		delta = start2 - start
		stop = datetime.datetime(year2, month2, day2, 0, 0, tzinfo=tz)
		rule = rrule.rrule(rrule.WEEKLY,interval=interval, byweekday=wd, dtstart=start, until=stop)
		for event in rule:
			event_end = event+delta
			if nonetime:
				self.entries.append(RepSingleDateTime(name, (event.day, event.month, event.year, event.hour, event.minute), rule))
			else:
				if event_end.day != event.day:
					self.entries.append(RepDateRangeTime(name, (event.day, event.month, event.year, event.hour, event.minute, event_end.day, event_end.month, event_end.year, event_end.hour, event_end.minute), rule))

				else:
					self.entries.append(RepSingleDateTimeRange(name, (event.day, event.month, event.year, event.hour, event.minute, event_end.hour, event_end.minute), rule))
			
		
class RepSingleDateTime(SingleDateTime):
	def __init__(self, name, values, rule):
		SingleDateTime.__init__(self, name, values)
		self.rule = rule
		
class RepSingleDateTimeRange(SingleDateTimeRange):
	def __init__(self, name, values, rule):
		SingleDateTimeRange.__init__(self, name, values)
		self.rule = rule
class RepDateRangeTime(DateRangeTime):
	def __init__(self, name, values, rule):
		DateRangeTime.__init__(self, name, values)
		self.rule = rule

class WeekdayTimeGenerator(WeekdayTimeRangeGenerator):
	def __init__(self, name, values, rep):
		values = values + (None, None)
		WeekdayTimeRangeGenerator.__init__(self, name, values, rep)


tests = [(single_date, SingleDate),
		(single_date_time, SingleDateTime),
		(single_date_time_range, SingleDateTimeRange),
		(date_range, DateRange),
		(date_range_time, DateRangeTime),
		(weekday_time, WeekdayTimeGenerator),
		(weekday_time_range, WeekdayTimeRangeGenerator)]

def analyze_date(name ,date, rep):
	for regex, dateClass in tests:
		rg = regex.match(date)
		if rg:
			if issubclass(dateClass, Generator):
				return dateClass(name, rg.groups(), rep)
			else:
				return dateClass(name, rg.groups())

def parse_wiki_page(content):
	result = []
	for line in content.splitlines(False):
		line = line.strip()
		dateinfo = entry.match(line)
		if not dateinfo:
			continue
		name, date, rep = dateinfo.groups()
		obj = analyze_date(name, date, rep)
		if obj:
			if issubclass(obj.__class__, Generator):
				result.extend(obj.entries)
			else:
				result.append(obj)
	return result

def next_up(entries):
	repeated_events = {}
	now_ = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz)
	now = now_-datetime.timedelta(hours=1)
	result = []
	for entry in sorted(entries):
		if entry.getEndDate() > now:
			# detect repeating events by nameyy
			eventid = entry.getPlainName()
			if eventid not in repeated_events:
				repeated_events[eventid] = 0
			repeated_events[eventid] +=1
			if repeated_events[eventid] > MAX_NEXT_UP_REPEATED:
				continue
				
			result.append(entry)
			
	return result

def in_before(entries):
	repeated_events = {}
	now_ = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz)
	now = now_-datetime.timedelta(hours=1)
	lowest = now_-datetime.timedelta(days=31)
	result = []
	for entry in sorted(entries, reverse=True):
		if entry.getEndDate() < now  and entry.getEndDate() > lowest:
			# detect repeating events by nameyy
			eventid = entry.getPlainName()
			if eventid not in repeated_events:
				repeated_events[eventid] = 0
			repeated_events[eventid] +=1
			if repeated_events[eventid] > MAX_IN_BEFORE_REPEATED:
				continue
				
			result.append(entry)
			
	return result

def generate_wiki_section(entries):
	result = []
	result.append("=== '''Aktuelles''' ===")
	result.append(u"<!-- Automatisch Generierter Content fängt hier an  -->")
	result.append("----")
	result.append("''siehe auch [[Kalender]] und [[:Kategorie:Termine]] <div style=\"float:right\">[[Termine| Termine verwalten]] (beta)</div>''")
	for i in next_up(entries):
		result.append(i.getMediawikiEntry())
	result.append("----")
	result.append("")
	result.append("==== Neulich: ====")
	result.append("''siehe auch [[Timeline]]''")
	for i in in_before(entries):
		result.append(i.getMediawikiEntry())
	result.append("| style=\"vertical-align: top; width: 20%; padding: 5px; border: 2px solid #dfdfdf;\" |")
	result.append(u"<!-- Automatisch Generierter Content hört hier auf  -->")
	return "\n".join(result)
