Cabot IRC Plugin
===

This plugin displays notifications on IRC rooms.

# Installation

    $ pip install cabot-alert-irc

Add `cabot_alert_irc` to the installed apps in settings.py. 

Then run:

    $ foreman run python manage.py syncdb --migrate
    $ foreman start

# Configuration

Provide the following variables in your `<file>.env` (or use the following defaults):

    IRC_HOST=sinisalo.freenode.net
    IRC_PORT=6667
    IRC_BOT_NICK=Cabot_Alert_Bot
    IRC_ROOM=Cabot_Alert_Bot_Test

I suggest you change the `IRC_BOT_NICK` with a custom unique value.

Each user can also register a room from the plugin configuration panel.

# License 

MIT (same as Cabot)
