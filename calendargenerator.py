#!/usr/bin/env python
# -.- encoding: utf-8 -.-
import re
import datetime
import time
from dateutil import rrule
import icalendar as ical
import pytz
import calendar
import md5

tz = pytz.timezone('Europe/Berlin')


entry = re.compile("^\|\s*(.*?)\s*\|\|\s*(.*?)\s*\|\|\s*(.*?)\s*$")

single_date = re.compile("^(\d+)\.(\d+)\.(\d+)$")
single_date_time = re.compile("^(\d+)\.(\d+)\.(\d+)\s+(\d+)[:\.](\d+)$")
single_date_time_range = re.compile("^(\d+)\.(\d+)\.(\d+)\s+(\d+)[:\.](\d+)\s*\-\s*(\d+)[:\.](\d+)$")
date_range = re.compile("^(\d+)\.(\d+)\.(\d+)\s*\-\s*(\d+)\.(\d+)\.(\d+)$")
date_range_time = re.compile("^(\d+)\.(\d+)\.(\d+)\s+(\d+)[:\.](\d+)\s*\-\s*(\d+)\.(\d+)\.(\d+)\s+(\d+)[:\.](\d+)$")
weekday_time = re.compile("^([a-zA-Z0-9/]+),?\s*(\d+)[:\.](\d+)$")
weekday_time_range = re.compile("^([a-zA-Z0-9/]+),?\s*(\d+)[:\.](\d+)\s*\-\s*(\d+)[:\.](\d+)$")

mediawiki_intern_link = re.compile(r"(\[\[([^|]+)\|?(.*)\]\])")
mediawiki_extern_link = re.compile(r"(\[([^\ ]+)\s+(.*)\])")

dow_regex = re.compile(r"^(\w+)(|/(\d+))$")
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


DEFAULT_DURATION = 3 #3h
MAX_NEXT_UP_REPEATED = 3
MAX_IN_BEFORE_REPEATED = 1



LANG_DE = "de_DE.UTF-8"
LANG_EN = "en_US.UTF-8"
LANG_FR = "fr_CA.UTF-8"

def day_of_week_str(day_of_week, lang):
	with calendar.TimeEncoding(lang):
		return calendar.day_abbr[day_of_week].title()

def short_lang(lang):
	return lang.split("_")[0]

def to_in_lang(lang):
	slang = short_lang(lang)
	if slang == "en":
		return "to"
	elif slang == "de":
		return "bis"
	elif slang == "fr":
		return u"à"
	return "--"

def make_extern(intern_url):
	return "https://stratum0.org/wiki/%s" % intern_url.replace(" ", "_")

class DatePrinter(object):
	def __init__(self, name, start_date, end_date):
		self.name = name
		self.rule = None
		self.start_date = start_date
		self.end_date = end_date

	def getIcal(self):
		event = ical.Event()
		event.add('summary', self.getPlainName().encode("utf8"))
		url = self.getURL()
		if url:
			event.add('url', url.encode("utf8"))
		event.add('dtstart', self.start_date)
		event.add('dtend', self.end_date)
		return event
	
	def getJson(self):
		result = {}
		result["id"] = md5.new(self.getPlainName().encode("utf8")).hexdigest()
		result["title"] = self.getDetailPlain()
		result["url"] = self.getURL()
		result["class"] = "event-important"
		result["start"] = int(time.mktime(self.start_date.timetuple()) * 1000)
		result["end"] = int(time.mktime(self.end_date.timetuple()) * 1000)
		
		return result
		
	def getMediawikiEntry(self, lang=LANG_DE):
		raise Exception("not implemented")

	def getDetailPlain(self, lang=LANG_DE):
		raise Exception("not implemented")
	
	def getMediawikiName(self):
		return self.name

	def getPlainName(self):
		def fix_intern(match):
			_, url, name = match.groups()
			if name:
				return name
			return url
		name = mediawiki_intern_link.sub(fix_intern, self.name)
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
		return other > self.start_date

	def __gt__(self, other):
		return other < self.end_date


class SingleDate(DatePrinter):
	def __init__(self, name, values):
		day, month, year = map(int, values)
		date = tz.localize(datetime.datetime(year, month, day, 0 , 0))
		date_end = date + datetime.timedelta(days=1)
		DatePrinter.__init__(self, name, date, date_end)
	
	def getDetailPlain(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		return "%s, %02d.%02d.: %s" % (dow, self.start_date.day, self.start_date.month, self.getPlainName())

	def getMediawikiEntry(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		return "* %s, %02d.%02d.: %s" % (dow, self.start_date.day, self.start_date.month, self.getMediawikiName())


class SingleDateTime(DatePrinter):
	def __init__(self, name, values):
		day, month, year, hour, minute = map(int, values)
		date = tz.localize(datetime.datetime(year, month, day, hour, minute))
		date_end = date + datetime.timedelta(hours=DEFAULT_DURATION)
		DatePrinter.__init__(self, name, date, date_end)
	
	def getDetailPlain(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		return "%s, %02d.%02d. %02d:%02d: %s" % (dow, self.start_date.day, self.start_date.month, self.start_date.hour, self.start_date.minute, self.getPlainName())

	def getMediawikiEntry(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		return "* %s, %02d.%02d. %02d:%02d: %s" % (dow, self.start_date.day, self.start_date.month, self.start_date.hour, self.start_date.minute, self.getMediawikiName())


class SingleDateTimeRange(DatePrinter):
	def __init__(self, name, values):
		day, month, year, hour, minute, hour2, minute2 = map(int, values)
		date = tz.localize(datetime.datetime(year, month, day, hour, minute))
		date_end = tz.localize(datetime.datetime(year, month, day, hour2, minute2))
		DatePrinter.__init__(self, name, date, date_end)
	
	def getDetailPlain(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		return "%s, %02d.%02d. %02d:%02d - %02d:%02d: %s" % (dow, self.start_date.day, self.start_date.month, self.start_date.hour, self.start_date.minute, self.end_date.hour, self.end_date.minute, self.getPlainName())
	
	def getMediawikiEntry(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		return "* %s, %02d.%02d. %02d:%02d - %02d:%02d: %s" % (dow, self.start_date.day, self.start_date.month, self.start_date.hour, self.start_date.minute, self.end_date.hour, self.end_date.minute, self.getMediawikiName())


class DateRange(DatePrinter):
	def __init__(self, name, values):
		day, month, year, day2, month2, year2 = map(int, values)
		date = tz.localize(datetime.datetime(year, month, day, 0, 0))
		date_end = tz.localize(datetime.datetime(year2, month2, day2, 0, 0))
		DatePrinter.__init__(self, name, date, date_end)
	
	def getDetailPlain(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		dow2 = day_of_week_str(self.end_date.weekday(), lang)
		to = to_in_lang(lang)
		return "%s, %02d.%02d. %s %s, %02d.%02d.: %s" % (dow, self.start_date.day, self.start_date.month, to, dow2, self.end_date.day, self.end_date.month, self.getPlainName())
	
	def getMediawikiEntry(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		dow2 = day_of_week_str(self.end_date.weekday(), lang)
		to = to_in_lang(lang)
		return "* %s, %02d.%02d. %s %s, %02d.%02d.: %s" % (dow, self.start_date.day, self.start_date.month, to, dow2, self.end_date.day, self.end_date.month, self.getMediawikiName())


class DateTimeRange(DatePrinter):
	def __init__(self, name, values):
		day, month, year, hour, minute, day2, month2, year2, hour2, minute2 = map(int, values)
		date = tz.localize(datetime.datetime(year, month, day, hour, minute))
		date_end = tz.localize(datetime.datetime(year2, month2, day2, hour2, minute2))
		DatePrinter.__init__(self, name, date, date_end)
	
	def getDetailPlain(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		dow2 = day_of_week_str(self.end_date.weekday(), lang)
		to = to_in_lang(lang)
		return "%s, %02d.%02d. %02d:%02d %s %s, %02d.%02d. %02d:%02d: %s" % (dow, self.start_date.day, self.start_date.month, self.start_date.hour, self.start_date.minute, to, dow2, self.end_date.day, self.end_date.month, self.end_date.hour, self.end_date.minute, self.getPlainName())

	def getMediawikiEntry(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		dow2 = day_of_week_str(self.end_date.weekday(), lang)
		to = to_in_lang(lang)
		return "* %s, %02d.%02d. %02d:%02d %s %s, %02d.%02d. %02d:%02d: %s" % (dow, self.start_date.day, self.start_date.month, self.start_date.hour, self.start_date.minute, to, dow2, self.end_date.day, self.end_date.month, self.end_date.hour, self.end_date.minute, self.getMediawikiName())


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
		wd, _, interval = dow.groups()
		if interval:
			interval = int(interval)
		else:
			interval = 1
		if wd.lower() not in dow_index:
			return
		wd = dow_index[wd.lower()]
		day, month, year, day2, month2, year2 = map(int, rep.groups())
		start = tz.localize(datetime.datetime(year, month, day, hour, minute))
		start2 = tz.localize(datetime.datetime(year, month, day, hour2, minute2))
		if start2 < start:
			start2 += datetime.timedelta(days=1)
		delta = start2 - start
		stop = tz.localize(datetime.datetime(year2, month2, day2, 0, 0))
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
class RepDateTimeRange(DateTimeRange):
	def __init__(self, name, values, rule):
		DateTimeRange.__init__(self, name, values)
		self.rule = rule

class WeekdayTimeGenerator(WeekdayTimeRangeGenerator):
	def __init__(self, name, values, rep):
		values = values + (None, None)
		WeekdayTimeRangeGenerator.__init__(self, name, values, rep)


tests = [(single_date, SingleDate),
		(single_date_time, SingleDateTime),
		(single_date_time_range, SingleDateTimeRange),
		(date_range, DateRange),
		(date_range_time, DateTimeRange),
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
		if entry.end_date > now:
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
		if entry.end_date < now  and entry.end_date > lowest:
			# detect repeating events by nameyy
			eventid = entry.getPlainName()
			if eventid not in repeated_events:
				repeated_events[eventid] = 0
			repeated_events[eventid] +=1
			if repeated_events[eventid] > MAX_IN_BEFORE_REPEATED:
				continue
				
			result.append(entry)
			
	return result

def generate_wiki_section(entries, templatefile, lang=LANG_DE):
	result = file(templatefile).read().decode("utf8")
	next_dates = []
	for i in next_up(entries):
		next_dates.append(i.getMediawikiEntry(lang=lang))
	next_dates = "\n".join(next_dates)
	prev_dates = []
	for i in in_before(entries):
		prev_dates.append(i.getMediawikiEntry(lang=lang))
	prev_dates = "\n".join(prev_dates)
	result = result.format(next_dates=next_dates, prev_dates=prev_dates)
	return result
