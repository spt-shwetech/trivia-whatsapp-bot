import  re
"""
Long Messages
"""

HELP_MESSAGE = u'''
ℹ️ Type #stake [animal] [ammount] to stake
You can set rat, ox, tiger, rabbit, dragon, snake, horse, goat, monkey, rooster, dog, pig
'''

HELP_MESSAGE_ROOM = u'''
Hey, welcome to the room, I am your guide.
To be able to play along, you should register yourself with #register.

ℹ️ and here's some other commands I understand
📩 type #register to register yourself to a game in this group
💰 type #stake [animal] [ammount] to stake

Have fun!
'''

GROUP_CREATED = '''
At the first, please setup initial balance of member by sending this command below:
#init_balance [amount of credit] groupname
for example :
#init_balance 1000 groupname
above command means that when a player register, each player will get 1000 credit upon registration.
'''

GROUP_FINISH_SETTING = '''
I finish setting up your game,
You can ask me to start your game at any time by using #start command
'''

GAME_STARTED = u'''
Perfect! 🏁 Ok we can start the game. 🏁
🎉 You can invite your friends to the group now.
'''

INVALID_MESSAGE = '''
Your command is not listed in our systems.Please type #help if you ever need any help.
'''

"""
HELPER FOR TRIVIA
"""

def isResponseSuccess(statusCode):
    """
    check if response is successful http response
    :param statusCode:
    :return:
    """
    if statusCode >= 200 and statusCode < 300:
        return True
    return False

def conversationIsGroup(message):
    """
    Check if conversation is group or personal
    if sender == conversation name it means it a private for user
    if sender != conversation it need to check
    :param conversation:
    :return boolean:
    """
    if message.conversation == message.who:
        return False
    return True

def isAllNumber(value):
    regex = re.compile("[0-9]")
    if not regex.match(value):
        return False
    return True
