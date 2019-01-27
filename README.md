# pronk
## (formerly ircbot-llama)
Legend has it that this little bot will grow and grow into the greatest bot in the world one day!

mwaaa

actions.py is where all functions like ?wiki and ?song live

llamabot.py is the base script that connects to IRC. It imports the useful stuff from actions.py and mwaaa.py

mwaaa.py has some constants defined and contains the dictionary of static replies. 

If you want the bot to respond "foobar" when someone types "?foo", add it to the reply dictionary in mwaaa.py
