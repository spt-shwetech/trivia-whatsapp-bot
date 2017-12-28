from app.mac import mac, signals
from modules.trivia import helper
import requests
import texttable
import re
import sys, os
from datetime import datetime
import time, threading

BASE_IP = 'trivia.shweapi.com'
#BASE_IP = 'localhost/trivia'
ANIMALS = ['rat', 'ox', 'tiger', 'rabbit', 'dragon', 'snake', 'horse', 'goat', 'monkey', 'rooster', 'dog', 'pig']
#ANIMALS = ['ji','gou','zhu','shu','niu','hu','tu','long','she','ma','yang','hou']
ALLANIMALS = set(ANIMALS)
TEMP = {}

#List API TRIVIA
API_TOP_UP_GROUP                = 'http://{}/api/top_up_group'.format(BASE_IP)
API_CREATE_GROUP                = 'http://{}/api/create_group'.format(BASE_IP)
API_UPDATE_GROUP                = 'http://{}/api/update_group'.format(BASE_IP)
API_CREATE_SESSIONS             = 'http://{}/api/create_sessions'.format(BASE_IP)
API_REGISTER_MEMBERS            = 'http://{}/api/register_members'.format(BASE_IP)
API_CREATE_GAME                 = 'http://{}/api/create_game'.format(BASE_IP)
API_START_GAME                  = 'http://{}/api/start_game'.format(BASE_IP)
API_END_GAME                    = 'http://{}/api/end_game'.format(BASE_IP)
API_STAKES                      = 'http://{}/api/stakes'.format(BASE_IP)
API_CHECK_STAKES_MEMBERS        = 'http://{}/api/check_stakes_members'.format(BASE_IP)
API_TOP_UP_AGENT                = 'http://{}/api/top_up_agent'.format(BASE_IP)
API_TOP_UP_MEMBER               = 'http://{}/api/top_up_member'.format(BASE_IP)
API_TOP_UP_GROUP                = 'http://{}/api/top_up_group'.format(BASE_IP)
API_LIST_STAKES                 = 'http://{}/api/list_stakes'.format(BASE_IP)
API_END_SESSIONS                = 'http://{}/api/end_sessions'.format(BASE_IP)
API_HELP                        = 'http://{}/api/help'.format(BASE_IP)
API_AHELP                       = 'http://{}/api/ahelp'.format(BASE_IP)
API_MAHELP                      = 'http://{}/api/mahelp'.format(BASE_IP)
API_CHECK_CREDIT_MEMBER         = 'http://{}/api/check_credit_member'.format(BASE_IP)   
API_GET_GROUP_INFO              = 'http://{}/api/get_group_from_private'.format(BASE_IP)  
API_CHECK_MASTER_AGENT_NUMBER   = 'http://{}/api/check_master_agent_number'.format(BASE_IP)
API_MA_BAL                      = 'http://{}/api/check_credit_master_agent'.format(BASE_IP)
API_A_BAL                       = 'http://{}/api/check_credit_agent'.format(BASE_IP)


@signals.command_received.connect
def handle(message):
    print(message.command+" "+message.predicate)

    #Both Command
    if message.command == "mahelp":
        ma_help(message)
        return
    if message.command == "mabal":
        ma_bal(message)
        return
    if message.command == "tpagent":
        top_up_agent(message)
        return
    #Accept group command only
    if message.conversation != message.who :
        print("group")
        if message.command == "list":
            check_all_stakes_in_game(message)
        elif message.command == "listbet":
            check_all_list_stakes(message)
        elif message.command == "reg":
            member_registration(message)
        elif message.command == "b":
            user_place_a_stake(message)
        elif message.command == "help":
            help(message)
        elif message.command == "bal":
            check_credit_member(message)
        elif message.command == "tpmember":
            top_up_member(message)
        elif message.command == "image":
            send_image("959403093452-1514460953@g.us","do")
        else:
            if message.command:
                check_master_agent(message)
    else:
        if message.command:
            help(message)
"""
Trivia Games Bot  
"""
"""
Agent Commands 
"""
def agent_cmd(message) :
    if message.command == "group":
            create_group(message)
    elif message.command == "credit":
        top_up_group(message)
    elif message.command == "session":
        create_sessions(message)
    elif message.command == "game":
        create_game(message)
    elif message.command == "start":
        start_game(message)
    elif message.command == "end":
        end_game(message)
    elif message.command == "autorun":
        autorun(message)
    elif message.command == "ahelp":
        a_help(message)
    elif message.command == "abal":
        a_bal(message)   
    else:
        if message.command:
            help(message)
    return

"""
Main Function
"""
"""
Name    : Top Up Agent
CMD     : #tpagent [space] wa_ph_number_agent [space] credit_top_up
ACCESS  : AGENT
"""
def top_up_agent(message):
    wa_ph_number_master_agent   = message.who.split("@")[0]
    params                      = message.predicate.split(" ")
    wa_ph_number_agent          = params[0]
    credit_top_up               = params[1]

    if wa_ph_number_agent and credit_top_up :
        payload = { "wa_ph_number_master_agent": wa_ph_number_master_agent, "wa_ph_number_agent": wa_ph_number_agent, 'credit_top_up': credit_top_up }
        _post = requests.post(API_TOP_UP_AGENT, data=payload )
        _data = _post.json()

        repsonse_handler(_data,message)

"""
Name    : Top Up Member
CMD     : #tpmember [space] member phone number [space] credit
ACCESS  : AGENT
"""
def top_up_member(message):
    wa_ph_number                = message.who.split("@")[0]
    params                      = message.predicate.split(" ")
    wa_member_ph_number         = params[0]
    credit_top_up               = params[1]

    if wa_member_ph_number and credit_top_up :
        payload = { "wa_ph_number": wa_ph_number, "wa_member_ph_number": wa_member_ph_number, 'credit_top_up': credit_top_up }
        _post = requests.post(API_TOP_UP_MEMBER, data=payload )
        _data = _post.json()

        repsonse_handler(_data,message)
        
"""
Name    : Top Up Group
CMD     : #credit [space] group_name [space] credit_groups
ACCESS  : AGENT
"""
def top_up_group(message):
    wa_ph_number    = message.who.split("@")[0]
    params          = message.predicate.split(" ")
    wa_group_name   = ' '.join(params[:-1])
    credit_groups   = params[-1]
    if wa_group_name and credit_groups:
        payload = { "wa_group_name": wa_group_name, "wa_ph_number": wa_ph_number, 'credit_groups': credit_groups }
        _post = requests.post(API_TOP_UP_GROUP, data=payload )
        _data = _post.json()

        repsonse_handler(_data,message)

"""
Name    : Create Group
CMD     : #group [space] group_name [space] credit_group
ACCESS  : AGENT
"""
def create_group(message):
    wa_ph_number    = message.who.split("@")[0]
    params          = message.predicate.split(" ")
    wa_group_name   = ' '.join(params[:-1])

    if not wa_group_name:
        wa_group_name   = params[0]
        credit_group = 'null'
    else :
        credit_group = params[-1]

    payload = { "wa_group_name": wa_group_name, "wa_ph_number": wa_ph_number, 'credit_group': credit_group }
    _post = requests.post(API_CREATE_GROUP, data=payload )
    _data = _post.json()

    repsonse_handler(_data,message)

    mac.create_group(wa_ph_number, wa_group_name, message.conversation, callback=update_group)


def update_group(groupId, group_name, ph_number, conversation):
    who = ph_number+'@s.whatsapp.net'
    payload = {'wa_group_id': groupId, 'wa_group_name': group_name, 'wa_ph_number': ph_number}
    group_update_post = requests.post(API_UPDATE_GROUP, data=payload)
    group_check_data = group_update_post.json()

"""
Name    : Create Session 
CMD     : #session [space] group_name [space] credit_member [space] duration (in day)
ACCESS  : AGENT
"""
def create_sessions(message):
    wa_ph_number    = message.who.split("@")[0]
    params          = message.predicate.split(" ")

    if len(params) < 3 :
        mac.send_message(helper.INVALID_MESSAGE, message.conversation)
        return

    wa_group_name   = ' '.join(params[:-2])
    credit_member   = params[-2]
    duration        = params[-1]

    if not wa_group_name:
        mac.send_message(helper.INVALID_MESSAGE, message.who)
        return

    if not duration :
        duration = "null"

    payload = { "wa_group_name": wa_group_name, "wa_ph_number": wa_ph_number, 'credit_member': credit_member, 'day_duration' : duration }
    _post = requests.post(API_CREATE_SESSIONS, data=payload )
    _data = _post.json()

    repsonse_handler(_data,message)


"""
Name    : Create Game
CMD     : #game [space] group_name
ACCESS  : AGENT
"""
def create_game(message):
    wa_ph_number    = message.who.split("@")[0]
    params          = message.predicate.split(" ")
    wa_group_name   = message.predicate

    if not wa_group_name:
        mac.send_message(helper.INVALID_MESSAGE, message.conversation)
        return

    payload = { "wa_group_name": wa_group_name, "wa_ph_number": wa_ph_number }
    _post = requests.post(API_CREATE_GAME, data=payload )
    _data = _post.json()

    repsonse_handler(_data,message)

"""
Name    : Start Game
CMD     : #start [space] group_name [space] duration (in minutes )
ACCESS  : AGENT
"""
def start_game(message):
    wa_ph_number    = message.who.split("@")[0]
    params          = message.predicate.split(" ")
    wa_group_name   = ' '.join(params[:-1])

    if not wa_group_name:
        wa_group_name   = params[0]
        duration = '10'
    else :
        duration = params[-1]

    payload = { "wa_group_name": wa_group_name, "wa_ph_number": wa_ph_number, 'minutes_duration': duration }
    print(payload)
    _post = requests.post(API_START_GAME, data=payload )
    _data = _post.json()

    repsonse_handler(_data,message)

"""
Name    : Member Registration 
CMD     : #reg
ACCESS  : Member
"""
def member_registration(message):
    wa_group_id     = message.conversation.split("@")[0]
    wa_ph_number    = message.who.split("@")[0]

    payload = { "wa_group_id": wa_group_id, "wa_ph_number": wa_ph_number}
    _post = requests.post(API_REGISTER_MEMBERS, data=payload )
    _data = _post.json()

    repsonse_handler(_data,message)

"""
Name    : User Place A Stake
CMD     : #b [space] list_stakes_name [space] stake_amount
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
        _post = requests.post(API_STAKES, data=payload )
        _data = _post.json()

        repsonse_handler(_data,message)  

"""
Name    : Check All Stakes In Game
CMD     : #list
ACCESS  : ALL
"""
def check_all_stakes_in_game(message):
    wa_group_id     = message.conversation.split("@")[0]
    wa_ph_number    = message.who.split("@")[0]

    payload = { "wa_group_id": wa_group_id, "wa_ph_number" : wa_ph_number}
    check_all_stakes_in_game_post = requests.post(API_CHECK_STAKES_MEMBERS, data=payload )
    check_all_stakes_in_game_data = check_all_stakes_in_game_post.json()

    if 'error' in check_all_stakes_in_game_data:
        mac.send_message(check_all_stakes_in_game_data['error']['response'], message.conversation)
        return        

    if 'success' in check_all_stakes_in_game_data:
        player_lists = check_all_stakes_in_game_data['success']['response']['check_stakes_members']
        player_stakes_rows= [["phone_number", "stakes", "value"]]
        for player in player_lists:
            player_stakes_rows.append([player["phone_number"], player["name_list_stakes"], player["value_stakes"]])
        table = texttable.Texttable()
        table.add_rows(player_stakes_rows)
        mac.send_message(table.draw(), message.conversation)
        return   

"""
Name    : Check All List Stakes
CMD     : #listbet
ACCESS  : ALL
"""
def check_all_list_stakes(message):
    wa_group_id     = message.conversation.split("@")[0]
    wa_ph_number    = message.who.split("@")[0]

    payload = { "wa_group_id": wa_group_id, "wa_ph_number" : wa_ph_number}
    check_all_list_stakes_post = requests.post(API_LIST_STAKES, data=payload )
    check_all_list_stakes_data = check_all_list_stakes_post.json()

    if 'error' in check_all_list_stakes_data:
        mac.send_message(check_all_list_stakes_data['error']['response'], message.conversation)
        return    

    if 'success' in check_all_list_stakes_data:
        player_lists = check_all_list_stakes_data['success']['response']
        player_stakes_rows= [["Command", "Name Stakes"]]
        for player in player_lists:
            player_stakes_rows.append([player["command_list_stakes"],player["name_list_stakes"]])
        table = texttable.Texttable()
        table.add_rows(player_stakes_rows)
        mac.send_message(table.draw(), message.conversation)
        return  

"""
Name    : Check All List Stakes
CMD     : #bal
ACCESS  : ALL
"""
def check_credit_member(message):
    wa_group_id     = message.conversation.split("@")[0]
    wa_ph_number    = message.who.split("@")[0]

    payload = { "wa_group_id": wa_group_id, "wa_ph_number" : wa_ph_number}
    check_credit_member_post = requests.post(API_CHECK_CREDIT_MEMBER, data=payload )
    check_credit_member_data = check_credit_member_post.json()

    if 'error' in check_credit_member_data:
        error_repsonse_handler(check_credit_member_data,message)
        return        

    if 'success' in check_credit_member_data:
        player_lists = check_credit_member_data['success']['response']
        check_credit_member_rows= [["Name Groups","Start Sessions","Credit Register","End Sessions"]]
        for player in player_lists:
            check_credit_member_rows.append([player["name_groups"],player["start_sessions"],str(player["credit_register_members"]),player["end_sessions"]])
        table = texttable.Texttable()
        table.add_rows(check_credit_member_rows)
        mac.send_message(table.draw(), message.who)
        return      
"""
Name    : End Game
CMD     : #end [space] group_name
ACCESS  : AGENT
"""
def end_game(message):
    wa_ph_number    = message.who.split("@")[0]
    wa_group_name   = message.predicate

    groupname_payload = { 'wa_group_name': wa_group_name, "wa_ph_number" : wa_ph_number }
    group_id_post = requests.post(API_GET_GROUP_INFO, data=groupname_payload )
    group_id_data = group_id_post.json()

    print(group_id_data)
    
    if 'success' not in group_id_data:
        return        

    mac.send_message("Game will End in 10 seconds", group_id_data['success']['response']['wa_group_id']+"@g.us")
    t = threading.Thread(target=end_api_thread, args=(message,wa_group_name,wa_ph_number,))
    t.start()
    
def autorun(message):
    #Todo
    # wa_group_id     = message.conversation.split("@")[0]
    wa_ph_number    = message.who.split("@")[0]
    wa_group_name   = message.predicate
    if wa_group_name != "":
        while True:
            #game 
            print("game cmd")
            payload = { "wa_group_name": wa_group_name, "wa_ph_number": wa_ph_number }
            create_game_post = requests.post(API_CREATE_GAME, data=payload )
            #time.sleep(0.5)
            #start
            print("start cmd")
            payload1 = { "wa_group_name": wa_group_name, "wa_ph_number": wa_ph_number, 'minutes_duration': 3 }
            start_game_post = requests.post(API_START_GAME, data=payload1 )
            start_game_data = start_game_post.json()

            # if 'successgroup' in start_game_data:
            #         mac.send_message(start_game_data['successgroup']['response'], start_game_data['successgroup']['value']+"@g.us")   
            time.sleep(180)
            #end
            print("end cmd")
            groupname_payload = { 'wa_group_name': wa_group_name, "wa_ph_number" : wa_ph_number }
            group_id_post = requests.post(API_GET_GROUP_INFO, data=groupname_payload )
            group_id_data = group_id_post.json()
            print(group_id_data)
            if 'success' not in group_id_data:
                return        

            mac.send_message("Game will End in 10 seconds", group_id_data['success']['response']['wa_group_id']+"@g.us")
            t = threading.Thread(target=end_api_thread, args=(message,wa_group_name,wa_ph_number,))
            t.start()

"""
Name    : Help
CMD     : #help
ACCESS  : GROUP
"""
def help(message):
    wa_group_id     = message.conversation.split("@")[0]

    payload = { "wa_group_id": wa_group_id }
    _post = requests.post(API_HELP, data=payload )
    _data = _post.json()

    repsonse_handler(_data,message)

"""
Name    : Agent Help
CMD     : #ahelp
ACCESS  : AGENT
"""
def a_help(message):
    wa_ph_number    = message.who.split("@")[0]

    payload = { "wa_ph_number" : wa_ph_number}
    _post = requests.post(API_AHELP, data=payload )
    _data = _post.json()

    repsonse_handler(_data,message)

"""
Name    : Agent bal
CMD     : #abal
ACCESS  : AGENT
"""
def a_bal(message):
    wa_ph_number    = message.who.split("@")[0]

    payload = { "wa_ph_number" : wa_ph_number}
    _post = requests.post(API_A_BAL, data=payload )
    _data = _post.json()

    repsonse_handler(_data,message)

"""
Name    : MA Help
CMD     : #mahelp
ACCESS  : AGENT
"""
def ma_help(message):
    wa_ph_number    = message.who.split("@")[0]

    payload = { "wa_ph_number" : wa_ph_number}
    _post = requests.post(API_MAHELP, data=payload )
    _data = _post.json()

    repsonse_handler(_data,message)

"""
Name    : MA bal
CMD     : #mabal
ACCESS  : MA
"""
def ma_bal(message):
    wa_ph_number    = message.who.split("@")[0]

    payload = { "wa_ph_number" : wa_ph_number}
    _post = requests.post(API_MA_BAL, data=payload )
    _data = _post.json()

    repsonse_handler(_data,message)


"""
Helper and other command
"""


def end_api_thread(message,wa_group_name,wa_ph_number):
    time.sleep(10)
    payload = { 'wa_group_name': wa_group_name, "wa_ph_number": wa_ph_number}
    end_game_post = requests.post(API_END_GAME, data=payload )
    end_game_data = end_game_post.json()

    print(end_game_data)

    if 'error' in end_game_data:
        mac.send_message(end_game_data['error']['response'], message.conversation)
        return        

    if 'success' in end_game_data:
        player_lists = end_game_data['success']['response']
        _wa_group_id = end_game_data['success']['value']+"@g.us"
        mac.send_message("Game is finish.", _wa_group_id)
        mac.send_message("Here's the list of winner: ",_wa_group_id)
        print(player_lists)
        #if 'phone_number' in player_lists:
        player_stakes_rows= [["phone_number", "stakes", "profit"]]
        for player in player_lists:
            player_stakes_rows.append([player["phone_number"], player["name_list_stakes"], player["profit"]])
            winner_stake_img = player["command_list_stakes"]
        table = texttable.Texttable()
        table.add_rows(player_stakes_rows)
        mac.send_message(table.draw(), _wa_group_id)

        try:
            send_image(_wa_group_id,winner_stake_img)
            # t = threading.Thread(target=send_image, args=(_wa_group_id,winner_stake_img,))
            # t.start()
        except NameError:
            print('Not found')
        return 

def send_image(wa_group_id,animal):
    if animal != "":
        print(animal)
        script_dir = sys.path[0]
        img_file = os.path.join(script_dir, 'modules/trivia/img/{}.png'.format(animal))
        print(img_file)
        print(wa_group_id)
        mac.send_image(img_file, wa_group_id) 
        

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

def error_repsonse_handler(data,message):
    if data['error']['target'] != 'private' : 
        mac.send_message(data['error']['response'], data['error']['value']+"@g.us")
        return
    else :
        mac.send_message(data['error']['response'], message.who)
        return

def success_repsonse_handler(data,message):
    if data['success']['target'] != 'private' : 
        mac.send_message(data['success']['response'], data['success']['value']+"@g.us")
        return
    else :
        mac.send_message(data['success']['response'], message.who)
        return

def repsonse_handler(data,message):
    print(data)

    if 'error' in data:
        error_repsonse_handler(data,message)
        return  

    if 'successgroup' in data:
        mac.send_message(data['successgroup']['response'], data['successgroup']['value']+"@g.us")   

    if 'successprivate' in data:
        mac.send_message(data['successprivate']['response'], message.conversation)

    if 'success' in data:
        success_repsonse_handler(data,message)
        return
    return   

"""
Check Master Agent
"""
def check_master_agent(message):

    wa_group_id     = message.conversation.split("@")[0]
    wa_ph_number    = message.who.split("@")[0]

    payload = { "wa_group_id": wa_group_id, "wa_ph_number": wa_ph_number}
    check_master_agent_post = requests.post(API_CHECK_MASTER_AGENT_NUMBER, data=payload)
    check_master_agent_data = check_master_agent_post.json()

    print(check_master_agent_data)
    if 'error' in check_master_agent_data:
        mac.send_message(check_master_agent_data['error']['response'], message.conversation)
        return

    if 'success' in check_master_agent_data:
        if 'master_agent_ph_number' in check_master_agent_data['success']['response'] :
            def get_info(result):
                wa_ph_master_number = str(check_master_agent_data['success']['response']['master_agent_ph_number'])+"@s.whatsapp.net"
                if wa_ph_master_number in result.participants:
                    # Agent Commands
                    agent_cmd(message)
                else:
                    mac.send_message('no master agent number phone in this group', message.conversation)

            mac.get_group_name(message.conversation, message.who, callback=get_info)  
            
        return 