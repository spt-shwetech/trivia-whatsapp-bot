from app.mac import mac, signals
from modules.trivia import helper
import requests
import texttable
import re
import sys, os
from datetime import datetime

#BASE_IP = 'trivia.shweapi.com'
BASE_IP = 'localhost/trivia'
ANIMALS = ['rat', 'ox', 'tiger', 'rabbit', 'dragon', 'snake', 'horse', 'goat', 'monkey', 'rooster', 'dog', 'pig']
#ANIMALS = ['ji','gou','zhu','shu','niu','hu','tu','long','she','ma','yang','hou']
ALLANIMALS = set(ANIMALS)
TEMP = {}

#List API TRIVIA
API_TOP_UP_GROUP            = 'http://{}/api/top_up_group'.format(BASE_IP)
API_CREATE_GROUP            = 'http://{}/api/create_group'.format(BASE_IP)
API_UPDATE_GROUP            = 'http://{}/api/update_group'.format(BASE_IP)
API_CREATE_SESSIONS         = 'http://{}/api/create_sessions'.format(BASE_IP)
API_REGISTER_MEMBERS        = 'http://{}/api/register_members'.format(BASE_IP)
API_CREATE_GAME             = 'http://{}/api/create_game'.format(BASE_IP)
API_START_GAME              = 'http://{}/api/start_game'.format(BASE_IP)
API_END_GAME                = 'http://{}/api/end_game'.format(BASE_IP)
API_STAKES                  = 'http://{}/api/stakes'.format(BASE_IP)
API_CHECK_STAKES_MEMBERS    = 'http://{}/api/check_stakes_members'.format(BASE_IP)
API_TOP_UP_AGENT            = 'http://{}/api/top_up_agent'.format(BASE_IP)
API_TOP_UP_GROUP            = 'http://{}/api/top_up_group'.format(BASE_IP)
API_LIST_STAKES             = 'http://{}/api/list_stakes'.format(BASE_IP)
API_END_SESSIONS            = 'http://{}/api/end_sessions'.format(BASE_IP)


@signals.command_received.connect
def handle(message):
    if message.conversation != message.who :
        if message.command == "ckstakes":
            check_all_stakes_in_game(message)
        elif message.command == "ltstakes":
            check_all_list_stakes(message)
        elif message.command == "register":
            member_registration(message)
        elif message.command == "stake":
            user_place_a_stake(message)
        else:
            if message.command:
                help(message, True)
    else:
        if message.command == "tpagent":
            print(message.command)
        elif message.command == "tpgroup":
            top_up_group(message)
        elif message.command == "ctgroup":
            create_group(message)
        elif message.command == "ctsessions":
            create_sessions(message)
        elif message.command == "ctgame":
            create_game(message)
        elif message.command == "start":
            start_game(message)
        elif message.command == "end":
            end_game(message)
        else:
            if message.command:
                help(message, True)

"""
Trivia Games Bot 
"""
"""
Main Function
"""
"""
Name    : Top Up Group
CMD     : #tpgroup [space] group_name [space] credit_groups
ACCESS  : AGENT
"""
def top_up_group(message):
    wa_ph_number    = message.who.split("@")[0]
    params          = message.predicate.split(" ")
    wa_group_name   = ' '.join(params[:-1])
    credit_groups   = params[-1]
    if wa_group_name and credit_groups:
        payload = { "wa_group_name": wa_group_name, "wa_ph_number": wa_ph_number, 'credit_groups': credit_groups }
        top_up_group_post = requests.post(API_TOP_UP_GROUP, data=payload )
        top_up_group_data = top_up_group_post.json()

        if 'error' in top_up_group_data:
            top_up_group_data['error']['response']
            print(top_up_group_data['error']['response'])
            return 

"""
Name    : Create Group
CMD     : #ctgroup [space] group_name [space] credit_group
ACCESS  : AGENT
"""
def create_group(message):
    wa_ph_number    = message.who.split("@")[0]
    params          = message.predicate.split(" ")
    wa_group_name   = ' '.join(params[:-1])
    credit_groups   = params[-1]
    if not wa_group_name:
        mac.send_message(helper.INVALID_MESSAGE, message.conversation)
        return
    if not credit_groups :
        credit_groups = null

    payload = { "wa_group_name": wa_group_name, "wa_ph_number": wa_ph_number, 'credit_groups': credit_groups }
    create_group_post = requests.post(API_TOP_UP_GROUP, data=payload )
    create_group_data = create_group_post.json()

    if 'error' in create_group_data:
        mac.send_message(create_group_data['error']['response'], message.conversation)
        return

    if 'success' in create_group_data:
        mac.send_message(create_group_data['success']['response'], message.conversation)

    mac.create_group(wa_ph_number, wa_group_name, message.conversation, callback=update_group)


def update_group(groupId, group_name, ph_number, conversation):
    who = ph_number+'@s.whatsapp.net'
    payload = {'wa_group_id': groupId, 'wa_group_name': group_name, 'wa_ph_number': ph_number}
    group_update_post = requests.post(API_UPDATE_GROUP, data=payload)
    group_check_data = group_update_post.json()

"""
Name    : Create Session 
CMD     : #ctsessions [space] group_name [space] credit_member [space] duration (in day)
ACCESS  : AGENT
"""
def create_sessions(message):
    wa_ph_number    = message.who.split("@")[0]
    params          = message.predicate.split(" ")
    wa_group_name   = ' '.join(params[:-2])
    credit_member   = params[-2]
    duration        = params[-1]

    if not wa_group_name:
        mac.send_message(helper.INVALID_MESSAGE, message.conversation)
        return
    if not duration :
        duration = null

    payload = { "wa_group_name": wa_group_name, "wa_ph_number": wa_ph_number, 'credit_member': credit_member, 'day_duration' : duration }
    create_sessions_post = requests.post(API_CREATE_SESSIONS, data=payload )
    create_sessions_data = create_sessions_post.json()

    if 'error' in create_sessions_data:
        mac.send_message(create_sessions_data['error']['response'], message.conversation)
        return

    if 'success' in create_sessions_data:
        mac.send_message(create_sessions_data['success']['response'], message.conversation)
"""
Name    : Member Registration 
CMD     : #register
ACCESS  : Member
"""
def member_registration(message):
    wa_group_id     = message.conversation.split("@")[0]
    wa_ph_number    = message.who.split("@")[0]

    payload = { "wa_group_id": wa_group_id, "wa_ph_number": wa_ph_number}
    member_registration_post = requests.post(API_REGISTER_MEMBERS, data=payload )
    member_registration_data = member_registration_post.json()

    if 'error' in member_registration_data:
        mac.send_message(member_registration_data['error']['response'], message.who)
        return

    if 'success' in member_registration_data:
        mac.send_message(member_registration_data['success']['response'], message.conversation)

"""
Name    : Create Game
CMD     : #ctgame [space] group_name [space] rtp_game
ACCESS  : AGENT
"""
def create_game(message):
    wa_ph_number    = message.who.split("@")[0]
    params          = message.predicate.split(" ")
    wa_group_name   = ' '.join(params[:-1])
    rtp_game        = params[-1]
    print(wa_group_name)
    if not wa_group_name:
        mac.send_message(helper.INVALID_MESSAGE, message.conversation)
        return

    payload = { "wa_group_name": wa_group_name, "wa_ph_number": wa_ph_number, 'rtp_game': rtp_game }
    print(payload)
    create_game_post = requests.post(API_TOP_UP_GROUP, data=payload )
    create_game_data = create_game_post.json()
    #ask you must enter credit message

    #Todo success
    if 'error' in create_game_data:
        mac.send_message(create_group_data['error']['response'], message.conversation)
        return
"""
Name    : Start Game
CMD     : #start [space] group_name [space] duration (in minutes )
ACCESS  : AGENT
"""
def start_game(message):
    wa_ph_number    = message.who.split("@")[0]
    params          = message.predicate.split(" ")
    wa_group_name   = ' '.join(params[:-1])
    duration        = params[-1]
    print(wa_group_name)
    if not wa_group_name:
        mac.send_message(helper.INVALID_MESSAGE, message.conversation)
        return
    if not duration :
        duration = null

    payload = { "wa_group_name": wa_group_name, "wa_ph_number": wa_ph_number, 'minutes_duration': duration }
    print(payload)
    start_game_post = requests.post(API_START_GAME, data=payload )
    start_game_data = start_game_post.json()

    #Todo success
    if 'error' in start_game_data:
        mac.send_message(start_game_data['error']['response'], message.conversation)
        return

"""
Name    : User Place A Stake
CMD     : #stake [space] list_stakes_name [space] stake_amount
ACCESS  : AGENT
"""
def user_place_a_stake(message):
    wa_group_id     = message.conversation.split("@")[0]
    wa_ph_number    = message.who.split("@")[0]
    params          = message.predicate.split(" ")
    stake           = params[0]
    value           = params[1]
    if stake and value :
        payload = { "wa_group_id": wa_group_id, "wa_ph_number": wa_ph_number, 'stake': stake, 'value': value}
        user_place_a_stake_post = requests.post(API_STAKES, data=payload )
        user_place_a_stake_data = user_place_a_stake_post.json()

        #Todo success
        if 'error' in user_place_a_stake_data:
            mac.send_message(user_place_a_stake_data['error']['response'], message.conversation)
            return        

"""
Name    : Check All Stakes In Game
CMD     : #ckstakes
ACCESS  : ALL
"""
def check_all_stakes_in_game(message):
    wa_group_id     = message.conversation.split("@")[0]
    wa_ph_number    = message.who.split("@")[0]

    payload = { "wa_group_id": wa_group_id, "wa_ph_number" : wa_ph_number}
    check_all_stakes_in_game_post = requests.post(API_STAKES, data=payload )
    check_all_stakes_in_game_data = check_all_stakes_in_game_post.json()

    #Todo success
    if 'error' in check_all_stakes_in_game_data:
        mac.send_message(check_all_stakes_in_game_data['error']['response'], message.conversation)
        return        

"""
Name    : Check All List Stakes
CMD     : #ltstakes
ACCESS  : ALL
"""
def check_all_list_stakes(message):
    wa_group_id     = message.conversation.split("@")[0]
    wa_ph_number    = message.who.split("@")[0]

    payload = { "wa_group_id": wa_group_id, "wa_ph_number" : wa_ph_number}
    check_all_list_stakes_post = requests.post(API_LIST_STAKES, data=payload )
    check_all_list_stakes_data = check_all_list_stakes_post.json()

    #Todo success
    if 'error' in check_all_list_stakes_data:
        mac.send_message(check_all_list_stakes_data['error']['response'], message.conversation)
        return    

"""
Name    : End Game
CMD     : #end [space] group_name
ACCESS  : AGENT
"""
def end_game(message):
    wa_ph_number    = message.who.split("@")[0]
    wa_group_name   = message.predicate
    payload = { 'wa_group_name': wa_group_name, "wa_ph_number": wa_ph_number}
    end_game_post = requests.post(API_END_SESSIONS, data=payload )
    end_game_data = end_game_post.json()
    #error without having group

    #Todo success
    if 'error' in end_game_data:
        mac.send_message(end_game_data['error']['response'], message.conversation)
        return        

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
            mac.send_message(helper.HELP_MESSAGE_ROOM, message.conversation)
        else:
            mac.send_message("Here is some command I understand", message.who)
            mac.send_message(helper.HELP_MESSAGE, message.who)
    if isLost:
        mac.send_message("Hi, {} seems you getting lost".format(message.who_name), message.who)
    # check wether sender == conversation
    # if sender == conversation it means it's private chat
    if message.who == message.conversation:
        mac.send_message("Here is some command I understand", message.who)
        mac.send_message(helper.HELP_MESSAGE, message.conversation )
    else:
        group_id = message.conversation.split("@")[0]
        mac.get_group_info(message.conversation, message.who, callback=callback_check_group)

