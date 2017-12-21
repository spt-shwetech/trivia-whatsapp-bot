from app.mac import mac, signals
from modules.trivia import helper
import requests
import texttable
import re
import sys, os
from datetime import datetime

BASE_IP = 'trivia.shweapi.com'
ANIMALS = ['rat', 'ox', 'tiger', 'rabbit', 'dragon', 'snake', 'horse', 'goat', 'monkey', 'rooster', 'dog', 'pig']
#ANIMALS = ['ji','gou','zhu','shu','niu','hu','tu','long','she','ma','yang','hou']
ALLANIMALS = set(ANIMALS)
TEMP = {}

@signals.command_received.connect
def handle(message):
    if message.command == "create":
        create_group(message)
    elif message.command == "init_balance":
        set_init_balance(message)
    elif message.command == "game":
        set_game(message)
    elif message.command == "start":
        start_game(message)
    elif message.command == "register":
        register_user(message)
    elif message.command == "stake":
        create_stake(message)
    elif message.command == "help":
        help(message)
    elif message.command == "end":
        confirm_game(message)
    elif message.command == "yes":
        if TEMP[message.who][-1] != "":
            end_game(message,TEMP[message.who][-1])
    elif message.command == "check":
        check_stake(message)
    elif message.command == "image":
        send_image(message.conversation,'tiger')
    else:
        if message.command:
            help(message, True)


"""
Trivia Games Bot 
"""

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

STAKE_MESSAGE = '''
And then I will guide you how to setup the game.
You can create multiple game session in a group, but make sure the existing game already finish 
before you start again the game session.
------------------------------------------------
To setup the game, please type command follow
#game [rtp] [hours] [groupname]
for example
#game 80 72 groupname
'''

"""
Main Function
"""

def create_group(message):
    params = message.predicate
    print(params)
    if len(params) == 0:
        ambigous("You need to initiate group name", message)
        return
    if len(params) > 24:
        ambigous("Group Name maximal character is 24. Yours is {}".format(len(params)), message)
        return
    group_name = params
    ph_number = message.who.split("@")[0]
    group_id = '{}_{}'.format(ph_number, group_name)
    payload = { "wa_group_name": group_name, "wa_ph_number": ph_number }
    group_check_post = requests.post('http://{}/api/whatsappbot/create_group'.format(BASE_IP), data=payload )
    group_check_data = group_check_post.json()
    is_successful = helper.isResponseSuccess(group_check_post.status_code)
    if not is_successful:
        mac.send_message('Sorry you are failed to create group. the error is: \n', message.conversation)
        mac.send_message(group_check_data['message'], message.conversation)
        return

    mac.create_group(ph_number, group_name, message.conversation, callback=update_group)


def update_group(groupId, group_name, ph_number, conversation):
    who = ph_number+'@s.whatsapp.net'
    payload = {'wa_group_id': groupId, 'wa_group_name': group_name, 'wa_ph_number': ph_number}
    group_update_post = requests.post('http://{}/api/whatsappbot/update_group'.format(BASE_IP), data=payload)
    group_check_data = group_update_post.json()
    mac.send_message("Hi, I am Trivibot, I'll guide your game Before you start the game, please setup the game from my whatapp phone number. Do not run any host commands in this group!", conversation)
    mac.send_message("Great! your {} has succesfully created.".format(group_name), who)
    mac.send_message(GROUP_CREATED, who)
    mac.send_message("Type #help if you ever need any help", conversation)
    #print(group_check_data["message"])

def set_init_balance(message):
    ph_number = message.who.split("@")[0]
    params = message.predicate.split(" ")
    init_point = params[0]
    group_name = " ".join(params[1:])
    # is_in_group = helper.conversationIsGroup(message)
    # if not is_in_group:
    #     mac.send_message("Hello, I can't set your from here, please do it from your group.", message.conversation)
    #     return
    if len(params) < 2:
        mac.send_message("Please specify the default balance and the rtp ammount for your players", message.conversation)
        mac.send_message("You can ask for my #help if you are not sure", message.conversation)
        return
    if len(params) > 10:
        mac.send_message("Please check your command again, it seems it contain too much arguments", message.conversation)
        mac.send_message("You can ask for my #help if you are not sure how to setup", message.conversation)
        return
    is_number_only = helper.isAllNumber(init_point)
    if not is_number_only:
        mac.send_message("Hey, I can't really understand your command. Please only use number for init_point"
                         , message.conversation)
        return

    mac.send_message("Setting the group..", message.conversation)
    group_id= message.conversation.split("@")[0]
    payload = {'wa_ph_number': ph_number, 'init_point': init_point, 'wa_group_name' : group_name}
    set_group_post = requests.post('http://{}/api/whatsappbot/init_balance'.format(BASE_IP), data=payload)
    set_group_data =set_group_post.json()
    if not set_group_data or not set_group_data['message']:
        mac.send_message("I Failed to setup the group, no message field", message.conversation)
        return
    if not helper.isResponseSuccess(set_group_post.status_code):
        mac.send_message('I failed to setup the group, here is the message \n {}'
                         .format(set_group_data['message']), message.conversation)
        return
    #mac.send_message(GROUP_FINISH_SETTING, message.conversation)
    mac.send_message('We already set the initial balance of member is {} credit.'.format(init_point), message.who)
    mac.send_message(STAKE_MESSAGE, message.who)

def register_user(message):
    ph_number = message.who.split("@")[0]
    user_phone_star = ph_number[:5]+"****"
    group_id = message.conversation.split("@")[0]
    
    if (not ph_number or not group_id):
        message.send_message("Error when registering user", message.conversation)
        return

    def get_info(result):
        group_name = result.subject
        payload = {'wa_group_id': group_id, 'wa_ph_number': ph_number}
        register_post = requests.post('http://{}/api/whatsappbot/register_group'.format(BASE_IP), data=payload)
        register_data =register_post.json()
        is_successful = helper.isResponseSuccess(register_post.status_code)
        if not register_data:
            mac.send_message('Sorry I Failed connecting to server', message.conversation)
            return
        if not is_successful:
            #mac.send_message('Sorry you are already registered in {} Group \n '.format(group_name), message.who)
            mac.send_message(register_data['message'], message.who)
            print(register_post.text)
            return

        mac.send_message("{} Success join the game! Good luck!".format(user_phone_star), message.conversation)
        mac.send_message(register_data['message'], message.who)
        if not register_data['init_point']:
            return
        mac.send_message("Congratz! You successfully join {} Group. Your initial balance is {}  ".format(group_name, register_data['init_point']), message.who)
    mac.get_group_name(message.conversation, message.who, callback=get_info)

def create_stake(message):
    params = message.predicate.split(" ")
    

    def is_admin(result):
        if result:
            mac.send_message("Sorry, you can not place a stake in your own group", message.who)
        return
    check_group(message,callback=is_admin)

    if message.conversation == message.who:
        mac.send_message("You can't place a stake from here, please place a stake from the group", message.who)
        return

    if len(params) == 1:
        mac.send_message(HELP_MESSAGE, message.who)
        return

    if len(params) < 2:
        mac.send_message("Too few arguments ! you should specify animal type and the value", message.who)
        return

    if len(params) > 2:
        mac.send_message("I can't understand your stake, seems it contain too much arguments !", message.who)
        return

    (stake,value) = params

    

    user_phone = message.who.split("@")[0]
    user_phone_star = user_phone[:5]+"****"
    group_id = message.conversation.split("@")[0]

    if not helper.isAllNumber(value):
        mac.send_message('Sorry there is something wrong in your stake command! \n Please use #stake [animal name] [amount]', message.who)
        return

    if int(value) < 1:
        mac.send_message('Sorry there is something wrong in your stake command! \n Please use #stake [animal name] [amount]', message.who)
        return

    if not stake in ALLANIMALS:
        mac.send_message('Sorry there is something wrong in your stake command! \n Please use #stake [animal name] [amount]', message.who)
        return

    payload = {'wa_group_id': group_id, 'wa_ph_number': user_phone, 'stake': stake, 'value': value}
    stake_post = requests.post('http://{}/api/whatsappbot/stakes'.format(BASE_IP), data=payload)
    stake_post_data = stake_post.json()
    is_successful = helper.isResponseSuccess(stake_post.status_code)
    if not stake_post_data or not stake_post_data['message']:
        mac.send_message('ERROR connecting to server', message.conversation)
        return
    if not is_successful:
        mac.send_message(stake_post_data['message'], message.who)
        return
    mac.send_message("💰 {} place a stake!".format(user_phone_star), message.conversation)
    mac.send_message("{}".format(stake_post_data['message']), message.who)



def set_game(message):
    ph_number = message.who.split("@")[0]
    params = message.predicate.split(" ")
    rtp = params[0]
    hours = params[1]
    group_name = " ".join(params[2:])

    if len(params) > 10:
        mac.send_message("I Failed to setup the game", message.who)

    if not helper.isAllNumber(rtp):
        mac.send_message('Sorry there is something wrong in your stake command!', message.who)
        return

    if int(rtp) > 101:
        mac.send_message('Sorry there is something wrong in your stake command! \n Please set rtp between 1 and 100', message.who)
        return

    group_id = message.conversation.split("@")[0]
    payload = {'rtp': rtp, 'hours': hours,'wa_ph_number': ph_number,'wa_group_name': group_name }
    start_game_post = requests.post("http://{}/api/whatsappbot/game".format(BASE_IP), data=payload)
    start_game_data =start_game_post.json()
    if not start_game_data or not start_game_data['message']:
        mac.send_message("I failed to start the game session, no message field", message.conversation)
        return
    if not helper.isResponseSuccess(start_game_post.status_code):
        mac.send_message('I failed to start the game, here some error \n {}'
                         .format(start_game_data['message']), message.conversation)
        return
    #print(start_game_data['message'])
    mac.send_message(start_game_data['message'], message.who)
    # mac.send_message('Awesome! Your game settings are:', message.who)
    # mac.send_message('Return to Player = {}%'.format(rtp), message.who)
    # mac.send_message('End Time = {} hours'.format(hours), message.who)
    # mac.send_message('------------------------------- \n Now you can start the game by enter \n #start [group name]', message.who)

def start_game(message):
    ph_number = message.who.split("@")[0]
    params = message.predicate.split(" ")
    if len(params) != 1:
        mac.send_message('Sorry there is something wrong in your stake command!')
        return
    (group_name) = params
    mac.send_message(u"📡 Ok, let's play ! But first, wait me to contact the server guy", message.conversation)
    payload = {'wa_group_name': group_name, 'wa_ph_number': ph_number}
    start_game_post = requests.post("http://{}/api/whatsappbot/start".format(BASE_IP), data=payload)
    start_game_data =start_game_post.json()
    if not start_game_data or not start_game_data['message']:
        mac.send_message("I failed to start the game session, no message field", message.conversation)
        return
    if not helper.isResponseSuccess(start_game_post.status_code):
        mac.send_message('I failed to start the game, here some error \n {}'
                         .format(start_game_data['message']), message.conversation)
        return
    mac.send_message(GAME_STARTED, message.who)

def check_stake(message):
    is_in_group = helper.conversationIsGroup(message)
    if not is_in_group:
        mac.send_message("Hello, I can't set your from here, please do it from your group.", message.conversation)
        return

    group_id = message.conversation.split("@")[0]
    payload = {'wa_group_id': group_id}
    check_stakes_post = requests.post("http://{}/api/whatsappbot/check_stakes".format(BASE_IP), data=payload)
    check_stakes_data =check_stakes_post.json()
    check_stakes_lists = check_stakes_data["list_game"]
    if len(check_stakes_lists) == 0:
        mac.send_message("There isn't any winner in this game", message.conversation)
    check_stakes_rows= [["phone_number", "stake", "value"]]
    for check_stake in check_stakes_lists:
        check_stakes_rows.append([check_stake["phone_number"], check_stake["stake"], check_stake["value"]])
    table = texttable.Texttable()
    table.add_rows(check_stakes_rows)

    mac.send_message(u"📡 Wait, contacting the server guy to see current results", message.conversation)
    mac.send_message(table.draw(), message.conversation)


def confirm_game(message):
    params = message.predicate.split(" ")
    (group_name) = params
    print(group_name)
    if group_name[-1] == "":
        ambigous("You need to initiate group name", message)
        return
    if message.command not in TEMP:
        TEMP[message.who] = [group_name]
    else:
        TEMP[message.who].append(group_name)   
    mac.send_message("Are you sure you want to end game? \n Type #yes or #no", message.who)    

def end_game(message,group_name):
    group_id = message.conversation.split("@")[0]
    ph_number = message.who.split("@")[0]
    payload = {'wa_group_name': group_name, 'wa_ph_number': ph_number}
    end_game_post = requests.post("http://{}/api/whatsappbot/end".format(BASE_IP), data=payload)
    end_game_data = end_game_post.json()
    if not end_game_data or not end_game_data['message']:
        mac.send_message("I failed to end the game session, no message field", message.conversation)
        return
    if not helper.isResponseSuccess(end_game_post.status_code):
        mac.send_message('I failed to end the game, here what the server guy say: \n {}'
                         .format(end_game_data['message']), message.conversation)
        return
    if not end_game_data['wa_group_id']:
        mac.send_message("You are missing group", message.conversation)
        return 
    wa_group_id = end_game_data['wa_group_id']+"@g.us"
    winner_lists = end_game_data["winner_list"]
    if len(winner_lists) == 0:
        mac.send_message("There isn't any winner in this game", wa_group_id)
    winner_rows= [["phone_number", "stakes", "profit"]]
    for winner in winner_lists:
        winner_rows.append([winner["phone_number"], winner["stake"], winner["profit"]])
    table = texttable.Texttable()
    table.add_rows(winner_rows)
    mac.send_message(u'🏁 We have reach the end of the game 🏁 \n '
                     u'🥁🥁🥁 Now I\'ll announce the winners! 🥁🥁🥁', wa_group_id)
    mac.send_message(table.draw(), wa_group_id)
    send_image(wa_group_id,end_game_data["winner_stake"])

def send_image(wa_group_id,animal):
    if animal != "":
        script_dir = sys.path[0]
        img_file = os.path.join(script_dir, 'modules/trivia/img/{}.jpg'.format(animal))
        mac.send_image(img_file, wa_group_id) 

"""
Helper and other command
"""

def check_group(message, callback=None):
    """
    #TODO [UNUSED]
    Check whether the user are the admin of the group
    it needed for some command that can only be call by admin
    :param message:
    :param callback:
    :return:
    """
    is_in_group = helper.conversationIsGroup(message)
    if not is_in_group:
        mac.send_message("Hello, I can't do it from here, please do it from your group.", message.conversation)
        return
    def callback_check_group(isAdmin):
        if not callback:
            return
        callback(isAdmin)
        print(isAdmin)
    mac.get_group_info(message.conversation, message.who, callback=callback_check_group)

def ambigous(text, message):
    ambigous_text = 'Your message seem ambigous. here is your error: \n {}'.format(text)
    mac.send_message(ambigous_text, message.conversation)


def help(message, isLost=False):
    def callback_check_group(isAdmin):
        if isAdmin:
            mac.send_message("Feeling lost ? Here is some command I understand", message.who)
            mac.send_message(HELP_MESSAGE_ROOM, message.conversation)
        else:
            mac.send_message("Here is some command I understand", message.who)
            mac.send_message(HELP_MESSAGE, message.who)
    if isLost:
        mac.send_message("Hi, {} seems you getting lost".format(message.who_name), message.who)
    # check wether sender == conversation
    # if sender == conversation it means it's private chat
    if message.who == message.conversation:
        mac.send_message("Here is some command I understand", message.who)
        mac.send_message(HELP_MESSAGE, message.conversation )
    else:
        group_id = message.conversation.split("@")[0]
        mac.get_group_info(message.conversation, message.who, callback=callback_check_group)

