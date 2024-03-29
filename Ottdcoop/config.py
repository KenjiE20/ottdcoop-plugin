###
# Copyright (c) 2010, Kenji Eva
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

import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Ottdcoop', True)


Ottdcoop = conf.registerPlugin('Ottdcoop')
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(Ottdcoop, 'someConfigVariableName',
#     registry.Boolean(False, """Help for someConfigVariableName."""))
conf.registerChannelValue(Ottdcoop, 'PlayerWarner',
     registry.Boolean(False, """Determines whether the bot will auto warn clients joining as 'Player'"""))
conf.registerChannelValue(Ottdcoop, 'PlayerReply',
     registry.String('Player, please change your in game nick', """What the bot will say if it sees '*** Player joined the game'"""))
conf.registerChannelValue(Ottdcoop, 'MultiWarner',
     registry.Boolean(False, """Determines whether the bot will auto warn clients multiple joining as 'nick #number'"""))
conf.registerChannelValue(Ottdcoop, 'MultiReply',
     registry.String('$name, it appears that you have joined twice, please ask someone to join you, rather than double joining. If this is due to a time-out, you may disregard this.', """What the bot will say if it sees '*** nick #number joined the game'"""))
conf.registerGroup(Ottdcoop, 'abbr')

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
