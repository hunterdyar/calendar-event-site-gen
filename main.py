import datetime
import json
import urllib.request
import icalendar
import chevron
import humanize


def get_template_data():
    with open('template/template.mustache', 'r') as f:
        template = f.read()
    return template


def get_calendar_data(url):
    response = urllib.request.urlopen(url)
    calendar = icalendar.Calendar.from_ical(response.read())
    return calendar


def get_calendar_metadata(calendar):
    return {
        'name': calendar.get('XR-WR-CALNAME'),
        'timezone': calendar.get('tzid')
    }


def render(template,calendar, include_past=False):
    out = ""
    args = get_calendar_metadata(calendar)
    args['events'] = []

    for event in calendar.walk('VEVENT'):
        start = event.get('DTSTART').dt

        if not include_past:
            if start < datetime.datetime.now(datetime.timezone.utc):
                continue

        stamp = event.get('dtstamp').dt

        duration = event.get('duration')
        end = event.get('DTEND').dt
        description = event.get('x-alt-desc')

        if not description:
            description = event.get('description')
        if not duration:
            duration = (end - start)
        else:
            duration = duration.timedelta

        event = {
            'uid': event.get('uid'),
            'class': event.get('class'),
            'geo': event.get('geo'),
            'status': event.get('status'),
            'summary': event.get('summary'),
            'description': description,
            'stamp': stamp,
            'start': start,
            'duration': {
                'human': humanize.precisedelta(duration),
                'human_no_seconds': humanize.precisedelta(duration, minimum_unit="minutes"),
                'duration_total_seconds': duration.total_seconds(),
                'hms': str(duration)
            },
            'organizer': event.get('organizer'),
            'location': event.get('location'),
            'priority': event.get('priority'),
            'transp': event.get('transp')

        }
        args['events'].append(event)
    out = chevron.render(template, args)
    return out


def main():
    # we should use command line arguments for the import settings and output file, so github can use SECRETS to make forking the project even easier.
    # import settings
    with open("settings.json",'r') as f:
        settings = json.load(f)

    output_file = settings["output_file"]
    calendar = get_calendar_data(settings["calendar_url"])

    with open(output_file,'w',encoding = "utf-8") as f:
        f.write(render(get_template_data(), calendar))

    print("finished.")


if __name__ == "__main__":
    main()
