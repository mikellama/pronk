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


# import the required libraries/files for this to work
import re, socket, os
from time import sleep
import actions
import mwaaa
import details

# Connect to the internet, then to IRC(at freenode for now, but it can be changed to other servers)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("irc.freenode.net", 6667))
sock.send("USER "+details.username+" 2 3 "+details.username+ "\n")
sock.send("NICK "+details.nick+"\n")

# use mwaaa.secret to use the password from the mwaaa.py file. 
sock.send("PRIVMSG NickServ :identify "+details.secret+" \n")
sleep(30)  # finish ident before joining channel
sock.send("JOIN "+details.channel+"\n")

# instantiate message buffer
msgMem = []

while True:
    msg = sock.recv(2048)
    print(msg)
    msg = msg.strip("\n\r")

    sender = msg[1:msg.find('!')]
    
    mloc = msg.find("PRIVMSG "+details.channel)+len(details.channel)+10
    msgMem.append(sender +"??"+ msg[mloc:])

    if len(msgMem) > 20:
        msgMem.pop(0)
        
# if you receive a /PING send a response
    if msg.find("PING :") != -1:
        sock.send("PONG :pingis\n")
# if you find the update key defined in mwaaa.py, print 'update complete' and reload actions.py and mwaaa.py
    if msg.find(mwaaa.updateKey) != -1:
        print("update complete")
        reload(actions)
        reload(mwaaa)

    for command in actions.commands:
        msgLow = msg.lower()
        if msgLow.find(command.lower()) != -1:
            r = actions.act(command, msg, sender, msgMem)
            try:
                target = msg.split(' ')[2]
                if target.lstrip('@+').startswith('#'):
                    sock.send("PRIVMSG "+target+" :"+r+"\n")
                else:
                    sock.send("PRIVMSG "+sender+" :"+r+"\n")
            except IndexError:
                pass

