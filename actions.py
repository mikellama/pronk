#!/usr/bin/env python
#
## Copyright (C) 2018 Mike Rose
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


##  Import the files required for this to work.
from __future__ import division
import requests, wikipedia
import urbandictionary as ud
import mwaaa
import details
import random
from HTMLParser import HTMLParser
from imdbparser import IMDb


##  Define a list of commands.
listCommands = ["?song", "?ask", "?wiki", "?ud", "?imdb", "?coin", "?slap", "?calc", "?/"]
commands = listCommands + list(mwaaa.reply.keys())
commands += ["PRIVMSG "+details.nick, mwaaa.updateKey, "?list"]



def act(c,msg,sender,mem):
    '''
    c is a command from commands list defined above
    msg is the whole message send that contains the command trigger
    sender is part of msg, the nick for the sender
    mem is a list or strings containing the last few 'msg's
    '''
    with open('callLog', 'a') as f:
        f.write(sender+": "+c+"\n"+msg+"\n\n")

    r = ""


    ##  Basic text response.
    if c in mwaaa.reply:
        r = mwaaa.reply[c]


    ##  Song.
    elif c == "?song":
        try:
            req = requests.get("http://letty.tk:8000/rds-xml.xsl")
            h = HTMLParser()
            r = h.unescape(req.content[29:-9])
	    if len(r) < 3:
		r = "I don't hear anything."			
        except:
            r = "not now " + sender
            #r = "This feature is disabled :("

    ##  get answer from yahoo answers.
    elif c == "?ask":
        try:
            question = msg[msg.find("?ask") + 5:]
            if len(question) > 1:
                h = HTMLParser()
                req = requests.get("http://api.haxed.net/answers/?b&q=" + question)
                r = h.unescape(req.content)
	    if len(r) < 3:
		r = "no answer"			
        except:
            r = "error getting answer"
            #r = "This feature is disabled :("

    ## List of Commands
    elif c == "?list":
        r = " ".join(listCommands)

    ## Calculator
    elif c == "?calc":
        equation = msg[msg.find("?calc") + 6:].replace("^", "**")
        try:
            n = round(eval(equation), 4)
            if n.is_integer():
                n = int(n)
            r = str(n)
        except:
            r = "Is that even math?"

    ## Slap
    elif c == "?slap":
        audience = msg[msg.find("?slap") + 6:]
        if len(audience) > 1:
            r = sender + " slaps themself for the amusement of " + audience
        else:
            r = sender + " slaps themself."

    ##  Coin Flip
    elif c == "?coin":
        r = random.sample(["heads", "tails"], 1)
        r = r[0]

    ##  Text replacement.
    elif c == "?/" and msg.find(" :?/") > 1:
        if msg[-1] == '/':
            msg = msg[:-1]
        mfull = msg[msg.find("?/")+2:]
        mbad = mfull[:mfull.find("/")]
        mgood = '\x02' + mfull[mfull.find("/")+1:] + '\x02'
        try:
            for m in reversed(mem[:-1]):
                if m.find(mbad) != -1 and m.find("?/") == -1:   
                    oldSender = m[:m.find("??")]
                    mes = m[len(oldSender)+2:]
                    if mes.startswith("\x01ACTION"): # /me
                        mes = mes[8:-1]
                        action = True
                    else:
                        action = False
                    preBad = mes[:mes.find(mbad)]
                    postBad = mes[mes.find(mbad)+len(mbad):]
                    fixed = preBad + mgood + postBad
                    if action:
                        fixed = "* \x02"+oldSender+"\x02 "+fixed
                    else:
                        fixed = '"'+fixed+'"'
                    r = "\x02"+oldSender+"\x02 meant: " +fixed
                    if sender != oldSender:
                        r = "\x02"+sender+'\x02 thinks ' + r
                    return r
        except:
	    r = "well that didn't work :/"


    ##  Urban Dictionary.
    elif c == "?ud":
        try:
            query = msg[msg.find("?ud") + 4:].replace('"',"'")
            defs = ud.define(query)
            for d in defs[:3]:
                r += d.definition.replace('\n', ' ').replace('\r', ' ')
        except:
            r = "well that didn't work :/"


    ##  Wikipedia.
    elif c == "?wiki":
        try:
            query = msg[msg.find("?wiki") + 6:]
            r = wikipedia.summary(query, sentences=3)
        except wikipedia.exceptions.DisambiguationError as e:
            optionCount = min(len(e.options), 14)
            for c, value in enumerate(e.options[:optionCount-1]):
                r += value+", "
            r+= "or " +e.options[optionCount-1]+ "?"
        except wikipedia.exceptions.PageError as e2:
            r = "Didn't find anything"


    ##  IMDb.
    elif c == "?imdb":
        imdb = IMDb()
        title = msg[msg.find("?imdb") + 6:]
        try:
	    searchResult = imdb.search_movie(title)
	    searchResult.fetch()
	    movie = searchResult.results[0]
	    movie.fetch()
	    if len(searchResult.results) < 1:
		r = "I didn't find anything"
	    else:
		r = movie.title+" ("+str(movie.year)+") "+'-'.join(movie.genres)+" ["+str(movie.rating)+"/10] "+movie.plot
	except:
	    r = "something went wrong :/"


    return r.encode('utf-8')


