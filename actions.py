import requests, wikipedia
import urbandictionary as ud
import mwaaa

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
        #req = requests.get("http://letty.tk:8000/rds-xml.xsl")
        #r = req.content[29:-9]
        r = "This feature is disabled :("

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
