# IMM Upcoming Events

Displays upcoming events for the Chatham Immersive Media Lab.
https://chatham-immersive-media-lab.github.io/upcoming-events-site/

### How It Works
This repository runs a GitHub Action which runs generate.py. This script downloads an .ics calendar file, which is a standard way to share calendar's by URL, and turns it into an HTML file. It uses the [mustache](https://mustache.github.io/) templating language.
Once the action is set up to run on a regular interval, the site - available through github pages - will update. The site does not dynamically grab the calendar events, it simply generates a static website file.

