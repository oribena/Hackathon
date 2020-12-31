import socket
import _thread
import time
import struct
import threading
import random

bufferSize = 1024
FORMAT = "32s 1s 40s 1s 256s 256s"
teams_array = []
clients_array = []
random_numbers_array = [1, 1, 2, 2]
random.shuffle(random_numbers_array)
members_group1 = []
members_group2 = []
points_sum = 0
points_group1 = 0
points_group2 = 0
all_members = 0
end_time = 10 + time.time()
count = 0


def group_thread():
    global points_group1
    global points_group2
    global count
    locking_count = threading.RLock()

    try:
        global end_time
        # TCP
        TCP_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        TCP_server_socket.bind(("", 10))
        TCP_server_socket.listen(1)
        while time.time() < end_time and count < 4:  # less than 10 sec and less than 4 clients
            client_socket, addr = TCP_server_socket.accept()
            group = threading.Thread(target=new_client, args=(client_socket, addr))
            group.start()
            with locking_count:
                count += 1  # count the clients
        return

    except:
        print("Wrong type of message received")


# the play of group 1
def group1_playing(client, address):
    global points_group1
    locking = threading.RLock()
    time_after_10_sec = 10 + time.time()
    while time.time() < time_after_10_sec:  # 10 seconds after the server was started
        try:
            key = client.recv(bufferSize)
            keyboard_pressing = key.decode()
            if keyboard_pressing:
                # count the points
                with locking:
                    points_group1 += 1
        except:
            continue
    return


# the play of group 2
def group2_playing(client, address):
    global points_group2
    locking = threading.RLock()
    time_after_10_sec = 10 + time.time()
    while time.time() < time_after_10_sec:  # 10 seconds after the server was started
        try:
            key = client.recv(bufferSize)
            keyboard_pressing = key.decode()
            if keyboard_pressing:
                # count the points
                with locking:
                    points_group2 += 1
        except:
            continue
    return


# The server records the names sent by the clients
# and assigns each of the clients randomly to group 1 or group 2
def new_client(client_socket, addr):
    global clients_array
    global members_group1
    global members_group2
    global points_group1
    global points_group2
    global all_members
    global end_time
    locking1 = threading.RLock()
    locking2 = threading.RLock()
    locking3 = threading.RLock()

    try:
        name = client_socket.recv(1024).decode()
        if name:
            # add the name to the clients array
            with locking1:
                clients_array.append(name)
            while len(clients_array) < 4:  # while there are less than 4 clients
                time.sleep(1)
            all_members = len(members_group1) + len(members_group2)
            if all_members < 4:
                # assign random group
                group_num = random_numbers_array[all_members]
                if group_num == 1:
                    with locking2:
                        members_group1.append(name)
                if group_num == 2:
                    with locking3:
                        members_group2.append(name)
            while len(members_group1) + len(members_group2) < 4:  # while there are less than 4 members
                time.sleep(1)
        while time.time() < end_time:  # wait 10 sec
            time.sleep(1)
            # the game begins - the server sends a welcome message to all of the clients with the names of the teams
        welcome_game = "Welcome to Keyboard Spamming Battle Royale.\n" \
                       "Group 1:\n==\n" + members_group1[0] + members_group1[1] \
                       + "Group 2:\n==\n" + members_group2[0] + members_group2[1] +\
                       "\nStart pressing keys on your keyboard as fast as you can!!\n"
        client_socket.send(welcome_game.encode())
        if group_num == 1:
            _thread.start_new_thread(group1_playing, (client_socket, addr))
        if group_num == 2:
            _thread.start_new_thread(group2_playing, (client_socket, addr))
        time.sleep(10)
        # check who is the winner
        if points_group1 < points_group2:
            winning_group = "Group 2"
            winners = members_group1[0] + members_group1[1]  # update the winners members
        else:
            winning_group = "Group 1"
            winners = members_group2[0] + members_group2[1]  # update the winners members
        # the massage to print
        finish_message = str(bonus()) +"\n" + "\nGame over!\nGroup 1 typed in " + str(points_group1) + " characters. Group 2 typed in " \
                         + str(points_group2) + " characters.\n" + winning_group + " wins!\n\n" \
                         + "Congratulations to the winners:\n==\n" + "" + winners
        client_socket.send(finish_message.encode())
        return

    except:
        print("error occurred")


def bonus():  # fun fact with color!!!!
    """
    :return: prints randomly a fun fact
    """
    facts = ["The First Computer Weighed More Than 27 Tons", "The First Computer Mouse was Made of Wood",
                     "The First Known Computer Programmer was a Woman, her name was Ada Lovelace",
                     "People Blink Less When They Use Computers", "Hackers Write About 6,000 New Viruses Each Month"]
    return u"\u001B[36mFun Fact:\n" + random.choice(facts)


# UDP broadcast
localPort = 7700

# The server starts
# UDP
UDP_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDP_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
UDP_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
UDP_server_socket.bind(('', localPort))
print(u"\u001B[32mServer started' listening on IP address 172.1.0.22\u001B[32m")  # title with color!!!!
thread = threading.Thread(target=group_thread, args=())
thread.start()

while time.time() < end_time:

    try:
        # send
        MSG = struct.pack('<3Q', 0xfeedbeef, 0x2, 0xA)
        UDP_server_socket.sendto(MSG, ('<broadcast>', 13117))
        time.sleep(1)

    except:
        time.sleep(1)

while time.time() < end_time:
    time.sleep(1)

time.sleep(10)

# The server closes
print("Game over, sending out offer requests...")
while True:
    # send
    MSG = struct.pack('<3Q', 0xfeedbeef, 0x2, 0xA)
    UDP_server_socket.sendto(MSG, ('<broadcast>', 13117))
    time.sleep(1)
