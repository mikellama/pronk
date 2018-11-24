#!/usr/bin/python2
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


##  Import the required libraries/files for this to work.
import re, socket, os, time, ssl, base64
import actions
import mwaaa
import details
import requests
import json     
import threading
import time

## open socket
sock = socket.socket()
sock = ssl.wrap_socket(sock)
sock.connect(("irc.freenode.net", 6697))

## Authenticate to Server
sock.send("CAP REQ :sasl\n")
time.sleep(0.5)
sock.send("NICK " + details.nick + " \n")
sock.send("USER " + details.nick + " hostname servername :" + details.username + " \n")
sock.send("AUTHENTICATE PLAIN\n")

null = u"\u0000"
authMessage = details.nick + null + details.nick + null + details.secret
authMessage = base64.b64encode(unicode(authMessage))

while True:
    msg = sock.recv(2048)
    if msg.find("AUTHENTICATE +") != -1:
        sock.send("AUTHENTICATE " + authMessage + "\n")
    if msg.find(":SASL authentication successful") != -1:
        sock.send("CAP END\n")
        print("SASL authentication successful\n")
        break


## Join a channel
sock.send("JOIN "+details.channel+"\n")


##  Instantiate message buffer.
msgMem = []

last_ping = time.time()
timeout = 15 * 60

## Stream Checker
class Checker(threading.Thread):
    def __init__(self):
        super(Checker, self).__init__()
        self.daemon = True
        self.paused = True
        self.state = threading.Condition()
        self.delay = 15
        self.notifyTime = time.time()
        self.streaming = False

    def run(self):
        while True:
            with self.state:
                if self.paused:
                    self.state.wait()
            try:
                q = requests.get("http://letty.tk:8000/status-json.xsl")
                js = json.loads(q.text)
                if "source" in js["icestats"]:
                    # check if it just came up or an annoncement was made recently
                    if self.streaming == False and time.time() - self.notifyTime > 1 * 60:
                        print("streaming!")
                        sock.send("PRIVMSG "+details.channel+" :Music is streaming at http://letty.tk:8000/stream.mp3 !!\n")
                        self.notifyTime = time.time()
                    self.streaming = True
                else:
                    if self.streaming == True and time.time() - self.notifyTime > 5* 60:
                        print("not streaming... but server is online")
                        sock.send("PRIVMSG "+details.channel+" :Silence.\n")
                        self.notifyTime = time.time()
                    self.streaming = False
            except:
                if self.streaming == True and time.time() - self.notifyTime > 5 * 60:
                    print("can't find server")
                    sock.send("PRIVMSG "+details.channel+" :It's quiet now.\n")
                    self.notifyTime = time.time()
                self.streaming = False
            time.sleep(self.delay)

    def resume(self):
        with self.state:
            self.paused = False
            self.state.notify()

    def pause(self):
        with self.state:
            self.paused = True

    def setDelay(self, d):
        self.delay = d
    
    def noMsg(self):
        self.streaming = True


checker = Checker()
checker.start()
checker.resume()

while True:
    msg = sock.recv(2048)
    msg = msg.strip("\n\r")  
    
    sender = msg[1:msg.find('!')]
    mloc = msg.find("PRIVMSG "+details.channel)+len(details.channel)+10
    msgMem.append(sender +"??"+ msg[mloc:])

    if len(msgMem) > 20:
        msgMem.pop(0)

    ##  If you receive a /PING send a response.
    if msg.find("PING :") != -1:
        sock.send("PONG :pingis\n")
        last_ping = time.time()
    ## Break while loop if not PINGed after timeout seconds
    if (time.time() - last_ping) > timeout:
        print("ping timeout")
        break

    if len(msg) < 1 and (msgMem) > 1:
        print("empty buffer exit")
        break


    ##  If you find the update key defined in mwaaa.py, print 'update complete' and reload actions.py and mwaaa.py
    if msg.find(mwaaa.updateKey) != -1:
        print("update complete")
        reload(actions)
        reload(mwaaa)
        reload(details)

    msgLow = msg.lower()
    for command in actions.commands:
        if msgLow.find(command.lower()) != -1:
            r = actions.act(command, msg, sender, msgMem)
            if len(r) > 0:
                try:
                    target = msg.split(' ')[2]
                    if target.lstrip('@+').startswith('#'):
                        sock.send("PRIVMSG "+target+" :"+r+"\n")
                    else:
                        sock.send("PRIVMSG "+sender+" :"+r+"\n")
                except IndexError:
                    pass


    ## special commands for the stream notifier
    if msg.find("?notify-off") != -1 and sender in details.admins:
        checker.pause()
    elif msg.find("?notify-on") != -1 and sender in details.admins:
        checker.resume()
    elif msg.find("?noMsg") != -1 and sender in details.admins:
        checker.noMsg()
    elif msg.find("?delay") != -1 and sender in details.admins:
        try:
            d = int(msg[msg.lower().find("?delay") + 6:])
            checker.setDelay(d)
        except:
            pass

print("It's all over man.")

