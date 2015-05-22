#!/usr/bin/env python
# -.- encoding: utf-8 -.-
import re
import datetime
import time
from dateutil import rrule
import icalendar as ical
import pytz
import calendar
import hashlib
import string
import os
import json
import sys


TIMEZONE = 'Europe/Berlin'
DEFAULT_DURATION = 3  # 3h
MAX_NEXT_UP_REPEATED = 3
MAX_NEXT_UP_REPEATED_DAYS = 4 * 7
MAX_NEXT_UP_DAYS = 31 * 3
MAX_IN_BEFORE_REPEATED = 1
MAX_IN_BEFORE_DAYS = 31

T_CATEGORY = "category"
T_EVENT = "date"
T_INVALID_EVENT = "invalid date"
T_ROW_DIVIDER = "row divider"
T_REST = "rest"

LANG_DE = "de_DE.UTF-8"
LANG_EN = "en_US.UTF-8"
LANG_FR = "fr_CA.UTF-8"


tz = pytz.timezone('Europe/Berlin')


entry = re.compile(r"^\|\s*(.*?)\s*\|\|\s*(.*?)\s*\|\|\s*(.*?)\s*$")

single_date = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
single_date_time = re.compile(r"^(\d+)\.(\d+)\.(\d+)\s+(\d+)[:\.](\d+)$")
single_date_time_range = re.compile(r"^(\d+)\.(\d+)\.(\d+)\s+(\d+)[:\.](\d+)\s*\-\s*(\d+)[:\.](\d+)$")
date_range = re.compile(r"^(\d+)\.(\d+)\.(\d+)\s*\-\s*(\d+)\.(\d+)\.(\d+)$")
date_range_time = re.compile(r"^(\d+)\.(\d+)\.(\d+)\s+(\d+)[:\.](\d+)\s*\-\s*(\d+)\.(\d+)\.(\d+)\s+(\d+)[:\.](\d+)$")
weekday_time = re.compile(r"^([a-zA-Z0-9/]+),?\s*(\d+)[:\.](\d+)$")
weekday_time_range = re.compile(r"^([a-zA-Z0-9/]+),?\s*(\d+)[:\.](\d+)\s*\-\s*(\d+)[:\.](\d+)$")

mediawiki_intern_link = re.compile(r"(\[\[([^|]+)\|?(.*?)\]\])")
mediawiki_extern_link = re.compile(r"(\[([^\ ]+)\s+(.*?)\])")
mediawiki_bold = re.compile(r"'''(.*?)'''")
mediawiki_emph = re.compile(r"''(.*?)''")

category_re = re.compile(r"^==([^=]+)==$")
divider_re = re.compile(r"^\|-$")

dow_regex = re.compile(r"^(\w+)(|/(\d+))$")
dow_index = {
	"mo": 0,
	"mon": 0,
	"di": 1,
	"tue": 1,
	"mi": 2,
	"wed": 2,
	"do": 3,
	"thu": 3,
	"fr": 4,
	"fri": 4,
	"sa": 5,
	"sat": 5,
	"so": 6,
	"sun": 6}

dow_list = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def simple_name(name):
	name = name.lower()
	ok = string.digits + string.lowercase
	new_name = []
	for char in name:
		if char in ok:
			new_name.append(char)
	return "".join(new_name)


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
	intern_url = intern_url.replace(" ", "_")

	def urldecode(match):
		result = ""
		for c in match.groups()[0].encode("utf8"):
			result += "%%%02x" % ord(c)
		return result

	intern_url = re.sub("([\x7f-\xff]+)", urldecode, intern_url)
	return "https://stratum0.org/wiki/%s" % intern_url


def date2datetime(date):
	return tz.localize(datetime.datetime(date.year, date.month, date.day, 0, 0))


class InvalidDateEntryException(Exception):
	pass


class DatePrinter(object):
	def __init__(self, name, category, start_date, end_date):
		self.name = name
		self.rule = None
		self.start_date = start_date
		self.end_date = end_date
		self.category = category
		if self.end_date <= self.start_date:
			raise InvalidDateEntryException

	def getIcal(self):
		event = ical.Event()
		event.add('uid', hashlib.md5(self.name.encode("utf8") + str(self.start_date)).hexdigest() + "@stratum0.org")
		event.add('summary', self.getPlainName().encode("utf8"))
		url = self.getURL()
		if url:
			event.add('url', url.encode("utf8"))
		event.add('dtstart', self.start_date)
		event.add('dtend', self.end_date)
		return event

	def getJson(self):
		result = {}
		result["id"] = hashlib.md5(self.getPlainName().encode("utf8")).hexdigest()
		result["title"] = self.getDetailPlain()
		result["url"] = self.getURL()
		result["class"] = "event-%s" % simple_name(self.category)
		result["start"] = int(time.mktime(self.start_date.timetuple()) * 1000)
		result["end"] = int(time.mktime(self.end_date.timetuple()) * 1000) - 1
		return result

	def getMediawikiRow(self):
		return ("| %s || %s ||" % (self.getMediawikiName(), self.getDateString()))

	def getDateString(self):
		raise Exception("not implemented")

	def getDateRangeString(self):
		raise Exception("not implemented")

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
		name = mediawiki_bold.sub(r"\1", name)
		name = mediawiki_emph.sub(r"\1", name)
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

	def start_datetime(self):
		if type(self.start_date) is datetime.date:
			return date2datetime(self.start_date)
		return self.start_date

	def end_datetime(self):
		if type(self.end_date) is datetime.date:
			return date2datetime(self.end_date)
		return self.end_date

	def __lt__(self, other):
		if isinstance(other, datetime.datetime):
			return self.start_datetime() < other
		if self.start_datetime() >= other.start_datetime() and self.end_datetime() < other.end_datetime():
			return True
		if self.start_datetime() == other.start_datetime():
			if self.end_datetime() == other.end_datetime():
				return self.name < other.name
			return self.end_datetime() < other.end_datetime()
		return self.start_datetime() < other.start_datetime()

	def __le__(self, other):
		if isinstance(other, datetime.datetime):
			return self.start_datetime() <= other
		return self < other or self == other

	def __eq__(self, other):
		return self.start_datetime() == other.start_datetime() and self.end_datetime() == other.end_datetime() and self.name == other.name

	def __gt__(self, other):
		if isinstance(other, datetime.datetime):
			return self.end_datetime() > other
		if self.start_datetime() <= other.start_datetime() and self.end_datetime() > other.end_datetime():
			return True
		if self.start_datetime() == other.start_datetime():
			if self.end_datetime() == other.end_datetime():
				return self.name > other.name
			return self.end_datetime() > other.end_datetime()
		return self.start_datetime() > other.start_datetime()

	def __ge__(self, other):
		if isinstance(other, datetime.datetime):
			return self.end_datetime() >= other
		return self > other or self == other


class SingleDate(DatePrinter):
	def __init__(self, name, category, values):
		day, month, year = map(int, values)
		date = datetime.date(year, month, day)
		date_end = date + datetime.timedelta(days=1)
		DatePrinter.__init__(self, name, category, date, date_end)

	def getDetailPlain(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		return "%s, %02d.%02d.: %s" % (dow, self.start_date.day, self.start_date.month, self.getPlainName())

	def getMediawikiEntry(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		return "* %s, %02d.%02d.: %s" % (dow, self.start_date.day, self.start_date.month, self.getMediawikiName())

	def getDateString(self):
		return "%02d.%02d.%02d" % (self.start_date.day, self.start_date.month, self.start_date.year)


class SingleDateTime(DatePrinter):
	def __init__(self, name, category, values):
		day, month, year, hour, minute = map(int, values)
		date = tz.localize(datetime.datetime(year, month, day, hour, minute))
		date_end = date + datetime.timedelta(hours=DEFAULT_DURATION)
		DatePrinter.__init__(self, name, category, date, date_end)

	def getDetailPlain(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		return "%s, %02d.%02d. %02d:%02d: %s" % (dow, self.start_date.day, self.start_date.month, self.start_date.hour, self.start_date.minute, self.getPlainName())

	def getMediawikiEntry(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		return "* %s, %02d.%02d. %02d:%02d: %s" % (dow, self.start_date.day, self.start_date.month, self.start_date.hour, self.start_date.minute, self.getMediawikiName())

	def getDateString(self):
		return "%02d.%02d.%02d %02d:%02d" % (self.start_date.day, self.start_date.month, self.start_date.year, self.start_date.hour, self.start_date.minute)


class SingleDateTimeRange(DatePrinter):
	def __init__(self, name, category, values):
		day, month, year, hour, minute, hour2, minute2 = map(int, values)
		date = tz.localize(datetime.datetime(year, month, day, hour, minute))
		date_end = tz.localize(datetime.datetime(year, month, day, hour2, minute2))
		if date_end < date:
			date_end += datetime.timedelta(days=1)
		DatePrinter.__init__(self, name, category, date, date_end)

	def getDetailPlain(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		return "%s, %02d.%02d. %02d:%02d - %02d:%02d: %s" % (dow, self.start_date.day, self.start_date.month, self.start_date.hour, self.start_date.minute, self.end_date.hour, self.end_date.minute, self.getPlainName())

	def getMediawikiEntry(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		return "* %s, %02d.%02d. %02d:%02d - %02d:%02d: %s" % (dow, self.start_date.day, self.start_date.month, self.start_date.hour, self.start_date.minute, self.end_date.hour, self.end_date.minute, self.getMediawikiName())

	def getDateString(self):
		return "%02d.%02d.%02d %02d:%02d - %02d:%02d" % (self.start_date.day, self.start_date.month, self.start_date.year, self.start_date.hour, self.start_date.minute, self.end_date.hour, self.end_date.minute)


class DateRange(DatePrinter):
	def __init__(self, name, category, values):
		day, month, year, day2, month2, year2 = map(int, values)
		date = datetime.date(year, month, day)
		date_end = datetime.date(year2, month2, day2) + datetime.timedelta(days=1)
		self.end_date2 = datetime.date(year2, month2, day2)
		DatePrinter.__init__(self, name, category, date, date_end)

	def getDetailPlain(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		dow2 = day_of_week_str(self.end_date2.weekday(), lang)
		to = to_in_lang(lang)
		return "%s, %02d.%02d. %s %s, %02d.%02d.: %s" % (dow, self.start_date.day, self.start_date.month, to, dow2, self.end_date2.day, self.end_date2.month, self.getPlainName())

	def getMediawikiEntry(self, lang=LANG_DE):
		dow = day_of_week_str(self.start_date.weekday(), lang)
		dow2 = day_of_week_str(self.end_date2.weekday(), lang)
		to = to_in_lang(lang)
		return "* %s, %02d.%02d. %s %s, %02d.%02d.: %s" % (dow, self.start_date.day, self.start_date.month, to, dow2, self.end_date2.day, self.end_date2.month, self.getMediawikiName())

	def getDateString(self):
		return "%02d.%02d.%02d - %02d.%02d.%02d" % (self.start_date.day, self.start_date.month, self.start_date.year, self.end_date2.day, self.end_date2.month, self.end_date2.year)


class DateTimeRange(DatePrinter):
	def __init__(self, name, category, values):
		day, month, year, hour, minute, day2, month2, year2, hour2, minute2 = map(int, values)
		date = tz.localize(datetime.datetime(year, month, day, hour, minute))
		date_end = tz.localize(datetime.datetime(year2, month2, day2, hour2, minute2))
		DatePrinter.__init__(self, name, category, date, date_end)

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

	def getDateString(self):
		return "%02d.%02d.%02d %02d:%02d - %02d.%02d.%02d %02d:%02d" % (self.start_date.day, self.start_date.month, self.start_date.year, self.start_date.hour, self.start_date.minute, self.end_date.day, self.end_date.month, self.end_date.year, self.end_date.hour, self.end_date.minute)


class Generator:
	def __init__(self):
		self.entries = []

	def getIcal(self):
		if not self.entries:
			return None
		first = self.entries[0]
		event = first.getIcal()
		interval = first.rule._interval
		until = first.rule._until
		event.add('rrule', {'FREQ': ['WEEKLY'], 'INTERVAL': [interval], 'UNTIL': [until]})
		return event

	def getMediawikiRow(self):
		first = self.entries[0]
		return ("| %s || %s || %s" % (first.getMediawikiName(), self.getDateString(), self.getDateRangeString())).strip()

	def getDateString(self):
		first = self.entries[0]
		interval = first.rule._interval
		if interval > 1:
			interval = "/%d" % interval
		else:
			interval = ""
		return "%s%s, %s" % (dow_list[first.start_date.weekday()], interval, first.getDateString())

	def getDateRangeString(self):
		first = self.entries[0]
		start = first.start_date
		end = first.rule._until
		return "%02d.%02d.%04d - %02d.%02d.%04d" % (start.day, start.month, start.year, end.day, end.month, end.year)

	def __lt__(self, other):
		return self.entries[-1] < other

	def start_datetime(self):
		return self.entries[0].start_datetime()

	def end_datetime(self):
		return self.entries[-1].end_datetime()


class WeekdayTimeRangeGenerator(Generator):
	def __init__(self, name, category, values, rep):
		Generator.__init__(self)
		self.category = category
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
		stop = tz.localize(datetime.datetime(year2, month2, day2, 23, 59))
		rule = rrule.rrule(rrule.WEEKLY, interval=interval, byweekday=wd, dtstart=start, until=stop)
		for event in rule:
			event_end = event + delta
			if nonetime:
				self.entries.append(RepSingleDateTime(name, category, (event.day, event.month, event.year, event.hour, event.minute), rule))
			else:
				if event_end.day != event.day:
					self.entries.append(RepDateTimeRange(name, category, (event.day, event.month, event.year, event.hour, event.minute, event_end.day, event_end.month, event_end.year, event_end.hour, event_end.minute), rule))

				else:
					self.entries.append(RepSingleDateTimeRange(name, category, (event.day, event.month, event.year, event.hour, event.minute, event_end.hour, event_end.minute), rule))


class RepSingleDateTime(SingleDateTime):
	def __init__(self, name, category, values, rule):
		SingleDateTime.__init__(self, name, category, values)
		self.rule = rule

	def getDateString(self):
		return "%02d:%02d" % (self.start_date.hour, self.start_date.minute)


class RepSingleDateTimeRange(SingleDateTimeRange):
	def __init__(self, name, category, values, rule):
		SingleDateTimeRange.__init__(self, name, category, values)
		self.rule = rule

	def getDateString(self):
		return "%02d:%02d - %02d:%02d" % (self.start_date.hour, self.start_date.minute, self.end_date.hour, self.end_date.minute)


class RepDateTimeRange(DateTimeRange):
	def __init__(self, name, category, values, rule):
		DateTimeRange.__init__(self, name, category, values)
		self.rule = rule


class WeekdayTimeGenerator(WeekdayTimeRangeGenerator):
	def __init__(self, name, category, values, rep):
		values = values + (None, None)
		WeekdayTimeRangeGenerator.__init__(self, name, category, values, rep)


tests = [(single_date, SingleDate),
		(single_date_time, SingleDateTime),
		(single_date_time_range, SingleDateTimeRange),
		(date_range, DateRange),
		(date_range_time, DateTimeRange),
		(weekday_time, WeekdayTimeGenerator),
		(weekday_time_range, WeekdayTimeRangeGenerator)]


def analyze_date(name, category, date, rep):
	for regex, dateClass in tests:
		try:
			rg = regex.match(date)
			if rg:
				if issubclass(dateClass, Generator):
					return dateClass(name, category, rg.groups(), rep)
				else:
					return dateClass(name, category, rg.groups())
		except InvalidDateEntryException:
			sys.stderr.write("InvalidDate: %s %s %s %s\n" % (name, category, date, rep))
			sys.stderr.flush()
			return


def tokenize_wiki_page(content):
	result = []
	category = None
	for line in content.splitlines(False):
		line = line.strip()
		dateinfo = entry.match(line)
		if not dateinfo:
			new_cat = category_re.match(line)
			if new_cat:
				category = new_cat.group(1).strip()
				result.append((T_CATEGORY, category))
				continue
			divider = divider_re.match(line)
			if divider:
				result.append((T_ROW_DIVIDER, None))
				continue
			result.append((T_REST, line))
			continue
		name, date, rep = dateinfo.groups()
		obj = analyze_date(name, category, date, rep)
		if obj:
			result.append((T_EVENT, obj))
		else:
			result.append((T_INVALID_EVENT, line))
	return result


def parse_wiki_page(content):
	result = []
	category = None
	for token, value in tokenize_wiki_page(content):
		if token == T_EVENT:
			result.append(value)
	return result


def parse_wiki_page_ordered(pagedata):
	ordered_categories = []
	category = None
	events = {}
	for token, value in tokenize_wiki_page(pagedata):
		if token == T_CATEGORY:
			category = value
			if category not in ordered_categories:
				ordered_categories.append(category)
				events[category] = []
		elif token == T_EVENT:
			events[category].append(value)
	return ordered_categories, events


def move_to_archive(events_text, archive_text, threshold_date):
	n = 0
	events_categories, _ = parse_wiki_page_ordered(events_text)
	archive_categories, archive_events = parse_wiki_page_ordered(archive_text)

	archive_final_categories = list(events_categories)
	for category in archive_categories:
		if category not in archive_final_categories:
			archive_final_categories.append(category)

	flatend = []
	skip_divider = False
	for token, value in tokenize_wiki_page(events_text):
		if token == T_EVENT:
			if value < threshold_date:
				if value.category not in archive_events:
					archive_events[value.category] = []
				archive_events[value.category].append(value)
				n += 1
				skip_divider = True
				continue
		elif token in (T_CATEGORY, T_REST, T_INVALID_EVENT):
			skip_divider = False
		elif token == T_ROW_DIVIDER and skip_divider:
			skip_divider = False
			continue
		flatend.append((token, value))

	archive_flatend = [(T_REST, u"= Termine Archiv =")]
	for category in archive_final_categories:
		if category in archive_events and archive_events[category]:
			archive_flatend.append((T_CATEGORY, category))
			archive_flatend.append((T_REST, u"{| class=\"prettytable\""))
			archive_flatend.append((T_REST, u"! Event !! Termin !! Im Zeitraum"))
			for event in sorted(archive_events[category]):
				archive_flatend.append((T_ROW_DIVIDER, None))
				archive_flatend.append((T_EVENT, event))

			archive_flatend.append((T_REST, u"|}\n"))

	new_events = render_page(flatend)
	new_archive = render_page(archive_flatend)

	return new_events, new_archive, n


def render_page(flatend):
	r = u""
	for token, value in flatend:
		if token == T_REST:
			r += u"%s\n" % value
		elif token == T_CATEGORY:
			r += u"== %s ==\n" % value
		elif token == T_ROW_DIVIDER:
			r += u"|-\n"
		elif token == T_EVENT:
			r += u"%s\n" % value.getMediawikiRow()
		elif token == T_INVALID_EVENT:
			r += u"%s\n" % value
			print str(token), repr(value)
		else:
			print str(token), repr(value)
	return r.strip()


def expand_dates(dates):
	result = []
	for date in dates:
		if issubclass(date.__class__, Generator):
			result.extend(date.entries)
		else:
			result.append(date)
	return result


def next_up(entries, now_):
	repeated_events = {}

	now = now_ - datetime.timedelta(hours=1)
	far_far_away = now + datetime.timedelta(days=MAX_NEXT_UP_REPEATED_DAYS)
	far_far_far_away = now + datetime.timedelta(days=MAX_NEXT_UP_DAYS)
	result = []
	for entry in sorted(entries):
		if entry.end_datetime() > now:
			# detect repeating events by name
			eventid = entry.getPlainName()
			if eventid not in repeated_events:
				repeated_events[eventid] = 0
			repeated_events[eventid] += 1
			if repeated_events[eventid] > MAX_NEXT_UP_REPEATED:
				continue
			# repeated events only in the near future
			if repeated_events[eventid] > 1 and entry.start_datetime() > far_far_away:
				continue

			# restrict all events to not so fare future
			if entry.start_datetime() > far_far_far_away:
				continue

			result.append(entry)

	return result


def in_before(entries, now_):
	repeated_events = {}
	now = now_ - datetime.timedelta(hours=1)
	lowest = now_ - datetime.timedelta(days=MAX_IN_BEFORE_DAYS)
	result = []
	for entry in sorted(entries, reverse=True):
		if entry.end_datetime() < now and entry.end_datetime() > lowest:
			# detect repeating events by nameyy
			eventid = entry.getPlainName()
			if eventid not in repeated_events:
				repeated_events[eventid] = 0
			repeated_events[eventid] += 1
			if repeated_events[eventid] > MAX_IN_BEFORE_REPEATED:
				continue

			result.append(entry)

	return result


def generate_wiki_section(entries, templatefile, lang=LANG_DE, now=None):
	if now is None:
		now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz)
	result = file(templatefile).read().decode("utf8")
	next_dates = []
	for i in next_up(entries, now):
		next_dates.append(i.getMediawikiEntry(lang=lang))
	next_dates = "\n".join(next_dates)
	prev_dates = []
	for i in in_before(entries, now):
		prev_dates.append(i.getMediawikiEntry(lang=lang))
	prev_dates = "\n".join(prev_dates)
	result = result.format(next_dates=next_dates, prev_dates=prev_dates)
	return result.strip()


def write_if_changed(filename, content):
	if not os.path.exists(filename) or content != file(filename).read():
		f = file(filename, "w")
		f.write(content)
		f.close()


def generate_ical(entries, filename):
	cal = ical.Calendar()
	timezone = ical.cal.Timezone()
	timezone.add('TZID', TIMEZONE)
	timezone.add('x-lic-location', TIMEZONE)

	tzs = ical.TimezoneStandard()
	tzs.add('tzname', 'MEZ')
	tzs.add('dtstart', datetime.datetime(1996, 10, 27, 3, 0, 0))
	tzs.add('rrule', {'freq': 'yearly', 'bymonth': 10, 'byday': '-1su'})
	tzs.add('TZOFFSETFROM', datetime.timedelta(hours=2))
	tzs.add('TZOFFSETTO', datetime.timedelta(hours=1))

	tzd = ical.TimezoneDaylight()
	tzd.add('tzname', 'MESZ')
	tzd.add('dtstart', datetime.datetime(1981, 3, 29, 2, 0, 0))
	tzd.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': '-1su'})
	tzd.add('TZOFFSETFROM', datetime.timedelta(hours=1))
	tzd.add('TZOFFSETTO', datetime.timedelta(hours=2))

	timezone.add_component(tzs)
	timezone.add_component(tzd)
	cal.add_component(timezone)

	cal.add('version', '2.0')
	cal.add('prodid', '-//willenbot')
	cal.add('x-wr-calname', 'Stratum 0')

	for entry in entries:
		component = entry.getIcal()
		if component:
			cal.add_component(component)
	write_if_changed(filename, cal.to_ical())


def generate_json_css(entries, jsonfile, cssfile):
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
		"result": e}

	write_if_changed(jsonfile, json.dumps(result).encode("utf8"))

	css_content = ""
	for group in css:
		color = "".join(map(lambda a: chr(int(a * 2, 16) | 0x1F).encode("hex"), list(hashlib.md5(group).hexdigest()[:3])))
		css_content += ".{name},.dh-{name} {{background-color:#{color};}}\n".format(name=group, color=color)
	write_if_changed(cssfile, css_content)
