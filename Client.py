from operator import mul
from queue import Empty
import socket
import json
import ast

host = "196.42.92.49"


port = 4455
addr = (host, port)
_AUTH_KEY = ''
_CHATS = []
_USER = '' #(ip address,name)
_USER_DETAILS = '' # user_id

#message = {'sender':_USER[0],'reciever':host,'txt':'','type':''}

""" Creating the UDP socket """
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#this is for a group request
def group_request(name,people):
    global host
    data = {'group_name':name,'creator':host,'people':people}
    group_name = data['group_name']
    command = str({'type':'GROUP_CREATION','token':_AUTH_KEY,'sender':host,'data':data})
    command  = command.encode("utf-8")
    global addr
    client.sendto(command, addr)
    print(name + ' group is being created...')
    #Wait for response from server
    print('Waiting for response from server')
    while True:

        data, addr = client.recvfrom(1024)
        data = data.decode("utf-8")
        #data = ast.literal_eval(data)
        #print(data)

        msg = "GROUP " + group_name + " CREATED "+ " SUCCESSFUL"
        if data == msg:
            print("Group Created Successfully.")
            START_APP()
            break
        else:
            #print("Group not created.")
            START_APP()

#this is for showing chat messages
def showChatMessages(group_id):
    things = {'group_id':group_id}
    data  = str({'type':'GetMessages','token':_AUTH_KEY,'sender':_USER[0],'data':things})
    data = data.encode("utf-8")
    global addr
    client.sendto(data, addr)


    while True:
        data, addr = client.recvfrom(1024)
        data = data.decode("utf-8")
        if data is not Empty:
            #print(data)
            data = ast.literal_eval(data)
            for msg in data:
                #print(msg)
                print(msg[2][1] + ": " + msg[3]+' (##)')  #printing message here
            break

#this allows a client to send a message request
def sendMessage(txt,group_id):
    global _USER_DETAILS
    global _USER
    data = {'user_id':_USER_DETAILS[0],'group_id':group_id,'sender_name':_USER,'txt':txt}
    command = str({'type':'SEND_MESSAGE','token':_AUTH_KEY,'sender':_USER[0],'data':data})
    command  = command.encode("utf-8")
    global addr
    print('Sending message...')
    print(_USER_DETAILS[0])
    client.sendto(command, addr)


    while True:

        data, addr = client.recvfrom(1024)
        data = data.decode("utf-8")

        if data == 'MESSAGE SENT':
            print(data)
            ShowChats()
            break



#this is for chat activity for client
def ChatActivity(command):
    print("Print 1 to send message , 0 to go back and -1 to go to main")
    command2 = int(input('Command : '))
    if command2 == -1:
        START_APP()
    elif command2 == 0 :
        ShowChats()
    elif command2 == 1:
        txt = str(input('Type a message: '))
        sendMessage(txt,command-1)

#this is for showing chats to user
def ShowChats():

    print('Choose a number to pick a chat.\nOr write 0 to go back.\n')

    global _CHATS
    index = 1
    for chat in _CHATS:
        print(str(index) +'. '+chat[1] + ' (created by : '+chat[2][0]['ip_address']+').')
        index+=1

    command = int(input('Command : '))

    if command == 0:
        START_APP()
    elif isinstance(command,int):
        pass
        print('-------------------------------------------------------------------------------')
        print('----------------------------------------CHATS---------------------------------')
        print('')
        if _CHATS is not Empty:
            #print(_CHATS[command -1])
            showChatMessages(_CHATS[command-1][3])
        else:
            print('NO CHATS.')
        print('----------------------------------------------')
        ChatActivity(command)

#this is for main menu
def START_APP():
    print('-------------------------------------------------------------------')
    print("------------------------Menu------------------------------\n1.Chats\n2.Create Group\n3.Exit")
    command = str(input("Select a number from the menu: "))

    if command == '2':
        name = str(input("Name of group: "))
        global host
        people = [{'name':_USER[1],'ip_address':_USER[0]},]
        person = str(input("Enter person name or EXIT: "))

        while person != 'EXIT':

            person_ip = str(input("Enter person ip: "))
            people.append({'name':person,'ip_address':person_ip})
            person = str(input("Enter person name or EXIT: "))
        group_request(name,people)

    elif command == '3':
        quit()

    elif command == '1':
        print("----------------CHATS---------------------")
        #global host
        command = str({'type':'CHATS','token':_AUTH_KEY,'sender':_USER[0],'data':''})
        command  = command.encode("utf-8")
        global addr
        client.sendto(command, addr)

        while True:
            #global client
            data, addr = client.recvfrom(1024)
            data = data.decode("utf-8")

            if data == "No Chats For You":
                print('No Chats')
                START_APP()
                break
            data = ast.literal_eval(data)
            global _CHATS
            _CHATS = data['data']

            if data['data'] is Empty or data['data'] is not Empty:
                #print('data is not empty')
                ShowChats()
                break
        #
    print('-------------------------------------------------------------------')

#this is for handling register requests to client
def RegisterUser():
    name = str(input('Enter your name:'))
    password = str(input('Enter your password :'))
    password2 = str(input('confirm password:'))

    if password2 != password:
        print('passwords are not the same')
        password = str(input('Enter your name:'))
        password2 = str(input('Enter your name:'))
    else:

        hostname = socket.gethostname()
        ## getting the IP address using socket.gethostbyname() method
        ip_address = socket.gethostbyname(hostname)

        user = {'name':name,'password':password,'ip_address':ip_address}
        command = str({'type':'REG','token':_AUTH_KEY,'sender':ip_address,'data':user})
        command  = command.encode("utf-8")
        global addr
        client.sendto(command, addr)


        #Wait for response from server
        while True:
            print('Waiting for response from server')
            data, addr = client.recvfrom(1024)
            data = data.decode("utf-8")
            if data == "You are now registered":
                print("You are now registered")
                LoginUser()
                break
            elif data == "You already have an account":
                print("You already have an account")
                LoginUser()
                break

#this is for handling login requests to client
def LoginUser():
    name =  str(input('Enter your name:'))
    password = str(input('Enter your password :'))


    hostname = socket.gethostname()
    ## getting the IP address using socket.gethostbyname() method
    ip_address = socket.gethostbyname(hostname)
    global _AUTH_KEY
    user = {'name':name,'password':password,'ip_address':ip_address}
    command = str({'type':'LOGIN','token':_AUTH_KEY,'sender':ip_address,'data':user})
    command  = command.encode("utf-8")
    global addr
    client.sendto(command, addr)

    #Waiting for response
    while True:
        print('Waiting for response from server')
        data, addr = client.recvfrom(1024)
        data = data.decode("utf-8")
        if "AUTH_KEY:" in data:
            print("You are now logged in")
            #print(data)

            multi = data.splitlines()


            _AUTH_KEY = multi[0][10:]
            global _USER_DETAILS
            _USER_DETAILS = (multi[1][9:])
            #print(_AUTH_KEY)
            global _USER
            _USER = (ip_address,name)
            START_APP()
            break
        elif data == "LOGIN FAILED":
            print("Login failed")
            break

#this is for starting the app
def Start():
    print('Welcome to UDP Chat \n')
    command = input("Enter LOGIN to login,\nREG to register\n")
    if command == 'AUTH':
        pass
        #AuthUser()
    elif command == "REG":
        RegisterUser()
    elif command =="LOGIN":
        LoginUser()

if __name__ == "__main__":
    Start()


