# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from cabot.cabotapp.alert import AlertPlugin, AlertPluginUserData

from os import environ as env

from irc3.plugins.command import command
from irc3.compat import asyncio
import irc3


# Connect, send the alert on multiple rooms and disconnect
@irc3.plugin
class CabotPlugin(object):
    def __init__(self, bot):
        self.bot = bot

    @irc3.event(irc3.rfc.JOIN)
    def connect(self, mask, channel, **kw):
        # Log on bot connection, disconnect right after
        if mask.nick == self.bot.nick:
            self.say(channel, self.bot.config.messages)

        self.disconnect()

    # The IRC protocol does not accept CR/LF inside a message
    # ref: http://www.ietf.org/rfc/rfc1459.txt section 2.3
    # Send multiple messages instead
    def say(self, channel, messages):
        for message in messages:
            self.bot.privmsg(channel, message)

    # Quit the server and call the end of the asyncio loop
    def disconnect(self):
        # Disconnect only if all messages are sent
        self.bot.config.room_count -= 1
        if self.bot.config.room_count <= 0:
            self.bot.quit()
            self.bot.config.end_callback.set_result('OK')


# Cabot irc alert plugin
class IRCAlert(AlertPlugin):
    name = " IRC"
    author = "nobe4"
    config = {}

    # Check if the bot should alert
    # Inspired by bonniejools/cabot-alert-hipchat
    def shouldAlert(self, service):
        alert = True
        if service.overall_status == service.WARNING_STATUS:
            alert = False  # Don't alert at all for WARNING
        elif service.overall_status == service.ERROR_STATUS:
            if service.old_overall_status in (service.ERROR_STATUS,
                                              service.ERROR_STATUS):
                alert = False  # Don't alert repeatedly for ERROR
        elif service.overall_status == service.PASSING_STATUS:
            alert = False  # Don't alert when passing
        return alert

    # Create the asyncio loop and irc3 bot with current file plugin (matching
    # CabotPlugin defined above)
    def bootstrapIrc3(self):
        # Create the asyncio loop
        loop = asyncio.get_event_loop()
        end_callback = asyncio.Future()

        # Save the end method to be called after posting the message
        self.config['end_callback'] = end_callback
        self.config['includes'] = [__name__]

        # Create the bot and run it once
        sender = irc3.IrcBot.from_config(self.config)
        sender.run(forever=False)

        # Set the asyncio resolve Future
        loop.run_until_complete(end_callback)

    # Generate a list of messages to be displayed in the IRC
    def generate_messages(self, service):
        failing_checks = ', '.join(
            [check.name for check in service.all_failing_checks()]
        )
        messages = [
            "Service " + service.name + " reporting " + service.overall_status + " status",
            "Failing checks : " + failing_checks,
            "(" + settings.WWW_SCHEME + "://" + settings.WWW_HTTP_HOST + ")"
        ]
        return messages

    # Set the requirements from cabot environment
    def configure(self, service, users):
        rooms = [env.get('IRC_ROOM')]

        # Get users room to extends default
        rooms += [
            user.irc_room
            for user in IRCAlertUserData.objects.filter(user__user__in=users)
            if user.irc_room
        ]

        self.config = dict(
            host=env.get('IRC_HOST'),
            port=env.get('IRC_PORT'),
            nick=env.get('IRC_BOT_NICK'),
            autojoins=rooms,
            room_count=len(rooms),
            messages=self.generate_messages(service)
        )

    def send_alert(self, service, users, duty_officers):
        if self.shouldAlert(service):
            self.configure(service, users)
            self.bootstrapIrc3()


# Expose the plugin informations to Cabot
class IRCAlertUserData(AlertPluginUserData):
    name = "IRC Plugin"
    irc_room = models.CharField(max_length=50, blank=True)
