from queue import Empty
import socket
import ast
from uuid import uuid4



host = "196.42.92.49" #this is the server ip address
port = 4455

""" Creating the UDP socket """
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

""" Bind the host address with the port """
server.bind((host, port))

Auth_Users = [] #[ [ip,name],[] ]

_GROUPS= [] # [(user_creator,group_name,people,group_id),()]

_GROUP_PEOPLE = [] # [(user_ID,group_id),()]

_GROUP_MESSAGES = [] # [(group_id,user_id,sender,txt),()]

_USERS = [] # this is without the user id
_USERS_DATA = [] #with the user id
_AUTH_TOKENS = [] #[ [user_id , token], [] ]
_tokens = []


#this method is a request for all the chats of the client
def SendChats(data,addr):
    # [(user_creator,group_name,people),()]
    client_groups = []
    for group in _GROUPS :
        people_ingroup = group[2] #this is a dictionary list
        #[{'name': 'memo', 'ip_address': '127.0.0.1'}, {'name': 'me', 'ip_address': '123.3453.223.2'}]
        for person in people_ingroup:
            #person is a dictionary
            if person['ip_address'] == data['sender']:
                client_groups.append(group)

    if client_groups is not Empty:
        #print(client_groups)
        #client_groups = client_groups.encode("utf-8")
        dat = {'data':client_groups}
        dat = str(dat)
        print(dat)
        #grp_str = listToString(client_groups)
        #dat.encode("utf-8")
        dat = bytes(dat, 'utf-8')
        server.sendto(dat,addr)
    else:
        string = "No Chats For You"
        print(string)

#this method just returns True :)
def validate_people(data):
    return True

#Store the data of groups in this method
def StoreGroupData(data,addr):
    # [(id,user_creator,group_name),()]

    _GROUPS.append((data['creator'],data['group_name'],data['people'],len(_GROUPS)))
    #last item is the group id
    print(_GROUPS)
    msg = "GROUP " + data['group_name'] + "CREATED "+ " SUCCESSFUL"
    print(msg +" for user "+data['creator'])
    msg  = msg.encode("utf-8")
    server.sendto(msg,addr)

#this method creates a group for us
def CreateGroup(data,addr):
    #data = {'group_name':name,'creator':host,'people':people}

    if validate_people(data['people']):
        StoreGroupData(data,addr)

#this method returns true if a user is registered
def userRegistered(user):
    global _USERS
    print(user)
    print(_USERS)

    for u in _USERS:
        if u['name']==user['name'] and u['password']==user['password']:
            return True
    return False
1
#this method is for getting a user if given its user object
def getUserId(user):
    global _USERS
    print(_USERS)
    for u in _USERS:
        if u['name']==user['name'] and u['password']==user['password']:
            return u['user_id']
    return "NO_ID"

#this method is to register a user in the app given its user object
def RegisterUser(user,user2,addr):


    if not userRegistered(user):#user not in _USERS:
        print(user)

        global _USERS
        user['user_id'] = len(_USERS)
        _USERS.append(user)

        print(_USERS)
        print(user)

        txt = 'You are now registered'
        txt = txt.encode("utf-8")
        server.sendto(txt, addr)
        print(user['name']+' - '+user['ip_address']  + ' is now registered')

    else:
        txt = 'You already have an account'
        txt = txt.encode("utf-8")
        server.sendto(txt, addr)
        print(user['name']+' - '+user['ip_address'] + ' is already registered')

#this method is to login a user in the app given its user object
def LoginUser(user,user2,addr):
    global _USERS
    if not userRegistered(user):#user not in _USERS:
        print(user)
        print(user['name']+' - '+user["ip_address"]+' login failed.')
        txt = 'LOGIN FAILED'
        txt = txt.encode("utf-8")
        server.sendto(txt, addr)

        print(_USERS)
        print(_USERS_DATA)
    else:
        print(user['name']+' - '+user["ip_address"]+' login successful.')
        token = str(uuid4())
        #if [user,token] in _AUTH_TOKENS:
        global _AUTH_TOKENS
        _AUTH_TOKENS.append([user,token])
        _tokens.append(token)
        #set(_AUTH_TOKENS)
        #list(_AUTH_TOKENS)
        txt = 'AUTH_KEY: ' + token   + '\n' + 'USER_ID: '+ str(getUserId(user))
        print(txt)
        txt = txt.encode("utf-8")
        server.sendto(txt, addr)

#this method is for UDP to send a request to server service for sending a message
def ClientSendsMessage(data,addr):
    #command = str({'type':'CHATS','sender':_USER[0],'data':''})
    pass
    dat = data['data']
    print(dat['user_id'])
    _GROUP_MESSAGES.append((dat['group_id'],dat['user_id'],dat['sender_name'],dat['txt']))
    #_GROUP_MESSAGES = [] # [(group_id,user_id,sender,txt),()]
    txt = 'MESSAGE SENT'
    txt = txt.encode("utf-8")
    server.sendto(txt, addr)

#this method is a UDP request for the clients messages
def ClientGetsMessage(data,addr):
    #_GROUP_MESSAGES = [] # [(group_id,user_id,sender_name,txt),()]
    messages = []
    global _GROUP_MESSAGES
    #_GROUP_MESSAGES.append((0,0,'thab','hi boys'))
    print('all group messages')
    print(_GROUP_MESSAGES)
    for m in _GROUP_MESSAGES:

        print(f'm[1] is {m[1]} and data[group_id] is  ')
        print(data['group_id'])
        if str(m[0]) == str(data['group_id']):
            print('found his message...')
            messages.append(m)

    if messages is Empty:
        print('no messages for group '+ data['group_id'])
        txt = "No Chats For Group"
        txt = txt.encode("utf-8")
        server.sendto(txt, addr)
        return
    print(messages)
    txt = str(messages)
    txt = txt.encode("utf-8")
    server.sendto(txt, addr)


if __name__ == "__main__":

    print("Server waiting for connection.")

    while True:
        data, addr = server.recvfrom(1024)
        data = data.decode("utf-8")
        data = ast.literal_eval(data)
        print('getting data...')
        if data['type'] == "REG":
            print('registering user ' + data['sender'])
            RegisterUser(data['data'],data['data'],addr)
            continue
        elif data['type'] == "LOGIN":
            print('loggin in user ' + data['sender'])
            LoginUser(data['data'],data['data'],addr)
            continue

        if data['token'] in _tokens:
            if data['type'] == "GROUP_CREATION":
                print('creating group for user ' + data['sender'])
                CreateGroup(data['data'],addr)
            elif data['type'] == "CHATS":
                print('getting chats for user ' + data['sender'])
                SendChats(data,addr)
            elif data['type'] == 'SEND_MESSAGE':
                print('sending message for user '+data['sender'])
                ClientSendsMessage(data,addr)
            elif data['type'] == 'GetMessages':
                print('getting messages for user '+data['sender'])
                ClientGetsMessage(data['data'],addr)
        else:
            print('-----------------------------------------security breach-----------------------------------------')

        if data == "!EXIT":
            print("Client disconnected.")
            break

