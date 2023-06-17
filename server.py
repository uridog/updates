import random
import socket as so
import ssl
import threading as th
import time

from db import user_exists, add_user, check_password, build_db, add_score_to_user, get_person_with_highest_score, \
    get_user_score_and_position
import hashlib


class Server:
    clients = []

    def __init__(self, clients_list):
        self.clients = clients_list


class Client_communication:
    def __init__(self):
        self.logged = False
        self.username = ""
        self.is_ready = False

    def handle_msg(self, client_socket):
        cmd = client_socket.recv(2).decode()
        data_len_received = client_socket.recv(4).decode()
        data_received = client_socket.recv(int(data_len_received)).decode()
        if cmd == "01":
            # signup request
            if user_exists(data_received.split(" ")[1]) is True:
                client_socket.send(create_msg("", "20").encode())
                # user taken response
            else:
                add_user(data_received.split(" ")[0], data_received.split(" ")[1], data_received.split(" ")[2],
                         md5_encrypt(data_received.split(" ")[3]))
                client_socket.send(create_msg("", "21").encode())
                self.logged = True
                self.username = data_received.split()[0]
            # user added response
        if cmd == "02":
            # log_in request
            logged = False
            for i in clients:
                if data_received.split(" ")[0] in i:
                    logged = True
            if user_exists(data_received.split(" ")[0]) is not True:
                client_socket.send(create_msg("", "23").encode())
            elif check_password(data_received.split(" ")[0], md5_encrypt(data_received.split(" ")[1])) is not True:
                client_socket.send(create_msg("", "24").encode())

            elif logged:
                client_socket.send(create_msg("", "27").encode())

            else:
                client_socket.send(create_msg("", "25").encode())
                self.logged = True
                self.username = data_received.split()[0]

        if cmd == "03":
            # ready_request send with username
            for c in clientsReady:
                if c[0] == data_received:
                    c[1] = True
                    self.is_ready = True
        if cmd == "04":
            # sends phrase
            return data_received
        if cmd == "05":
            return "05"
        if cmd == "06":
            username2, score = get_person_with_highest_score(int(data_received))
            score = str(score)
            client_socket.send((username2 + " " + score).encode())
        if cmd == "07":
            username2, score, position2 = get_user_score_and_position(data_received)
            client_socket.send((str(username2) + " " + str(score) + " " + str(position2)).encode())

    def log_in_protocol(self, client_socket):
        global clientsReady
        global username
        global clients
        while self.logged is False:
            self.handle_msg(client_socket)
        if len(clients) == 3:
            client_socket.send(create_msg("", "26").encode())
        while len(clients) == 3:
            pass
        clients.append([client_socket, self.username])
        clientsReady.append([clients[-1][1], False])
        return self.username


NUMBER_OF_PLAYERS = 2
certfile = r"localhost.pem"
cafile = r"cacert.pem"
purpose = ssl.Purpose.CLIENT_AUTH
context = ssl.create_default_context(purpose, cafile=cafile)
context.load_cert_chain(certfile)
all_set = []
categories_milon = {
    0: "country",
    1: "capital",
    2: "boy",
    3: "animal",
}
pts_arr = [[0, " "], [0, " "]]
client_num = 0
round_num = 1
client_done = False
finished_game_counter = 0
broadcast_end = False
username = ""
player_lists = []
current_start_letter = 'A'
start_game = False
build_db()
round_letters = ['', '', '']
game_data_updated = False
clientsReady = []
clients = []
buf = 1024
file = open("countries.txt")
countriesList = file.read().split("\n")
file2 = open("cities.txt")
citiesList = file2.read().split("\n")
file3 = open("boy.txt")
boyList = file3.read().split("\n")
movieList = []
file4 = open("movies.txt")
long_movie_List = file4.read().split("\n")
for z in long_movie_List:
    position = z.find("(")
    z = z[:(position - 1)]
    movieList.append(z)
file5 = open("animals.txt", encoding="utf8")
animalsList = file5.read().split("\n")
file6 = open("fruitsAndVeggies.txt")
fruitsAndVeggiesList = file6.read().split("\n")
file7 = open("householdItems.txt")
householdItemsList = file7.read().split("\n")


def md5_encrypt(message):
    md5_hash = hashlib.md5()
    md5_hash.update(message.encode('utf-8'))
    encrypted = md5_hash.hexdigest()
    return encrypted


def create_msg(data, cmd):
    data_len = len(data)
    data_len_len = len(str(data_len))
    data_len = str(data_len)
    for i in range(4 - data_len_len):
        data_len = "0" + data_len
    return cmd + data_len + data


def broadcast(string_to_broadcast, cmd, clientList):
    for i in clientList:
        i[0].send(create_msg(string_to_broadcast, cmd).encode())


def check_if_ready(clientList):
    if len(clientList) < NUMBER_OF_PLAYERS:
        return False
    for i in clientList:
        if i[1] is False:
            return False
    return True


def check_if_category(word_list, category_list, category_array, word_array, num):
    global categories_milon
    for i in category_list:
        if i in word_list:
            category_array[num] = 1
            word_array[num] = i
            return "you said a ?" + categories_milon[num] + "? :" + i + ": "
    return ""


def analyze_word(word_list, category_array, word_array):
    msgToSend = " "
    msgToSend += check_if_category(word_list, countriesList, category_array, word_array, 0)
    msgToSend += check_if_category(word_list, citiesList, category_array, word_array, 1)
    msgToSend += check_if_category(word_list, boyList, category_array, word_array, 2)
    msgToSend += check_if_category(word_list, animalsList, category_array, word_array, 3)
    return msgToSend


def add_lists(list1, list2):
    result = []
    for i in range(len(list1)):
        result.append(list1[i] + list2[i])
    return result


def check_for_special_word(single_category_list):
    special = True
    counter = 0
    for i in range(3):
        if single_category_list[i] != "":
            for x in range(3):
                if x != i:
                    if single_category_list[x] != "":
                        special = False
            if special is True:
                return counter
        counter += 1
        special = True
    return -1


def calculate_points_for_a_single_category(single_category_list):
    points = [0] * len(single_category_list)  # initialize points list to 0
    special_word_index = check_for_special_word(single_category_list)
    counter = 0
    five_pts = False
    if single_category_list[0] == "" and single_category_list[1] == "" and single_category_list[2] == "":
        return points
    if special_word_index != -1:
        points[special_word_index] = 15
        return points
    else:
        for i in single_category_list:
            if i != "":
                for x in single_category_list:
                    if x == i:
                        points[counter] = 5
                        five_pts = True
                if five_pts is False:
                    points[counter] = 10
            counter += 1
        return points


def calculate_and_add_points(player_list):
    all_clients_words_list = [player_list[0][0], player_list[1][0], player_list[2][0]]
    points = [0] * len(player_list)  # initialize points list to 0
    for i in range(7):
        results = calculate_points_for_a_single_category(
            [all_clients_words_list[0][i], all_clients_words_list[1][i], all_clients_words_list[2][i]])
        points = add_lists(results, points)
    for j in range(3):
        add_score_to_user(player_list[j][1], points[j])


def calculate_points_for_debug(player_list):
    for x in range(len(player_list)):
        add_score_to_user(player_list[x][1], 15)
    return [[15, player_list[0][1]], [15, player_list[1][1]]]


def handle_client(client_socket):
    global current_start_letter, client_num
    global clients
    global start_game
    global clientsReady
    global game_data_updated
    global finished_game_counter
    global broadcast_end
    global client_done
    global pts_arr
    categories_arr = [0, 0, 0, 0]
    word_arr = ["", "", "", ""]
    print("222", th.get_native_id())
    client_com = Client_communication()
    """Handles a single client connection."""
    client_name = client_com.log_in_protocol(client_socket)
    while True:
        # ready message
        while client_com.is_ready is False:
            client_com.handle_msg(client_socket)
        for i in range(3):
            client_done = False
            finished_game_counter = 0
            broadcast_end = False
            while start_game is False:
                pass
            game_data_updated = False
            for c in clientsReady:
                if c[0] == client_name:
                    c[1] = False
            data = client_com.handle_msg(client_socket)
            start_time = time.time()
            while client_done is False:
                try:
                    if data == " ":
                        if (time.time() - start_time) > 15 and broadcast_end is False:
                            broadcast("Time is up, turn finished@ ending turn", "10", clients)
                            broadcast_end = True
                            client_done = True
                        else:
                            client_socket.send(create_msg("null", "12").encode())
                    else:
                        myText = data.lower()
                        print(myText)
                        myText = myText.title()
                        myTextListAllWords = myText.split(" ")
                        myTextListAllWords.append(myText)
                        myTextList = [word for word in myTextListAllWords if word.startswith(current_start_letter)]
                        plural_list = []
                        for q in myTextList:
                            plural_list.append(q + "s")
                        myTextList = myTextList + plural_list
                        msgToSend = analyze_word(myTextList, categories_arr, word_arr)
                        if 0 not in categories_arr and broadcast_end is False:
                            broadcast(msgToSend, "10", clients)
                            broadcast_end = True
                            client_done = True
                        elif (time.time() - start_time) > 15 and broadcast_end is False:
                            broadcast(msgToSend, "10", clients)
                            broadcast_end = True
                            client_done = True
                        else:
                            if msgToSend == "":
                                client_socket.send(create_msg("null", "12").encode())
                            client_socket.send(create_msg(msgToSend, "13").encode())
                    data = client_com.handle_msg(client_socket)

                except:
                    pass

            player_lists.append([word_arr, client_name])
            finished_game_counter += 1
            while game_data_updated is False:
                pass
            won = 0
            if pts_arr[0][0] > pts_arr[1][0]:
                won = 1
            elif pts_arr[1][0] > pts_arr[0][0]:
                won = 2
            for r in range(2):
                if client_name == pts_arr[r][1]:
                    if i != 2:
                        client_socket.send(create_msg(str(pts_arr[r][0]), "45").encode())
                    else:
                        if won == 0:
                            client_socket.send(create_msg(str(pts_arr[r][0])+" 0", "46").encode())
                        elif won == (r+1):
                            client_socket.send(create_msg(str(pts_arr[r][0]) + " 1", "46").encode())
                        else:
                            client_socket.send(create_msg(str(pts_arr[r][0]) + " 2", "46").encode())
            categories_arr = [0, 0, 0, 0, 0, 0, 0]
            word_arr = ["", "", "", "", "", "", ""]
            broadcast_end = False
            while "05" not in data:
                data = client_com.handle_msg(client_socket)
            if i != 2:
                for c in clientsReady:
                    if c[0] == client_name:
                        c[1] = True


def main():
    global current_start_letter, finished_game_counter
    global start_game
    global game_data_updated
    global round_num
    global client_num
    global round_letters
    global pts_arr
    client_num = 0
    server_socket = so.socket()
    server_socket.bind(('0.0.0.0', 8820))
    server_socket.listen(1)
    while client_num < NUMBER_OF_PLAYERS:
        (client_socket, client_address) = server_socket.accept()
        client_socket = context.wrap_socket(client_socket, server_side=True)
        client_num += 1
        try:
            e = th.Thread(target=handle_client, args=(client_socket,))
            e.start()
        except:
            pass
    while client_num == NUMBER_OF_PLAYERS:
        while check_if_ready(clientsReady) is False:
            pass
        for i in range(3):

            start_game = False
            while check_if_ready(clientsReady) is False:
                pass
            current_start_letter = random.choice("ABCDGHIJKLMNOPRST")
            while current_start_letter in round_letters:
                current_start_letter = random.choice("ABCDGHIJKLMNOPRST")
            round_letters[i] = current_start_letter
            broadcast(current_start_letter, "11", clients)
            start_game = True
            while finished_game_counter < NUMBER_OF_PLAYERS:
                pass
            finished_game_counter = 0
            pts_arr = calculate_points_for_debug(player_lists)

            game_data_updated = True
            start_game = False


main()
