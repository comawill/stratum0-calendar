# stratum0-calendar
stratum0-calendar generates multiple calendar/events representations for [stratum0.org](https://stratum0.org)

* ical(ics)-file
* html-calendar using [bootstrap-calendar](https://github.com/Serhioromano/bootstrap-calendar)
* wiki-pages in multiple languages

## Installation
1. `$ pip install -r requirements.txt`
2. setup `config.py` (see `config.py.example` for an example)
3. run `$ ./bot.py`

## Supported Date-Formats

* Event
	* over the whole day `DD.MM.YYYY`
	* at a given time of a day `DD.MM.YYYY hh.mm`
	* at a given time of a day with specific end `DD.MM.YYYY hh.mm-hh.mm`
* Multiple day event
	* `DD.MM.YYYY - DD.MM.YYYY`
	* with start and end time `DD.MM.YYYY hh.mm - DD.MM.YYYY hh.mm`
* Repeating event
	* every week `wd, hh.mm` plus `DD.MM.YYYY - DD.MM.YYYY`
	* every week with end time `wd, hh.mm - hh.mm` plus `DD.MM.YYYY - DD.MM.YYYY`
	* instead of `wd` it is possible to use `wd/n` to generate an event every n-th week



