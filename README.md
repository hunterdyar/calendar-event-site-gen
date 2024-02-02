#IMM Upcoming Events

Displays upcoming events for the Chatham Immersive Media Lab.
https://chatham-immersive-media-lab.github.io/upcoming-events-site/


# Calendar Events Site Generator
Generate static single serving websites for events from a calendar

## How It Works
This repository runs a GitHub Action which runs generate.py. This script downloads an .ics calendar file, which is a standard way to share calendar's by URL, and turns it into an HTML file. It uses the [mustache](https://mustache.github.io/) templating language.
Once the action is set up to run on a regular interval, the site - available through github pages - will update. The site does not dynamically grab the calendar events, it simply generates a static website file.

## Setup
1. Fork this repository.
2. In Settings, Evironments, 'github-pages' environment, add a environmnent variable called 'CALENDAR_URL' with the value of the public url (ending in .ics)
3. Optional: Modify settings.json. 
4. Modify template.mustache.
5. Enable github pages, set it to deploy from an action.
6. Enable the actions (in the Actions tab; A forked repo won't run actions by default)
