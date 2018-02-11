#!/usr/bin/env python

import re, socket, os
from time import sleep
import actions
import mwaaa

# do the thing
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("irc.freenode.net", 6667))
sock.send("USER "+mwaaa.username+" 2 3 "+mwaaa.username+ "\n")
sock.send("NICK "+mwaaa.nick+"\n")
sock.send("PRIVMSG NickServ :identify "+mwaaa.secret+" \n")
sleep(30)  # finish ident before joining channel
sock.send("JOIN "+mwaaa.channel+"\n")

# instantiate message buffer
msgMem = []

while True:
    msg = sock.recv(2048)
    print(msg)
    msg = msg.strip("\n\r")

    sender = msg[1:msg.find('!')]
    
    mloc = msg.find("PRIVMSG "+mwaaa.channel)+len(mwaaa.channel)+10
    msgMem.append(sender +"??"+ msg[mloc:])

    if len(msgMem) > 20:
        msgMem.pop(0)

    if msg.find("PING :") != -1:
        sock.send("PONG :pingis\n")

    if msg.find(mwaaa.updateKey) != -1:
        print("update complete")
        reload(actions)
        reload(mwaaa)

    for command in actions.commands:
        if msg.find(command) != -1:
            r = actions.act(command, msg, sender, msgMem)
            sock.send("PRIVMSG "+mwaaa.channel+" :"+r+"\n")


