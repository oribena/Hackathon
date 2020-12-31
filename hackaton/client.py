import socket
import time
import struct
import msvcrt
import string
import random
import _thread as thread

FORMAT = "32s 1s 40s 1s 256s 256s"
bufferSize = 1024

# Create a UDP socket
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
UDPClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
UDPClientSocket.bind(("", 13117))

print(u"\u001B[35mClient started, listening for offer requests...\u001B[35m")  # title with color!!!!
t_end = time.time() + 10  
while time.time() < t_end: # run for 10 second
    try:
        first_massage = UDPClientSocket.recvfrom(bufferSize)
        full_massage = struct.unpack('<3Q', first_massage[0])
        full_massage += first_massage[1]
        if full_massage[1] == 2 and full_massage[0] == 4276993775:  # The message is rejected if it doesn’t start with this cookie 0xfeedbeef. 
            tcp_port = full_massage[2]  # The port on the server that the client is supposed to connect to over TCP
            print("“Received offer from " + full_massage[3] + ", attempting to connect...")
            try:
                group_name = ''.join(random.choice(string.ascii_lowercase) for i in range(5)) # find random group name
                ClientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                ClientSock.connect(('localhost', tcp_port))
                final_name = group_name+"\n" 
                ClientSock.send(final_name.encode()) # send the group name to the server
            except:
                break
            try:
                start_message = ClientSock.recv(bufferSize).decode() # receive start massage 
                if start_message != "":
                    print(start_message)
                    t_end3 = time.time() + 10
                    while time.time() < t_end3:  # for 10 second send every char to server
                        one_key = msvcrt.getch()
                        char = one_key.decode('ASCII')
                        ClientSock.send(char.encode())  # every pressed key send to the server
                    res_message = ClientSock.recv(bufferSize).decode()  # receive result massage
                    if res_message != "":
                        print(res_message)
            except:
                break
    except:
        break
print("Server disconnected, listening for offer requests...")
while True:
    massage = UDPClientSocket.recvfrom(bufferSize) # client go back to waiting for offer messages

