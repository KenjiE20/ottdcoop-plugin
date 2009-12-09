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
