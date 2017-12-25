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
API_TOP_UP_GROUP                = 'http://{}/api/top_up_group'.format(BASE_IP)
API_LIST_STAKES                 = 'http://{}/api/list_stakes'.format(BASE_IP)
API_END_SESSIONS                = 'http://{}/api/end_sessions'.format(BASE_IP)
API_HELP                        = 'http://{}/api/help'.format(BASE_IP)
API_AHELP                       = 'http://{}/api/ahelp'.format(BASE_IP)
API_CHECK_CREDIT_MEMBER         = 'http://{}/api/check_credit_member'.format(BASE_IP)   
API_GET_GROUP_INFO              = 'http://{}/api/get_group_from_private'.format(BASE_IP)  
API_CHECK_MASTER_AGENT_NUMBER   = 'http://{}/api/check_master_agent_number'.format(BASE_IP)


@signals.command_received.connect
def handle(message):
    print(message.command+" "+message.predicate)
    #Accept group command only
    if message.conversation != message.who :
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
        else:
            if message.command:
                check_master_agent(message)
    else:
        help(message)
"""
Trivia Games Bot  
"""
"""
Check Master Agent
"""
def check_master_agent(message):
    def get_info(result):
        master_agent_ph = result.subjectOwnerJid.split("@")[0]
        payload = {'wa_ph_number': master_agent_ph}
        check_master_agent_post = requests.post(API_CHECK_MASTER_AGENT_NUMBER, data=payload)
        check_master_agent_data = check_master_agent_post.json()

        if 'error' in check_master_agent_data:
            mac.send_message(check_master_agent_data['error']['response'], message.conversation)
            return

        if 'success' in check_master_agent_data:
            # Agent Commands
            if ( 'master_agent_ph_number' in check_master_agent_data['success']['response'] ):
                agent_cmd(message)
            return 

    mac.get_group_name(message.conversation, message.who, callback=get_info)

"""
Agent Commands 
"""
def agent_cmd(message) :
    if message.command == "tpagent":
        print(message.command)
    elif message.command == "credit":
        top_up_group(message)
    elif message.command == "group":
        create_group(message)
    elif message.command == "session":
        create_sessions(message)
    elif message.command == "game":
        create_game(message)
    elif message.command == "start":
        start_game(message)
    elif message.command == "end":
        end_game(message)
    elif message.command == "ahelp":
        ahelp(message)
    else:
        if message.command:
            help(message)
    return
"""
Main Function
"""
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
        top_up_group_post = requests.post(API_TOP_UP_GROUP, data=payload )
        top_up_group_data = top_up_group_post.json()

        if 'error' in top_up_group_data:
            mac.send_message(top_up_group_data['error']['response'], message.conversation)
            return

        if 'success' in top_up_group_data:
            mac.send_message(top_up_group_data['success']['response'], message.conversation)
            return 

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
    create_group_post = requests.post(API_CREATE_GROUP, data=payload )
    create_group_data = create_group_post.json()

    print(create_group_data)

    if 'error' in create_group_data:
        mac.send_message(create_group_data['error']['response'], message.who)
        return

    if 'success' in create_group_data:
        mac.send_message(create_group_data['success']['response'], message.who)

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
    create_sessions_post = requests.post(API_CREATE_SESSIONS, data=payload )
    create_sessions_data = create_sessions_post.json()

    print(create_sessions_data)
    if 'error' in create_sessions_data:
        mac.send_message(create_sessions_data['error']['response'], message.who)
        return

    if 'success' in create_sessions_data:
        mac.send_message(create_sessions_data['success']['response'], message.who)


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
    create_game_post = requests.post(API_CREATE_GAME, data=payload )
    create_game_data = create_game_post.json()

    print(create_game_data)
 
    if 'error' in create_game_data:
        mac.send_message(create_game_data['error']['response'], message.who)
        return

    if 'success' in create_game_data:
            mac.send_message(create_game_data['success']['response'], message.who)   


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
    start_game_post = requests.post(API_START_GAME, data=payload )
    start_game_data = start_game_post.json()

    print(start_game_data)
    if 'error' in start_game_data:
        mac.send_message(start_game_data['error']['response'], message.who)
        return

    if 'successgroup' in start_game_data:
            mac.send_message(start_game_data['successgroup']['response'], start_game_data['successgroup']['value']+"@g.us")   

    if 'successprivate' in start_game_data:
        mac.send_message(start_game_data['successprivate']['response'], message.who)
        return     
"""
Name    : Member Registration 
CMD     : #reg
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

    if 'successgroup' in member_registration_data:
            mac.send_message(member_registration_data['successgroup']['response'], message.conversation)   

    if 'successprivate' in member_registration_data:
        mac.send_message(member_registration_data['successprivate']['response'], message.who)
        return  
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
        user_place_a_stake_post = requests.post(API_STAKES, data=payload )
        user_place_a_stake_data = user_place_a_stake_post.json()

        if 'error' in user_place_a_stake_data:
            mac.send_message(user_place_a_stake_data['error']['response'], message.who)
            return    

        if 'successgroup' in user_place_a_stake_data:
            mac.send_message(user_place_a_stake_data['successgroup']['response'], message.conversation)   

        if 'successprivate' in user_place_a_stake_data:
            mac.send_message(user_place_a_stake_data['successprivate']['response'], message.who)
            return        

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
        mac.send_message(check_credit_member_data['error']['response'], message.conversation)
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
    

"""
Name    : Help
CMD     : #help
ACCESS  : GROUP
"""
def help(message):
    wa_group_id     = message.conversation.split("@")[0]

    payload = { "wa_group_id": wa_group_id }
    help_post = requests.post(API_HELP, data=payload )
    help_data = help_post.json()

    if 'error' in help_data:
        mac.send_message(help_data['error']['response'], message.conversation)
        return        

    if 'success' in help_data:
        mac.send_message(help_data['success']['response'], message.conversation)
        return   

"""
Name    : Agent Help
CMD     : #ahelp
ACCESS  : AGENT
"""
def ahelp(message):
    wa_ph_number    = message.who.split("@")[0]

    payload = { "wa_ph_number" : wa_ph_number}
    ahelp_post = requests.post(API_AHELP, data=payload )
    ahelp_data = ahelp_post.json()

    if 'error' in ahelp_data:
        mac.send_message(ahelp_data['error']['response'], message.conversation)
        return        

    if 'success' in ahelp_data:
        mac.send_message(ahelp_data['success']['response'], message.conversation)
        return   



"""
Helper and other command
"""
def end_api_thread(message,wa_group_name,wa_ph_number):
    time.sleep(10)
    payload = { 'wa_group_name': wa_group_name, "wa_ph_number": wa_ph_number}
    end_game_post = requests.post(API_END_GAME, data=payload )
    end_game_data = end_game_post.json()

    if 'error' in end_game_data:
        mac.send_message(end_game_data['error']['response'], message.conversation)
        return        

    if 'success' in end_game_data:
        player_lists = end_game_data['success']['response']
        wa_group_id = end_game_data['success']['value']+"@g.us"
        mac.send_message("Game is finish.", wa_group_id)
        mac.send_message("Here's the list of winner: ",wa_group_id)
        print(player_lists)
        #if 'phone_number' in player_lists:
        player_stakes_rows= [["phone_number", "stakes", "profit"]]
        for player in player_lists:
            player_stakes_rows.append([player["phone_number"], player["name_list_stakes"], player["profit"]])
            winner_stake_img = player["command_list_stakes"]
        table = texttable.Texttable()
        table.add_rows(player_stakes_rows)
        mac.send_message(table.draw(), wa_group_id)

        try:
            send_image(wa_group_id,winner_stake_img)
        except NameError:
            print('Not found')
        return 

def send_image(wa_group_id,animal):
    if animal != "":
        script_dir = sys.path[0]
        img_file = os.path.join(script_dir, 'modules/trivia/img/{}.png'.format(animal))
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

