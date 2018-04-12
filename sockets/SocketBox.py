import ast

FILENAME_CHARS = 'abcdefghijklmnopqrstuvwxyz_.1234567890'
USERNAME_CHARS = 'abcdefghijklmnopqrstuvwxyz_'
LETTER_CHARS = 'abcdefghijklmnopqrstuvwxyz'
NUMBER_CHARS = '12334567890'

require_username = True

def check_string(_in, _allow_chars,
    can_be_empty = False):
  if not can_be_empty and len(_in) == 0:
    return False

  for i in _in.lower():
    if not i in _allow_chars:
      return False
      
  return True

class Socket_box:
  usernames = dict() #{username:[_ws,_ws]}
  users = dict() #{_ws:{'username':'some_name'}}
  rooms = {
    'Lobby': {'users': [],'usernames':[]}
  } #{'room_name':{'users':[_ws],'usernames':[]}};

  #allow multiple logins to the socketbox with the same username
  allow_multi=False

  char_limit = 512

  def on_successfull_message(self, _ws, _in):pass
  def on_successfull_disconnect(self, _ws):pass

  #when a message is received from the browser
  def on_message(self, _ws, _message):
    #valid flag for stable dictionary message
    valid = False
    if len(_message)<=self.char_limit:
      _in = dict()
      try:
        _in = ast.literal_eval(_message)
        valid = True
      except Exception:
        pass #no go, the message will be skipped.
    else:
      _ws.sendMessage(str({'from_host':True,'toast': 'The message is too long.'}))
      _ws.close()
      on_disconnect(_ws)
    
    if valid:
      #if login message {'login':true}
      if (_ws not in self.users and
          'login' in _in and
          'user' in _in and
          check_string(_in['user'], USERNAME_CHARS) and
          (_in['user'] not in self.usernames or self.allow_multi)):

        #add websocket with data about the user
        self.users[_ws] = {'username': _in['user'],'rooms':[]}
        
        #track multiple sign ins 
        if _in['user'] not in self.usernames:
          self.usernames[_in['user']]=[]
        self.usernames[_in['user']].append(_ws)

        #join the Lobby on by default
        self.join_room(_ws, 'Lobby')
        #send successfull response to client
        _ws.sendMessage(str({'logged': _in['user']}))

        #if more data is in the login message, pass this to the socketbox
        self.on_successfull_message(_ws, _in)
      elif _ws in self.users:
        #message after being connected. 
        self.on_successfull_message(_ws, _in)
      else:
        #if the login message isn't valid or breaks a rule for logging in
        _ws.sendMessage(str({'from_host':True,'toast': 'That is not a valid username'}))
        _ws.close()

  #used to clean up user list and handle disconnected users
  def on_disconnect(self, _ws):
    if _ws in self.users:
      #could be usefull for saving data when the user disconnects.
      self.on_successfull_disconnect(_ws)

      #leave all rooms
      for e in self.rooms:
        self.leave_room(_ws, e)

      #remove instance of socket from the usernames list
      self.usernames[self.users[_ws]['username']].remove(_ws)
        
      #clear username if empty
      if len(self.usernames[self.users[_ws]['username']])==0:
        del self.usernames[self.users[_ws]['username']]
      
      #delete instance of _ws from users list
      del self.users[_ws]

  #allows a broadcast message to other users in a room
  def send_to_room(self, _from, _to, _message, _include_self = False) :
    if _to in self.rooms:
      for e in self.rooms[_to]['users']:
        if _include_self or _from != e:
          e.sendMessage(str(_message))
          
  #sends a message to a user through the _ws instance
  def send_to(self, _to, _message):
    _to.sendMessage(str(_message))
  
  #sends message to all _ws instances for a specific username
  #usefull when the user has multiple clients signed in
  def send_to_username(self, _to, _message):
    if _to in self.usernames:
      for i in self.usernames[_to]:
        self.send_to(i,_message)

  #create a room for users
  def on_create_room(self, _ws, _name):pass
  def create_room(self, _ws, _name):
    if _name not in self.rooms:
      self.rooms[_name] = {'users': [], 'usernames':[]}
      self.on_create_room(_ws, _name)
      return True
    else:
      return False
      
  #destroy a room for users
  def on_destroy_room(self, _ws, _name):pass
  def destroy_room(self, _ws, _name):
    if _name in self.rooms:
      self.on_destroy_room(_ws, _name)
      for i in self.rooms[_name]['users']:
        self.leave_room(i,_name)
      del self.rooms[_name]
      return True
    else:
      return False


  #join room
  def on_join_room(self, _ws, _name):pass
  def join_room(self, _ws, _name):
    if (_name in self.rooms and 
       _ws not in self.rooms[_name]['users'] and 
       self.users[_ws]['username'] not in self.rooms[_name]['usernames']):
      self.rooms[_name]['users'].append(_ws)
      self.rooms[_name]['usernames'].append(self.users[_ws]['username'])
      self.users[_ws]['rooms'].append(_name)
      self.on_join_room(_ws, _name);
      return True
    else:
      return False

  #leave room
  def on_leave_room(self, _ws, _name):pass
  def leave_room(self,_ws, _name):
    if _ws in self.rooms[_name]['users']:
      self.on_leave_room(_ws, _name)
      self.rooms[_name]['users'].remove(_ws)
      self.rooms[_name]['usernames'].remove(self.users[_ws]['username'])
      self.users[_ws]['rooms'].remove(_name)
      return True
    else:
      return False
      
