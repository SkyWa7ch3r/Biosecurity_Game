import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
import time
import os, sys

'''
Authors
Martin Porebski
Joel Dunstan
Trae Shaw
'''

rooms = {}
profanity_list = []
profanity = open("Profanity/Profanity.txt", "r")
for words in profanity:
    word = words.replace("\n","")
    profanity_list.append(word)
print("Filter Loaded")

#list retrieved from http://stackoverflow.com/questions/3531746/what-s-a-good-python-profanity-filter-library
# code partially sourced from, we based the rest of the code based upon this link http://www.remwebdevelopment.com/blog/python/simple-websocket-server-in-python-144.html

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    loader = tornado.template.Loader(".")
    self.write(loader.load("index.html").generate())

class WSHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True
    
    def open(self):
        print ('connection opened...')
        self.write_message("Connection established, you may begin chatting!")
        self.write_message("If you have been made uncomfortable by other participants at any time, this will not be tolerated, please contact your coordinator immediately.")


    def on_message(self, message):

        msg = message.split(';;_;;')

        # check if it's a new connection
        if msg[0] == 'newconnection':

            # check if the room already exists
            if msg[1] in rooms.keys():
                print ('room already exists')

                #check if client is already in that room
                if msg[2] not in rooms[msg[1]]:
                    rooms[msg[1]].append(self)
                    print('new client connected')

            # else create a new chat room
            else:
                rooms[msg[1]] = list([self])
                print ('New chat room created: ', msg[1])
                #Create a new file to store the chat room and add the messages
                thetime = time.strftime("%d_%m_%Y")
                #The file name will be sessionid_groupnumber_LOCALDATE
                name = msg[1] + "_" + str(thetime)
                #Check if Chat exists, create it if it doesn't exist
                if not os.path.exists("../Chats/"):
                    os.makedirs("../Chats/")
                #The Chats are stored in a 'Chats' Directory
                try :
                    #Try writing the file
                    file = open("../Chats/" + name + ".txt", "a+")
                    file.write("Created chat room: "+ name + "_" + time.strftime("%H:%M:%S") + "\n")
                    file.close()
                    print("Chat file created for chat room" + name)
                except OSError as e:
                    #If it cant find the Chats Directory, make it and leave a warning inside the file.
                    if e.errono == errno.EEXIST:
                        os.makedirs("../Chats/")
                        file = open("../Chats/" + name + ".txt", "a+")
                        file.write("WARNING: YOU MAY HAVE LOST PREVIOUS CHAT DATA" + "\n")
                        file.write("THIS WARNING COMES UP IN THE EVENT IT CAN'T FIND THE CHAT DIRECTORY, WHILE TRYING TO WRITE ITS POSSIBLE CHATS WAS DELETED" + "\n")
                        file.write("Created chat room: "+ name + "_" + time.strftime("%H:%M:%S"))
                        file.close()

        # a message coming through
        elif msg[0] == 'sending':
            print ('received:', message)
            # get the clients in the room
            clients = rooms[msg[1]]
            if clients == None:
                print ('Error!')
            else:
                #Store the Latest Message, profanity or not, initialize name and the time
                thetime = time.strftime("%d_%m_%Y")
                name = msg[1] + "_" + str(thetime)
                #Check the message for profanity and display a warning so a user can let the coordinator know of the warning.
                if any(word in msg[3].lower() for word in profanity_list):
                    try:
                            file = open("../Chats/" + name + ".txt", "a")
                            file.write("\n" + msg[2] + ': ' + msg[3] + ' at ' + time.strftime("%H:%M:%S"))
                            file.close()
                    except OSError as e:
                        #If it cant find the file, make it and leave a warning inside the file.
                        if e.errono == e.EEXIST:
                            os.makedirs("../Chats/"+name+".txt")
                            file = open("../Chats/" + name + ".txt", "a+")
                            file.write("WARNING: YOU MAY HAVE LOST PREVIOUS CHAT DATA" + "\n")
                            file.write("THIS WARNING COMES UP IN THE EVENT IT CAN'T FIND THE CHAT DIRECTORY, WHILE TRYING TO WRITE ITS POSSIBLE CHATS WAS DELETED" + "\n")
                            file.write("Created chat room: "+ name + "_" + time.strftime("%H:%M:%S") + "\n")
                            file.write("\n" + msg[2] + ': ' + msg[3] + ' at ' + time.strftime("%H:%M:%S"))
                            file.close()
                    for p in clients:
                        p.write_message("Please keep this conversation civil and about the game, if you are seeing this message, please let the coordinator know")
                else:
                    try:
                        file = open("../Chats/" + name + ".txt", "a")
                        file.write("\n" + msg[2] + ': ' + msg[3] + ' at ' + time.strftime("%H:%M:%S"))
                        file.close()
                    except OSError as e:
                        #If it cant find the file, make it and leave a warning inside the file.
                        if e.errono == e.EEXIST:
                            os.makedirs("../Chats/"+name+".txt")
                            file = open("../Chats/" + name + ".txt", "a+")
                            file.write("WARNING: YOU MAY HAVE LOST PREVIOUS CHAT DATA" + "\n")
                            file.write("THIS WARNING COMES UP IN THE EVENT IT CAN'T FIND THE CHAT DIRECTORY, WHILE TRYING TO WRITE ITS POSSIBLE CHATS WAS DELETED" + "\n")
                            file.write("Created chat room: "+ name + "_" + time.strftime("%H:%M:%S") + "\n")
                            file.write("\n" + msg[2] + ': ' + msg[3] + ' at ' + time.strftime("%H:%M:%S"))
                            file.close()
                    # send the message to everyone in that room
                    for p in clients:
                        send_msg = msg[2]+';;_;;'+msg[3]
                        p.write_message(send_msg)
                

    def on_close(self):
        print ('Connection closed...')
        for key in rooms:
            # remove the client that has disconnected
            for index in range(0,len(rooms[key])):
                if rooms[key][index] == self:
                    rooms[key].pop(index)
                    print ('Removed client')

            # remove the room if there is no more players there
            if len(rooms[key]) == 0:
                print ('Removed an unused room')
                rooms.pop(key, None)
                break


application = tornado.web.Application([
  (r'/ws', WSHandler),
  (r'/', MainHandler),
  (r"/(.*)", tornado.web.StaticFileHandler, {"path": "./resources"}),
])

if __name__ == "__main__":
  application.listen(8000)
  tornado.ioloop.IOLoop.instance().start()

