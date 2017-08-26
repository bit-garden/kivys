from SocketBox import Socket_box

socket = Socket_box()

socket.allow_multi=True

def on_message(_ws, _data):
  if 'message' in _data:
    _data['username'] = socket.users[_ws]['username']
    socket.send_to_room(_ws, 'Lobby', _data, True)

socket.on_successfull_message=on_message
