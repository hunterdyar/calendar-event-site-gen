# built ins
import argparse
import shutil
from datetime import datetime
import json
import urllib.request
# external deps
import icalendar
import chevron
import arrow


def get_template_data():
    with open('template/template.mustache', 'r') as f:
        template = f.read()
    return template


def get_calendar_data(url):
    response = urllib.request.urlopen(url)
    calendar = icalendar.Calendar.from_ical(response.read())
    return calendar


def get_calendar_metadata(calendar):
    # Get the calendar name, preferring xr-wr-calname over name prop.
    name = calendar.get('XR-WR-CALNAME')
    if not name:
        name = calendar.get('NAME')
    zone = calendar.walk('vtimezone')[0].get('TZID')

    return {
        'name': name,
        'timezone': zone,
        'tzname': calendar.get('tzname')
    }


def render(template, calendar, settings, include_past=False):
    out = ""
    args = get_calendar_metadata(calendar)

    # Override calendar settings if set.
    if settings['title']:
        args['name'] = settings['title']
    if settings['timezone']:
        args['timezone'] = settings['timezone']

    args['events'] = []
    skipped = 0
    rendered = 0
    total = 0

    for event in calendar.walk('VEVENT'):
        total += 1
        ndt = event.get('DTSTART').dt
        try:
            start = arrow.Arrow.fromdatetime(ndt)
        except:
            continue

        if not include_past:
            if start < arrow.utcnow():
                skipped += 1
                continue

        # start = start.replace(tzinfo=timezone.utc).astimezone(tz=ZoneInfo(args["timezone"]))
        stamp = arrow.Arrow.fromdatetime(event.get('dtstamp').dt)
        # stamp = stamp.replace(tzinfo=timezone.utc).astimezone(tz=ZoneInfo(args["timezone"]))

        end = arrow.Arrow.fromdatetime(event.get('DTEND').dt)
        description = event.get('x-alt-desc')

        if not description:
            description = event.get('description')
        duration = event.get('duration')
        if not duration:
            duration = (end - start)
        else:
            duration = duration.timedelta
        total_seconds = duration.total_seconds()
        event = {
            'uid': event.get('uid'),
            'class': event.get('class'),
            'geo': event.get('geo'),
            'status': event.get('status'),
            'summary': event.get('summary'),
            'description': description,
            'stamp': stamp,
            'stamp_human': start.humanize(),
            'datetime': start.format(settings['date_format']),
            'stamp_datetime': stamp.format(settings['date_format']),
            'start': start,
            'start_human': start.humanize(),
            'duration': {
                'human': duration,
                # 'human_no_seconds': humanize.precisedelta(duration, minimum_unit="minutes"),
                'duration_total_seconds': total_seconds,
                'hms': str(duration)
            },
            'organizer': event.get('organizer'),
            'location': event.get('location'),
            'priority': event.get('priority'),
            'transp': event.get('transp')
        }
        args['events'].append(event)
        rendered += 1
    out = chevron.render(template, args)
    print(f"Rendered: {rendered}. Skipped: {skipped}. Total: {total} events")
    return out


def apply_default_settings(settings):
    if "date_format" not in settings:
        settings["date_format"] = "%B %d, %Y"
    if "title" not in settings:
        settings["title"] = ""
    if "static_folder" not in settings:
        settings["static_folder"] = "static/"
    if "output_folder" not in settings:
        settings["output_folder"] = "build/"
    if "output_file" not in settings:
        settings["output_file"] = "index.html"
    if "time_format" not in settings:
        settings["time_format"] = "%-I:%M %p %Z"
    if "timezone" not in settings:
        settings["timezone"] = ""
    return settings


parser = argparse.ArgumentParser(description="Generate Calendar Event Site")
parser.add_argument("url", help="a public .ics calendar URL to use as a source.")


def main():
    # we should use command line arguments for the import settings and output file, so github can use SECRETS to make forking the project even easier.
    # import settings
    with open("settings.json", 'r') as f:
        settings = json.load(f)
        settings = apply_default_settings(settings)

    # get calendar and data
    output_file = settings["output_folder"] + settings["output_file"]
    args = parser.parse_args()

    calendar = get_calendar_data(args.url)
    # copy over static folder if it exists.
    shutil.copytree(settings["static_folder"], settings["output_folder"], dirs_exist_ok=True)

    # render and write file
    with open(output_file, 'w+', encoding="utf-8") as f:
        f.write(render(get_template_data(), calendar, settings))
    print(f"Finished Generation.")


if __name__ == "__main__":
    main()
