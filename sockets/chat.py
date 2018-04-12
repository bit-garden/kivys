from SocketBox import *

socket = Socket_box()

socket.rooms['Lobby']['game']='none'
socket.rooms['Lobby']['destroy_on_lost_host']=False
socket.rooms['Lobby']['description']='''{'name':'Lobby'}'''

games={'none':[]} # {'game':[ws,ws]}

def on_message(_ws, _data):
  if 'from_host' in _data:
    del _data['from_host']

  if set(('login','game')) <= _data.keys():
    if _data['game'] in games:
      games[_data['game']].append(_ws)
      socket.users[_ws]['game']=_data['game']
    if check_string(_data['game'],FILENAME_CHARS):
      games[_data['game']]=[_ws]
      socket.users[_ws]['game']=_data['game']
      
  elif 'login' in _data:
    games['none'].append(_ws)
    socket.users[_ws]['game']='none'
  
  #just broadcast chat messages to the room the player is in
  if 'message' in _data or 'event' in _data:
    _data['username']=socket.users[_ws]['username']
    if (_data['username'] == socket.rooms[socket.users[_ws]['rooms'][0]]['usernames'][0] and
        'event' in _data):
      _data['from_host']=True
    if 'to' in _data and _data['to'] in socket.usernames:
      socket.send_to_username(_data['to'],_data)
    else:
      socket.send_to_room(_ws, socket.users[_ws]['rooms'][0], _data, False)
    
  if 'action' in _data:
    if _data['action']=='join':
      last_room = socket.users[_ws]['rooms'][0]
      was_host = socket.rooms[last_room]['users'][0]==_ws
      if 'room' in _data and check_string(_data['room'],FILENAME_CHARS):
      
        #if the room doesnt exist, make it, else it does, then just join
        if (_data['room'] not in socket.rooms and socket.create_room(_ws, _data['room']) or 
             _data['room'] in socket.rooms and _data['room'] not in socket.users[_ws]['rooms'] and socket.rooms[_data['room']]['game']==socket.users[_ws]['game']):
          socket.leave_room(_ws,last_room)
          socket.join_room(_ws,_data['room'])
          
          if socket.rooms[_data['room']]['users']==[_ws] and _data['room'] != 'Lobby':
            socket.rooms[_data['room']]['game']=socket.users[_ws]['game']
            socket.rooms[_data['room']]['destroy_on_lost_host']=False
            for _ in games[socket.users[_ws]['game']]:
              _.sendMessage(str({'new_room': _data['room']}))
          socket.send_to_room(_ws, _data['room'], {'room':_data['room'],
                                                    'event':'joined',
                                                    'from_host':True,
                                                    'user':socket.users[_ws]['username'],
                                                    'host':socket.rooms[_data['room']]['usernames'][0]}, True)
          
          #remove old rooms if noone is in them EXCEPT for Lobby
          if last_room!='Lobby' and len(socket.rooms[last_room]['users'])==0:
            socket.destroy_room(_ws,last_room)
          elif last_room!='Lobby' and was_host and not socket.rooms[last_room]['destroy_on_lost_host']:
            socket.send_to_room(_ws, last_room, {'event':'new_host','from_host':True,
                                                  'host':socket.users[socket.rooms[last_room]['users'][0]]['username']}, False)
          elif last_room!='Lobby' and was_host and socket.rooms[last_room]['destroy_on_lost_host']:
            for _ in socket.rooms[last_room]['users']:
              socket.join_room(_,'Lobby')
            socket.destroy_room(_ws,last_room)
          
    
    if _data['action'] == 'room_list' and 'game' in _data:
      room_list = [[_,socket.rooms[_]['description']] for _ in socket.rooms if socket.rooms[_]['game'] == _data['game']]
      _ws.sendMessage(str({'room_list': room_list}))
      
    
    if _data['action'] == 'data' and 'response' in _data:
      if _data['response'] in socket.usernames:
        _data['get']=False
        _data['user']=socket.users[_ws]['username']
        _data['room']=socket.users[_ws]['rooms'][0]
        print(_data)
        print(socket.usernames)
        #socket.usernames[_data['response']][0].sendMessage(str(_data))
        socket.send_to_username(_data['response'], _data)
        
    if (_data['action']=='set_host_lost' and 'val' in _data and 
         _ws == socket.rooms[socket.users[_ws]['rooms'][0]]['users'][0] and
         socket.users[_ws]['rooms'][0]!='Lobby'):
      socket.rooms[socket.users[_ws]['rooms'][0]]['destroy_on_lost_host']=_data['val']

    
    if (_data['action']=='set_description' and 'val' in _data and 
         _ws == socket.rooms[socket.users[_ws]['rooms'][0]]['users'][0] and
         socket.users[_ws]['rooms'][0]!='Lobby'):
      socket.rooms[socket.users[_ws]['rooms'][0]]['description']=_data['val']
      for _ in games[socket.users[_ws]['game']]:
        _.sendMessage(str({'new_desc': [socket.users[_ws]['rooms'][0],_data['val']]}))
    

socket.on_successfull_message=on_message


#clean up game reference
def on_disconnect(_ws):
  on_message(_ws,{'action':'join', 'room':'Lobby'})
  games[socket.users[_ws]['game']].remove(_ws)
  if socket.users[_ws]['game']!='none' and len(games[socket.users[_ws]['game']])==0:
    del games[socket.users[_ws]['game']]

socket.on_successfull_disconnect=on_disconnect

def on_leave(_ws, _name):
  if _name!='Lobby':
    socket.send_to_room(_ws, _name, {'from_host':True,'room':_name, 'event':'left','user':socket.users[_ws]['username']}, True)
  
socket.on_leave_room=on_leave



