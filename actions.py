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
from imdbparser import IMDb
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
listCommands = ["?song", "?ask", "?wiki", "?ud", "?imdb", "?coin", "?calc", "?poll", "?vote", "?results", "?roll", "?dict"]
commands = listCommands + list(mwaaa.reply.keys())
commands += ["PRIVMSG "+details.nick, mwaaa.updateKey, "?list", "?ftb", "?tb"]
commands += ["?ignore", "?save", "?bye", "?ignoring", "?print"]
commands += ["youtube.com/watch?"]

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

        ## youtube titles cause the other bots were down
        elif c == "youtube.com/watch?":
            linkStart = msg.find("youtube.com/watch?")
            linkEnd = msg[linkStart:].find(" ") + linkStart + 1
            url = "https://www."
            if linkEnd == linkStart: #no space after URL
                url += msg[linkStart:]
            else: 
                url += msg[linkStart:linkEnd]
        
            page = requests.get(url)
        
            soup = BeautifulSoup(page.text, "lxml")
        
            t = soup.title.text[:-10]
            try:
                v = soup.find("div", {"class": "watch-view-count"}).text
                r = t + " :: " + v
            except:
                r = t

        ## Print Stuff
        elif c == "?print":
            print(pollList)

        ## Dictionary
        elif c == "?dict":
            words = msg[msg.find("?dict")+6:].lower().split()
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
            poll = msg[msg.find("?poll") + 6:]
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
            m = msg[msg.find("?vote") + 5:]
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
            m = msg[msg.find("?results") + 8:]
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
                question = msg[msg.find("?ask") + 5:]
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
                r = sender + " slaps him or herself for the amusement of " + audience
            else:
                r = sender + " slaps him or herself."
        
        ## Ted Bundy
        elif c == "?ftb":
            ted = msg[msg.find("?ftb") + 5:]
            r = "Funny thing about " + ted + ": She turned out to be Ted Bundy right after murdering someone."
        elif c == "?tb":
            ted = msg[msg.find("?tb") + 4:]
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
            try:
                query = msg[msg.find("?ud") + 4:].replace('"',"'")
                defs = ud.define(query)
                for d in defs[:3]:
                    r += d.definition.replace('\n', ' ').replace('\r', ' ')
            except:
                r = "well that didn't work :/"
            if r == "":
                r = "I didn't find anything for '"+query+"'"


        ##  Wikipedia.
        elif c == "?wiki":
            query = msg[msg.find("?wiki") + 6:]
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
		            r = movie.title+" ("+str(movie.year)+") "+'-'.join(movie.genres)+" ["+str(movie.rating)+"/10] "+str(movie.plot)

            except:
	            r = "something went wrong :/"
        
        ### ADMIN FEATURES
        ## Save Status and exit
        elif c == "?bye" and sender in details.admins:
            print('goodbye')            
            saveStatus()
            exit(0)

        ## Ignore abusers
        elif c == "?ignore" and sender in details.admins:
            person = msg[msg.find("?ignore") + 8:]
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


