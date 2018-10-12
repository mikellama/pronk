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
import csv, urllib2
import urbandictionary as ud
import mwaaa
import details
import random
from HTMLParser import HTMLParser
# from imdbparser import IMDb
import imdbparser
import sys
import pickle
import os.path
import re
from collections import defaultdict
from wordnik import *
from bs4 import BeautifulSoup
import json

reload(sys)  
sys.setdefaultencoding('utf8')

##  Define a list of commands.
listCommands = ["?song", "?ask", "?wiki", "?ud", "?imdb", "?coin", "?calc", "?poll", "?vote", "?results", "?roll", "?dict", "?weather", "?slap", "?c2f", "?f2c"]

# listCommands.remove("?song")

commands = listCommands + list(mwaaa.reply.keys())
commands += ["PRIVMSG "+details.nick, mwaaa.updateKey, "?list", "?ftb", "?tb"]
commands += ["?ignore", "?save", "?bye", "?ignoring", "?print", "?test"]
commands += ["youtube.com/watch?", "youtu.be/"]

yesNo = ["yes", "no", "y", "n"]
currentSong = "It Will Never Be This"
shutUp = False

client = swagger.ApiClient(details.wnAPI_key, "http://api.wordnik.com/v4")
wordApi = WordApi.WordApi(client)

def saveStatus():
    with open('llamaStatus.pkl', 'w') as f:
        pickle.dump([ignoreList, pollList], f)

def readStatus():
    with open('llamaStatus.pkl', 'r') as f:
        return pickle.load(f)


if os.path.isfile('llamaStatus.pkl') == False:
    print('creating new llamaStatus.pkl file')
    ignoreList = ['spammer']
    pollList = []
    saveStatus()
else:
    ignoreList, pollList = readStatus()


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

    if sender not in ignoreList:

        ##  Basic text response.
        if c in mwaaa.reply:
            r = mwaaa.reply[c]

        ##  Song.
        elif c == "?song":
            global currentSong
            global shutUp
            try:
                req = requests.get("http://letty.tk:8000/status-json.xsl")

                j = json.loads(req.text)
                l = str(j["icestats"]["source"]["listeners"])
                t = j["icestats"]["source"]["title"]
                r = t + " -- " + l + " listeners"
                
                if r != currentSong:
                    shutUp = False
                    
                if shutUp == True and sender not in details.admins:
                    r = ""
                elif r == currentSong and sender not in details.admins:
                    r = "it's still the same song"
                    shutUp = True
                else:
                    shutUp = False
                    currentSong = r
                    '''
                    response = urllib2.urlopen("http://letty.tk/likes.txt")              
                    songList = []
                    
                    cr = csv.reader(response, delimiter="|")
                    for row in cr:
                        songList.append([row[2],row[4]])
                    
                    likes = 0
                    dislikes = 0
                    
                    for song in songList:
                        if song[1] == r:
                            if song[0] == "like":
                                likes += 1
                            else:
                                dislikes += 1
                    if likes > 0 or dislikes > 0:
                        r += " ["                    
                        if likes > 0:
                            r += "+" + str(likes)
                            if dislikes > 0:
                                r += " "
                        if dislikes > 0:
                            r += "-" + str(dislikes)
                        r += "]"                  
                    '''
                    if len(r) < 3:
	                    r = "I don't hear anything."			
            except:
                r = "not now " + sender
        
        ## Weather
        elif c == "?weather":
            place = msg[msg.lower().find("?weather")+9:].split(" ")
            countryState = place.pop()
            city = "_".join(place)
            url = "http://api.wunderground.com/api/" + details.wuAPI_key + "/conditions/forecast/q/"
            url += countryState + "/" + city + ".json"
            try:
                j = json.loads(urllib2.urlopen(url).read())
                if "results" in j["response"]:
                    # r = "Could you be more specific?"
                    url = "http://api.wunderground.com/api/" + details.wuAPI_key + "/conditions/forecast/"
                    url += j["response"]["results"][0]["l"] + ".json"
                    try:
                        j = json.loads(urllib2.urlopen(url).read())
                    except:
                        r = "Nope."
                elif "error" in j["response"]:
                    r = j["response"]["error"]["description"]
                try:
                    f = j["forecast"]["txt_forecast"]["forecastday"]
                    c = j["current_observation"]
                    location = c["display_location"]["full"]

                    #ask for fahrenhiet in US
                    if c["display_location"]["country"] in ["US"]:
                        scale = "fcttext"
                    else:
                        scale = "fcttext_metric"

                    weather = c["weather"] + " " + str(c["temp_f"])+"F/"+str(c["temp_c"])+"C"

                    forecast = ""
                    for i in range(2):
                        if f[i][scale] != "":
                            forecast += f[i]["title"]+": "
                            forecast += f[i][scale] + " "

                    r = " :: ".join([location, weather, forecast])
                except:
                    "Fail."

            except:
                r = "something terrible happened but I'm not sure what..."

        ## Dictionary
        elif c == "?dict":
            words = msg[msg.lower().find("?dict")+6:].lower().split()
            if len(words) > 2:
                r = "?dict <word> [partOfSpeech]"
            elif len(words) == 2:
                definitions = wordApi.getDefinitions(words[0],
                                     partOfSpeech=words[1],
                                     sourceDictionaries='ahd-legacy')
                if definitions != None:
                    r = "[" + definitions[0].partOfSpeech + "] "+definitions[0].text
                else:
                    r = "["+words[1]+"] *"+words[0]+"* not found in dictionary"
            else:
                definitions = wordApi.getDefinitions(words[0],
                                     sourceDictionaries='ahd-legacy')
                if definitions != None:
                    r = "[" + definitions[0].partOfSpeech + "] "+definitions[0].text
                else:
                    r = "*"+words[0]+"* not found in dictionary"                 
        ## Poll
        elif c == "?poll":
            poll = msg[msg.lower().find("?poll") + 6:]
            if poll.find("close #") != -1:
                # close and send results if starter or admin
                pass

            elif poll.find("remove") != -1 and sender in details.admins:
                # if starter or admin, remove poll
                try:                
                    l = poll.find("remove") + 6
                    pollNum = poll[l:l+2]
                    n = int(pollNum)
                    pollList.pop(n-1)
                except:
                    r = "aint no poll #" + pollNum

            elif len(poll) > 1:
                #create new poll
                pollList.append([poll, sender, {}])
                n = len(pollList)
                r = "new poll created #" + str(n)
            else:
                # display active polls (maybe)
                pass
        
        ## Vote
        elif c == "?vote":
            m = msg[msg.lower().find("?vote") + 5:]
            try:
                n = re.search(r'\d+', m).group()
                if m.replace("#","").find(n) > 1:
                    r = 'which number poll?'
                else:
                    pollNum = int(n)-1
                    if pollNum < 0 or pollNum >= len(pollList):
                        r = "#" + n + " is not an active poll"
                    else:
                        if len(m[m.find(n) + len(n):]) == 0:
                            r = "but what is your vote?"
                        else:
                            vote = m[m.find(n) + len(n) + 1:]
                            if vote[-1] == " ":
                                vote = vote[:-1]
                            voteDict = pollList[pollNum][2]
                            voteDict[sender] = vote 

            except:
                r = 'but, which number poll?'
            saveStatus()
        
        ## Poll Results
        elif c == "?results":
            m = msg[msg.lower().find("?results") + 8:]
            try:
                n = re.search(r'\d+', m).group()
                pollNum = int(n)-1
                if len(pollList) < int(n):
                    r = "There is no poll #" + str(n)
                else:
                    voteDict = pollList[pollNum][2]
                    countDict = defaultdict(int)
                    for key, value in voteDict.iteritems():
                        countDict[value] += 1
                    r += pollList[pollNum][0] + " -- "
                    for key, value in countDict.iteritems():
                        r += str(key)+":"+str(value)+", "
                    r = r[:-2]
            except:
                print('?results failure')
            

        ##  get answer from yahoo answers.
        elif c == "?ask":
            try:
                question = msg[msg.lower().find("?ask") + 5:]
                if len(question) > 1:
                    h = HTMLParser()
                    req = requests.get("http://api.haxed.net/answers/?b&q=" + question)
                    r = h.unescape(req.content)
	        if len(r) < 3 or r.find("<br />") >= 0 or r.find("<!DOCTYPE") >= 0:
		        r = "Who knows?"			
            except:
                r = "error getting answer"
                #r = "This feature is disabled :("

        ## List of Commands
        elif c == "?list" and msg[-5:] == "?list":
            r = " ".join(listCommands)

        ## Calculator
        elif c == "?calc":
            equation = msg[msg.lower().find("?calc") + 6:].replace("^", "**")
            try:
                n = round(eval(equation), 4)
                if n.is_integer():
                    n = int(n)
                r = str(n)
            except:
                r = "Is that even math?"

        ## Temp Conversion
        elif c == "?f2c":
            ot = msg[msg.lower().find("?f2c") + 5:]
            try:
                ot = float(ot)
            except:
                r = "uh... numbers please"
            else:
                nt = (ot - 32)*(5/9)
                r = str(round(nt, 2))
        
        elif c == "?c2f":
            ot = msg[msg.lower().find("?c2f") + 5:]
            try:
                ot = float(ot)
            except:
                r = "uh... numbers please"
            else:
                nt = ot*(9/5) + 32
                r = str(round(nt, 2))

        ## Slap
        elif c == "?slap":
            audience = msg[msg.lower().find("?slap") + 6:]
            if len(audience) > 1:
                r = sender + " slaps himself for the amusement of " + audience
            else:
                r = sender + " slaps himself."
        
        ## Ted Bundy
        elif c == "?ftb":
            ted = msg[msg.lower().find("?ftb") + 5:]
            r = "Funny thing about " + ted + ": She turned out to be Ted Bundy right after murdering someone."
        elif c == "?tb":
            ted = msg[msg.lower().find("?tb") + 4:]
            r = "Funny thing about " + ted + ": He turned out to be Ted Bundy right after murdering someone."


        ##  Coin Flip
        elif c == "?coin":
            r = random.sample(["heads", "tails"], 1)
            r = r[0]
		
        ##  Dice
        elif c == "?roll":
            r = "you rolled a "
            r += random.sample(["1", "2", "3", "4", "5", "6"], 1)[0]
		
        ##  Urban Dictionary.
        elif c == "?ud":
            example = False
            n = 999
            try:
                key = msg[msg.lower().find("?ud") + 3]
            except IndexError:
                r = "that's not how this works"
            else:
                if key.lower() == "e":
                    example = True
                    query = msg[msg.lower().find("?ud") + 5:].replace('"',"'")

                elif key.isdigit() and key != ' ':
                    n = int(key)
                    if n == 0:
                        n = 10
                    query = msg[msg.lower().find("?ud") + 5:].replace('"',"'")
                else:
                    query = msg[msg.lower().find("?ud") + 4:].replace('"',"'")
                
                if query.replace(" ", "") == "":
                    r = "that's not how this works"
                else:
                    try:
                        allDefs = ud.define(query)
                        allDefs.sort(key=lambda x: x.upvotes, reverse=True)
                        defs = [d for d in allDefs if d.word.lower() == query.lower()]
                        defs = [d for d in defs if d.upvotes > d.downvotes]

                        if len(defs) == 0:
                            r = "I didn't find anything for '" + query + "'."

                        elif n != 999:
                            if len(defs) < n:
                                r = "I only found " + str(len(defs)) + " matches."
                            else:
                                r = str(n) + ". " + defs[n-1].definition
                                r += " {" + defs[n-1].example + "}"

                        else:
                            for i,d in enumerate(defs):
                                r += str(i+1) + ". " + d.definition
                                if example:
                                    r += " {" + d.example + "}"
                                r += " | "

                        r = r.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
                        r = r.replace("[", "").replace("]", "")
                        r = r.replace('  ', ' ')                    
                
                    except:
                        r = "well that didn't work :/"
                    if r == "":
                        r = "I didn't find anything for '"+query+"'"


        ##  Wikipedia.
        elif c == "?wiki":
            query = msg[msg.lower().find("?wiki") + 6:]
            if len(query) > 1:
                try:
                    r = wikipedia.summary(query, sentences=3)
                except wikipedia.exceptions.DisambiguationError as e:
                    optionCount = min(len(e.options), 14)
                    for c, value in enumerate(e.options[:optionCount-1]):
                        r += value+", "
                    r+= "or " +e.options[optionCount-1]+ "?"
                except wikipedia.exceptions.PageError as e2:
                    r = "Didn't find anything"
            else:
                r = "look up what?"


        ##  IMDb.
        elif c == "?imdb":
            msg += ' '
            title = msg[msg.lower().find("?imdb") + 6:]
            key = msg[msg.lower().find("?imdb") + 5]
            #bu = "https://www.imdb.com/find?q=%s&s=tt&exact=true"
            #imdbparser.searchresult.SearchResult.base_url = bu
            imdb = imdbparser.IMDb()
            r = ""
            k = 0
            searchResult = imdb.search_movie(title)
            searchResult.fetch()
            nResults = len(searchResult.results)
            oneMovie = True
            try:
                if nResults < 1:
                    r = "I didn't find anything"
                    oneMovie = False
                elif key.isdigit():
                    if nResults < int(key):
                        r = "There is no " + key
                        oneMovie = False
                    else:
                        k = int(key)
                elif key == '0' or key.lower() == "l":
                    oneMovie = False
                    movieList = []
                    for i,m in enumerate(searchResult.results[:min(10, nResults)]):
                        mov = str(i+1)+". "+m.title.encode('utf-8')+" ("+str(m.year)+") "
                        mov += "https://imdb.com/title/tt"+str(m.imdb_id)+"/"
                        movieList.append(mov)
                    r = ' | '.join(movieList)

                if oneMovie == True:
                    movie = searchResult.results[k]
                    movie.fetch()
                    r = movie.title.encode('utf-8')
                    if movie.year == None:
                        r+= " ["+movie.release_date+"] "+'-'.join(movie.genres)
                    else:
                        r+=" ("+str(movie.year)+") "+'-'.join(movie.genres)
                    if movie.rating != None:
                        r += " ["+str(movie.rating)+"/10]"
                    if movie.plot != None:
                        r += " " + movie.plot.encode('utf-8')
            except:
                r = "Oh darn. It broke."


        ### ADMIN FEATURES
        ## Save Status and exit
        elif c == "?bye" and sender in details.admins:
            print('goodbye')
            saveStatus()
            exit(0)

        ## Ignore abusers
        elif c == "?ignore" and sender in details.admins:
            person = msg[msg.lower().find("?ignore") + 8:]
            if len(person) == 0:
                pass
            elif person[-1] == " ":
                person = person[:-1]
            if person in ignoreList:
                ignoreList.remove(person)
                print(ignoreList)
            else:
                ignoreList.append(person)
                print(ignoreList)

        ##  Save Status
        elif c == "?save" and sender in details.admins:
            print('status saved to llamaStatus.pkl')
            saveStatus()

        ## Send Ignore List
        elif c == "?ignoring" and sender in details.admins:
            r = ' '.join(ignoreList)

    return r.encode('utf-8')


