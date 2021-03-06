from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from SocketBox import Socket_box
#ws://ansible-ansible.a3c1.starter-us-west-1.openshiftapps.com/chat

import chat

echo_box = Socket_box()
echo_box.on_successfull_message=lambda ws,data:echo_box.send_to(ws,data)




boxes={'/chat':chat}


class SimpleEcho(WebSocket):

    def handleMessage(self):
        # echo message back to client
        if self.request.path in boxes:
          boxes[self.request.path].socket.on_message(self,self.data)
        else:
          self.close()

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')
        #chat_box.on_disconnect(self)
        if self.request.path in boxes:
          boxes[self.request.path].socket.on_disconnect(self)
        else:
          self.close()



#import os
#port = os.environ['PORT']

server = SimpleWebSocketServer('', int(8080), SimpleEcho)
server.serveforever()