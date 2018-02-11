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

# import the files required for this to work
import requests, wikipedia
import urbandictionary as ud
import mwaaa

# define a list of commands 
commands = ["?song", "?wiki", "?bye", "?ud", "?/"]
commands += list(mwaaa.reply.keys())
commands += ["PRIVMSG "+mwaaa.nick, mwaaa.updateKey]

def act(c,msg,sender,mem):
    r = ""

    #basic text response
    if c in mwaaa.reply:
        r = mwaaa.reply[c]

    #song
    elif c == "?song":
        req = requests.get("http://letty.tk:8000/rds-xml.xsl")
        r = req.content[29:-9]
        #r = "This feature is disabled :("

    #text replacement
    elif c == "?/":
        mfull = msg[msg.find("?/")+2:]
        mbad = mfull[:mfull.find("/")]
        mgood = mfull[mfull.find("/")+1:]
        try:
            for m in reversed(mem[:-1]):
                if m.find(mbad) != -1 and m.find("?/") == -1:   
                    oldSender = m[:m.find("??")]
                    mes = m[len(oldSender)+2:]
                    preBad = mes[:mes.find(mbad)]
                    postBad = mes[mes.find(mbad)+len(mbad):]
                    fixed = '"'+preBad + mgood + postBad+'"'
                    r = "\x02"+oldSender+"\x02 meant: " +fixed
                    if sender != oldSender:
                        r = "\x02"+sender+'\x02 thinks ' + r
                    return r
        except:
            r = "well that didn't work :/"

    #urban dictionary
    elif c == "?ud":
        query = msg[msg.find("?ud") + 4:].replace('"',"'")
        try:
            defs = ud.define(query)
            for d in defs[:3]:
                r += d.definition.replace('\n', ' ').replace('\r', '')
        except:
            r = "well that didn't work :/"

    #wikipedia
    elif c == "?wiki":
        query = msg[msg.find("?wiki") + 6:]
        try:
            r = wikipedia.summary(query, sentences=3)
        except wikipedia.exceptions.DisambiguationError as e:
            if len(e.options) > 2:
                r = e.options[0]+", "+e.options[1]+", or "+e.options[2]+"?"
            else:
                r = e.options[0]+" or "+e.options[1]+"?"
        except wikipedia.exceptions.PageError as e2:
            r = "Didn't find anything"

    #bot driver
    if c == "PRIVMSG "+mwaaa.nick and sender in mwaaa.admins:
        r = msg[msg.find("PRIVMSG "+mwaaa.nick)+15:]
    elif c == "PRIVMSG "+mwaaa.nick and msg.find("?say") != -1:
        r = msg[msg.find("?say")+5:]
    
    #quit
    if c == "?bye" and sender in mwaaa.admins:
        exit(0)

    if c == mwaaa.updateKey:
        reload(mwaaa)

    return r.encode('utf-8')
