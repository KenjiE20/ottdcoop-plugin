###
# Copyright (c) 2005, Jeremiah Fincher
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import re
import math
import new

import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.registry as registry
import supybot.callbacks as callbacks

class Ottdcoop(callbacks.PluginRegexp):
    """Add the help for "@help Web" here."""
    threaded = True
    regexps = ['warnSnarfer']
    def __init__(self, irc):
        self.__parent = super(Ottdcoop, self)
        self.__parent.__init__(irc)
        # Schema: {alias: [command, locked, commandMethod]}
        self.abbr = {}
        # XXX This should go.  aliases should be a space separate list, etc.
        group = conf.supybot.plugins.Ottdcoop.abbr
#        for (name, text) in registry._cache.iteritems():
#            name = name.lower()
#             if name.startswith('supybot.plugins.ottdcoop.abbr.'):
#                 name = name[len('supybot.plugins.ottdcoop.abbr.'):]
#                 if '.' in name:
#                     continue
#                 conf.registerGlobalValue(group, name, registry.String('', ''))
#                 conf.registerGlobalValue(group.get(name), 'url',
#                                          registry.Boolean(False, ''))
        for (name, value) in group.getValues(fullNames=False):
            name = name.lower() # Just in case.
            text = value()
            url = value.url()
            self.abbr[name] = [text, url, None]
        for (name, (text, url, _)) in self.abbr.items():
            try:
                f = self.makeAbbrCommand(name)
                self.abbr[name] = [text, url, f]
            except Exception, e:
                self.log.exception('Exception when trying to add abbreviation %s.  '
                                   'Removing from the database.', name)
                del self.abbr[name]

    def isCommandMethod(self, name):
        if not self.__parent.isCommandMethod(name):
            if name in self.abbr:
                return True
            else:
                return False
        else:
            return True

#     def listCommands(self):
#         commands = self.__parent.listCommands()
#         commands.extend(self.abbr.keys())
#         commands.sort()
#         return commands

    def getCommandMethod(self, command):
        try:
            return self.__parent.getCommandMethod(command)
        except AttributeError:
            return self.abbr[command[0]][2]

#     def callCommand(self, command, irc, msg, *args, **kwargs):
#         try:
#             super(Ottdcoop, self).callCommand(command, irc, msg, *args, **kwargs)
#         except utils.error.Error, e:
#             irc.reply(str(e))

    def makeAbbrCommand(self, name):
        docstring = """<no arguments>

        Returns full name and reference url (if defined)
        """
        def f(self, irc, msg, args):
            args.insert(0, name)
            self.get(irc, msg, args)
        f = utils.python.changeFunctionName(f, name, docstring)
        f = new.instancemethod(f, self, Ottdcoop)
        return f

    def get(self, irc, msg, args, name):
        if name in self.abbr:
            text = self.abbr[name][0]
            url = self.abbr[name][1]
            s = format('%s: %s', name, text)
            if url:
                s = format('%s, see also: %s', s, url)
            irc.reply (s, prefixNick=False)
    get = wrap(get, ['commandName'])

    def add(self, irc, msg, args, name, optlist, text):
        """<name> [--over] <text>

        Creates a definition for <name> with the explanation <text>. If
        --over is given, it will overwrite the old definition with the
        new one.
        """
        # Overwrite option
        over = False
        for (option, _) in optlist:
            if option == 'over':
                over = True
        _invalidCharsRe = re.compile(r'[\[\]\s]')
        if _invalidCharsRe.search(name):
            irc.reply ('Names cannot contain spaces or square brackets.')
            return
        if '|' in name:
            irc.reply ('Names cannot contain pipes.')
            return
        # Is already a command
        if self.isCommandMethod(name):
            # But is not a 'def command'
            if name in self.abbr:
                if over:
                    url = self.abbr[name][1]
                    f = self.abbr[name][2]
                    self.abbr[name] = [text, url, f]
                    # Write values to config
                    conf.supybot.plugins.Ottdcoop.abbr.register(name,
                                                        registry.String(text, ''))
                    self.log.info('Adding abbreviation %q for %q (from %s)', text, name, msg.prefix)
                    irc.replySuccess()
                else:
                    irc.reply ('This word is already defined, you can overwrite with --over')
            else:
                irc.reply ('You can\'t overwrite commands in this plugin.')
        # New abbr
        else:
            try:
                f = self.makeAbbrCommand (name)
                self.abbr[name] = [text, None, f]
                # Write values to config
                conf.supybot.plugins.Ottdcoop.abbr.register(name,
                                                    registry.String(text, ''))
                conf.supybot.plugins.Ottdcoop.abbr.get(name).register('url',
                                                    registry.String('', ''))
                self.log.info('Adding abbreviation %q for %q (from %s)', text, name, msg.prefix)
                irc.replySuccess()
            except utils.error.Error, e:
                irc.error(str(e))
                del self.abbr[name]
    add = wrap(add, ['commandName', getopts({'over':''}), 'text'])

    def seturl(self, irc, msg, args, name, optlist, url):
        """<name> [--over] <URL>

        Sets the URL <URL> to <name>. <URL> must be a correct http url. If
        --over is given, it will overwrite the old URL with the new one.
        """
        # Overwrite option
        over = False
        for (option, _) in optlist:
            if option == 'over':
                over = True
        _invalidCharsRe = re.compile(r'[\[\]\s]')
        if _invalidCharsRe.search(name):
            irc.reply ('Names cannot contain spaces or square brackets.')
            return
        if '|' in name:
            irc.reply ('Names cannot contain pipes.')
            return
        # Is already a command
        if self.isCommandMethod(name):
            # But is not a 'def command'
            if name in self.abbr:
                oldurl = self.abbr[name][1]
                regUrl = False
                if oldurl:
                    # URL set once
                    if over:
                        regUrl = True
                    else:
                        irc.reply ('This word already has an URL defined, you can overwrite with --over')
                else:
                    regUrl = True
                if regUrl:
                    # No previous url
                    text = self.abbr[name][0]
                    f = self.abbr[name][2]
                    self.abbr[name] = [text, url, f]
                    # Write values to config
                    conf.supybot.plugins.Ottdcoop.abbr.get(name).url.setValue(url)
                    self.log.info('Adding URL %q for %q (from %s)', url, name, msg.prefix)
                    irc.replySuccess()
            else:
                irc.reply ('You can\'t set url\'s for commands in this plugin.')
        # Unknown abbr
        else:
            irc.reply (format('%s must be added before you can assign it an URL', name))
    seturl = wrap(seturl, ['commandName', getopts({'over':''}), 'httpUrl'])

    def remove(self, irc, msg, args, name):
        """<name>

        Removes the entry <name>.
        """
        if name in self.abbr and self.isCommandMethod(name):
            try:
                self.log.info('Removing abbreviation %q (from %s)', name, msg.prefix)
                del self.abbr[name]
                conf.supybot.plugins.Ottdcoop.abbr.unregister(name)
                irc.replySuccess()
            except utils.error.Error, e:
                    irc.error(str(e))
        else:
            irc.error('There is no such alias.')
    remove = wrap(remove, ['commandName'])

    def glossary (self, irc, msg, args):
        """<no arguments>

        Returns a list of defined lookup words
        """
        words = []
        for (name, (text, url, _)) in self.abbr.items():
            words.append(name)
        if words:
            utils.sortBy(str.lower, words)
            irc.reply(format('Available definitions: %L', words))
        else:
            irc.reply('There are no words defined.')

    def warnSnarfer(self, irc, msg, match):
        r"^\*\*\* Player(| #\d+) joined the game$"
        channel = msg.args[0]
        if not irc.isChannel(channel):
            return
        if callbacks.addressed(irc.nick, msg):
            return
        s = self.registryValue('PlayerReply')
        irc.reply(s, prefixNick=False)

    def clcalc(self, irc, msg, args, rail, tilt, number):
        """<railtype> [<tilt>] <cl|km/h>

        For a number <30 this calculates the speed for <cl> on <railtype>.  For
        any other numbers, this calculates the CL required for <railtype>
        travelling at <km/h>, assuming TL is small enough.  [<tilt>] will
        apply tilt bonuses to the calculation.
        """
        if number < 30:
            intnum = (number * 2) - 1
            if intnum > 13:
                intnum = 13
            if rail == 'erail':
                rail = 'rail'
            if rail == 'rail':
                if number == 1:
                    speed = 88
                else:
                    speed = (232 - pow((13-intnum), 2))
                if tilt:
                    speed += speed / 5
            if rail == 'monorail':
                if number == 1:
                    speed = 88
                else:
                    speed = (232 - pow((13-intnum), 2))
                speed = speed*1.5
                if tilt:
                    speed += speed / 5
            if rail == 'maglev':
                if number == 1:
                    speed = 88
                else:
                    speed = (232 - pow((13-intnum), 2))
                speed = speed*2
                if tilt:
                    speed += speed / 5
            spdmph = speed *10 / 16
            reply = format('A %s Curve Length of %s (', rail, number)
            if intnum == 13:
                reply = format('%scapped at ', reply)
            reply = format('%s%s half tiles)', reply, intnum)
            if tilt:
                reply = format('%s, with tilt bonus,', reply)
            reply = format('%s gives a speed of %skm/h or %smph', reply, ircutils.bold(speed), ircutils.bold(spdmph))
            irc.reply(reply)
        else:
            intspd = number
            if tilt:
                intspd = number/1.2
            if rail == 'erail':
                rail = 'rail'
            if rail == 'rail':
                intcl = int(math.ceil(-math.sqrt(232-min(232, intspd))+13))
            if rail == 'monorail':
                intcl = int(math.ceil(-math.sqrt(231-min(231, (intspd/1.5)))+13))
            if rail == 'maglev':
                intcl = int(math.ceil(-math.sqrt(231-min(231, (intspd/2)))+13))
            cl = int(math.ceil((float(intcl)+1)/2))
            reply = format("Required CL for %s at %skm/h", rail, number)
            if tilt:
                reply = format("%s, with tilt bonus,", reply)
            reply = format("%s is %s (%s half tiles) or TL", reply, ircutils.bold(cl), ircutils.bold(intcl))
            irc.reply(reply)
    clcalc = wrap(clcalc, [("literal", ("rail", "erail", "maglev", "monorail")), optional(("literal", ("tilt"))), "int"])

# monoclspd: echo Monorail speed with CL of $1 is; [math calc 231 - pow((13-$1), 2)+(.5*(231 - pow((13-$1), 2)))]km/h or [math calc (231 - pow((13-$1), 2)+(.5*(231 - pow((13-$1), 2))))* 10 /16]mph
# trainclspd: echo Train speed with CL of $1 is; [math calc 231 - pow((13-2), 2)]km/h or [math calc (231 - pow((13-2), 2))* 10 / 16]mph
# magclspd: echo Maglev speed with CL of $1 is;
#
# traincl: echo CL[math calc floor((-sqrt(231-min(231, $1))+13)* (10**3))/(10.0**3)] required for rail at speed $1km/h (or TL if it's shorter)
# monocl: echo CL[math calc floor((-sqrt(231-min(231, $1/1.5))+13)* (10**3))/(10.0**3)] required for monorail at speed $1km/h (or TL if it's shorter)
# magcl: echo CL[math calc floor((-sqrt(231-min(231, ($1/2)))+13)* (10**3))/(10.0**3)] required for maglev at speed $1km/h (or TL if it's shorter)

Class = Ottdcoop

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
