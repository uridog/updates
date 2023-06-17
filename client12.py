# Python program to translate
# speech to text and text to speech

import socket
import ssl
import threading as th
import time

import speech_recognition as sr


from enter_screen1 import Ui_startWindow, show_win
from log_in_screen1 import Ui_LogInWindow, show_window
from lobby_screen import Ui_readyWindow, show_lobby_window
from signin_screen import Ui_signUpWindow, show_sign_window
from game_screen1 import Ui_gameWindow, show_game
from leaderboard_screen import Ui_MainWindow, show_leaderboard_window
from tutorial_screen import Ui_TutorialWindow, show_tutorial_window

context = ssl.create_default_context()
# Set the context to not verify the server's SSL/TLS certificate
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE


class Client:

    def __init__(self, server_socket):
        self.socket = server_socket
        self.screen_state = -1
        self.first_name = ""
        self.last_name = ""
        self.username = ""
        self.password = ""
        self.client_ready = False
        self.client_singed = False
        self.game_start = False
        self.server_ans = False
        self.voice = True
        self.curr_word = ""
        self.tutorial = [0, 0]
        self.record = False


def create_msg(data1, cmd1):
    data_len = len(data1)
    data_len_len = len(str(data_len))
    data_len = str(data_len)
    for i in range(4 - data_len_len):
        data_len = "0" + data_len
    return cmd1 + data_len + data1


def handle_data(client_socket):
    cmd3 = client_socket.recv(2).decode()
    data_len_received = client_socket.recv(4).decode()
    data_received5 = client_socket.recv(int(data_len_received)).decode()
    return data_received5, cmd3


def voice_to_text():
    global MyText
    r = sr.Recognizer()
    try:
        # use the microphone as source for input.
        with sr.Microphone() as source2:

            # wait for a second to let the recognizer
            # adjust the energy threshold based on
            # the surrounding noise level
            r.adjust_for_ambient_noise(source2, duration=0.2)

            # listens for the user's input
            try:
                audio2 = r.listen(source2, 5, 3)
                MyText = r.recognize_google(audio2)
                print(MyText)
            except:
                pass
            # Using google to recognize audio


    except sr.RequestError as e:
        pass

    except sr.UnknownValueError:
        pass


categories_milon = {
    "country": 0,
    "capital": 1,
    "boy": 2,
    "animal": 3,

}
ans = " "
MyText = ""
buf = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 8820))
s = context.wrap_socket(s, server_hostname='127.0.0.1')
socket_running = True
client12 = Client(s)
start_window = Ui_startWindow(client12)
leaderboard_window = Ui_MainWindow(client12)
tutorial_window = Ui_TutorialWindow(client12)
round_num = 0

try:
    show_win(start_window)
except:
    pass

while client12.screen_state == -1:
    pass
if client12.screen_state == 0:
    sign_in_window = Ui_signUpWindow(client12)
    try:
        e = th.Thread(target=show_sign_window, args=(sign_in_window,))
        e.start()
    except:
        pass
    while client12.username == "":
        pass
    userInfo = client12.username + " " + client12.first_name + " " + client12.last_name + " " + client12.password
    s.send(create_msg(userInfo, "01").encode())
    current_username = client12.username
    data_received, cmd = handle_data(s)
    while cmd == "20":
        client12.server_ans = True
        sign_in_window.username_taken.show()
        client12.server_ans = False
        while client12.username == current_username:
            pass
        userInfo = client12.username + " " + client12.first_name + " " + client12.last_name + " " + client12.password
        s.send(create_msg(userInfo, "01").encode())
        client12.server_ans = True
    client12.client_singed = True
    data_received, cmd = handle_data(s)
elif client12.screen_state == 1:
    log_in_window = Ui_LogInWindow(client12)
    try:
        e = th.Thread(target=show_window, args=(log_in_window,))
        e.start()
    except:
        pass
    while client12.username == "" and client12.password == "":
        pass
    userInfo = client12.username + " " + client12.password
    old_username = client12.username
    old_password = client12.password
    s.send(create_msg(userInfo, "02").encode())
    data_received, cmd = handle_data(s)
    client12.server_ans = True
    while cmd == "23" or cmd == "24" or cmd == "27":
        print("cnd" + cmd)
        if cmd == "27":
            log_in_window.player_in.show()
        else:
            log_in_window.label_2.show()
        client12.server_ans = False
        while client12.username == old_username and client12.password == old_password:
            pass
        old_username = client12.username
        old_password = client12.password
        userInfo = client12.username + " " + client12.password
        s.send(create_msg(userInfo, "02").encode())
        data_received, cmd = handle_data(s)
        client12.server_ans = True
    client12.client_singed = True
ready_window = Ui_readyWindow(client12)
time.sleep(0.3)
print("rghtrhdfgrgregerg")
try:
    print("tfhfdthft")
    t6 = th.Thread(target=show_lobby_window, args=(ready_window,))
    t6.start()
except:
    pass
print("rgedgd ")
while socket_running:
    client12.client_ready = False
    round_num = 0
    client12.screen_state = 2
    client12.game_start = False
    leaderboard_list = []
    while client12.client_ready is False:
        if client12.screen_state == 4:
            for i in range(3):
                s.send(create_msg(str(i + 1), "06").encode())
                username_and_score = s.recv(1024).decode()
                username2 = username_and_score.split(" ")[0]
                score = username_and_score.split(" ")[1]
                a = [str(username2), str(score)]
                leaderboard_list.append(a)
            s.send(create_msg(client12.username, "07").encode())
            user_data = s.recv(1024).decode()
            username2 = user_data.split(" ")[0]
            score = user_data.split(" ")[1]
            position2 = user_data.split(" ")[2]
            curr_user = [str(position2), str(username2), str(score)]
            try:
                t87 = th.Thread(target=show_leaderboard_window, args=(leaderboard_window, leaderboard_list, curr_user))
                t87.start()
            except:
                pass
            while client12.screen_state == 4:
                pass
            ready_window.voice_button.show()
            ready_window.leaderboard_button.show()
            ready_window.textgmae_button.show()
            ready_window.tutorial_button.show()
        if client12.screen_state == 5:
            try:
                t8 = th.Thread(target=show_tutorial_window, args=(tutorial_window,))
                t8.start()
            except:
                pass
            print("sf42e3")
            while client12.record is False:
                pass
            print("sf4uir")
            MyText = " "
            while MyText != "Germany" and MyText != "germany":
                voice_to_text()
            tutorial_window.welldone_label.show()
            tutorial_window.banana_label.show()
            tutorial_window.banana_photo.show()
            while MyText != "Banana" and MyText != "banana":
                voice_to_text()
            client12.record = False
            tutorial_window.excellent_label.show()
            tutorial_window.continue_button.show()
            while client12.screen_state == 5:
                pass
            ready_window.voice_button.show()
            ready_window.leaderboard_button.show()
            ready_window.textgmae_button.show()
            ready_window.tutorial_button.show()

    s.send(create_msg(client12.username, "03").encode())
    client12.screen_state = 3
    game_window = Ui_gameWindow(client12)
    try:
        t1 = th.Thread(target=show_game, args=(game_window,))
        t1.start()
    except:
        pass
    while round_num < 3:
        if round_num == 0:
            while game_window.opened is False:
                pass
            try:
                t3 = th.Thread(target=game_window.waiting_for_players)
                t3.start()
            except:
                pass
        round_num += 1
        # try:
        #     t1 = th.Thread(target=game_window.start_round)
        #     t1.start()
        # except:
        #     pass
        letter_recieved, cmd = handle_data(s)
        while "11" not in cmd:
            letter_recieved, cmd = handle_data(s)
        client12.game_start = True
        letter = letter_recieved
        game_window.set_letter(round_num, letter)
        game_window.game_table.update()

        ans = " "
        while cmd != "10":
            MyText = ""
            if client12.voice is True:
                voice_to_text()
            else:
                while client12.curr_word == "":
                    pass
                print(client12.curr_word)
                MyText = client12.curr_word
            s.send(create_msg(MyText, "04").encode())
            client12.curr_word = ""
            ans, cmd = handle_data(s)
            if cmd == "13":
                ans_list = ans.split(":")
                cat_list = ans.split("?")
                for i in range(int(len(ans_list) / 2)):
                    # table in row round num, coloum category dictionary = ans list 1+2i
                    game_window.insert_value(categories_milon[cat_list[1 + 2 * i]], round_num, ans_list[1 + 2 * i])
                    game_window.game_table.update()
        s.send(create_msg("game end", "05").encode())
        pts, cmd = handle_data(s)
        if cmd == "45":
            game_window.insert_value(4, round_num, str(pts))
            game_window.game_table.update()
        else:
            pts_real = pts.split(" ")[0]
            game_window.insert_value(4, round_num, str(pts_real))
            game_window.game_table.update()
            won = pts.split(" ")[1]
            if won == "1":
                game_window.won_label.show()
            elif won == "2":
                game_window.lost_label.show()
            else:
                game_window.tied_label.show()
    game_window.return_button.show()
    game_window.play_again_button.show()
    game_window.word_text.hide()
    game_window.submit_button.hide()
    game_window.word_text.hide()
    while client12.screen_state == 3:
        pass
    ready_window.voice_button.show()
    ready_window.leaderboard_button.show()
    ready_window.textgmae_button.show()
    ready_window.tutorial_button.show()
    ready_window.waiting_text.hide()
