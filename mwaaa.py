#!/usr/bin/env python
#
## Copyright (C) 2018 MikeLlama
#
## This is version 0.5 of the Copyfree Open Innovation License.
##
## ## Terms and Conditions
##
## Redistributions, modified or unmodified, in whole or in part, must retain
## applicable copyright or other legal privilege notices, these conditions, and
## the following license terms and disclaimer.  Subject to these conditions, the
## holder(s) of copyright or other legal privileges, author(s) or assembler(s),
## and contributors of this work hereby grant to any person who obtains a copy of
## this work in any form:
## 
## 1. Permission to reproduce, modify, distribute, publish, sell, sublicense, use,
## and/or otherwise deal in the licensed material without restriction.
## 
## 2. A perpetual, worldwide, non-exclusive, royalty-free, irrevocable patent
## license to reproduce, modify, distribute, publish, sell, use, and/or otherwise
## deal in the licensed material without restriction, for any and all patents:
## 
##     a. Held by each such holder of copyright or other legal privilege, author
##     or assembler, or contributor, necessarily infringed by the contributions
##     alone or by combination with the work, of that privilege holder, author or
##     assembler, or contributor.
## 
##     b. Necessarily infringed by the work at the time that holder of copyright
##     or other privilege, author or assembler, or contributor made any
##     contribution to the work.
## 
## NO WARRANTY OF ANY KIND IS IMPLIED BY, OR SHOULD BE INFERRED FROM, THIS LICENSE
## OR THE ACT OF DISTRIBUTION UNDER THE TERMS OF THIS LICENSE, INCLUDING BUT NOT
## LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE,
## AND NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS, ASSEMBLERS, OR HOLDERS OF
## COPYRIGHT OR OTHER LEGAL PRIVILEGE BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER
## LIABILITY, WHETHER IN ACTION OF CONTRACT, TORT, OR OTHERWISE ARISING FROM, OUT
## OF, OR IN CONNECTION WITH THE WORK OR THE USE OF OR OTHER DEALINGS IN THE WORK.
#


# change all of these things:

nick = "pronk"          # the nickname the bot uses
username = "pronk"      # the bot's username
channel = "##llamas"  # the channel it joins when you start the bot script 
secret = "notreallythis" 
updateKey = "?update"   # the command for updating the bot
admins = ["mikez"]      # a list of admins for the bot, who can give commands 

# the reply ["?foo"] list below defines a list of replies for preset commands that can be used for comedic effect
reply = dict()
reply["?letty"] = "All hail letty, our llama queen. She's leet af."
reply["?Zerock"] = "Henlo. Please remember, Zerock is the leetest llama."
reply["?Time-Warp"] = "OH NOZ"
reply["?help"] = "You're on your own."
reply["?Roserin"] = "?Roserin ?Roserin ?Roserin!"
reply["?mikez"] = "My daddy :)"
reply["?pebble"] = "o"
reply["?mwaaa"] = "That's llama speak."
reply["?pronk"] = "who me? llamabot by mikellama, https://github.com/mikellama/ircbot-llama/"
reply["?website"] = "http://llamas.haxed.net"
reply["?radio"] = "letty.tk"
reply["?fChanX"] = "She's young and vibrant and perfect <3"
reply["?[n0mad]"] = "[n0mwaaad]"
reply["?stuff"] = "?song ?wiki ?ud ?/old/new ?help"
reply["?more"] = "No! No more!"
reply["?duckgoose"] = "The coolest duck/goose hybrid around. He's so perfect, words can't describe his awesomeness."
reply["?shantaram3013"] = "The cliche Asian whiz kid/horny teenager. Loves electrical engineering and hanging out on ##llamas."
