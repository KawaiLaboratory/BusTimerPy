#!/usr/bin/env python
# coding: utf-8

import pandas   as pd
import datetime as dt
import tkinter  as tk
import threading
import enum
import sys

class Application(tk.Frame):
    def __init__(self, master = None):
        super().__init__(master)
        master.option_add('*font', 'GN-キルゴUかなO 120')
        master.option_add('*background', Color.BLACK.value)
        master.option_add('*foreground', Color.ORANGE.value)
        master.option_add('*Button.foreground', Color.WHITE.value)
        master.title(u"BusTimer")
        master.geometry("1280x1030")
        master.protocol("WM_DELETE_WINDOW", self.closed(master))

        self.now = int(dt.datetime.now().strftime("%H%M"))
        self.timetable = TimeTable()
        self.status = 0
        self.anm_status = True
        self.disp_go_msg = 0
        self.disp_come_msg = 0

        self.f1 = tk.Frame(master, width=1280, height=141, bg=Color.GRAY2.value)
        self.f1.pack()
        self.f1.pack_propagate(0)
        self.l11 = tk.Label(self.f1, text="出発", font=("Yu Gothic", 100), bg=Color.GRAY1.value, fg=Color.WHITE.value)
        self.l11.pack(fill=tk.Y, expand=True, anchor=tk.NW, side="left")
        self.l12 = tk.Label(self.f1, text="", font=("GN-キルゴUかなO", 88), fg=Color.ORANGE.value, bg=Color.GRAY2.value)
        self.l12.pack(fill=tk.BOTH, expand=True, anchor=tk.NW, side="left")

        self.f2 = tk.Frame(master, width=1280, height=446)
        self.f2.pack()
        self.f2.pack_propagate(0)
        self.l21 = tk.Label(self.f2, text="--:--")
        self.l21.pack(fill=tk.NONE, expand=True)
        self.l22 = tk.Label(self.f2, text="--:--")
        self.l22.pack(fill=tk.BOTH, expand=True)

        self.f3 = tk.Frame(master, width=1280, height=141, bg=Color.GRAY2.value)
        self.f3.pack()
        self.f3.pack_propagate(0)
        self.l31 = tk.Label(self.f3, text="到着", font=("Yu Gothic", 100), bg=Color.GRAY1.value, fg=Color.WHITE.value)
        self.l31.pack(fill=tk.Y, expand=True, anchor=tk.NW, side="left")
        self.l32 = tk.Label(self.f3, text="", font=("GN-キルゴUかなO", 88), fg=Color.WHITE.value, bg=Color.GRAY2.value)
        self.l32.pack(fill=tk.BOTH, expand=True, anchor=tk.NW, side="left")

        self.f4 = tk.Frame(master, width=1280, height=220)
        self.f4.pack()
        self.f4.pack_propagate(0)
        self.l4 = tk.Label(self.f4, text="--:--", fg=Color.CYAN.value)
        self.l4.pack(fill=tk.BOTH, expand=True)

        self.f5 = tk.Frame(master, width=1280, height=82)
        self.f5.pack()
        self.f5.pack_propagate(0)
        self.b1 = tk.Button(self.f5, text="平日", font=("GN-キルゴUかなO",20), command=self.btn_changed(0))
        self.b1.pack(fill=tk.BOTH, expand=True, side="left")
        self.b2 = tk.Button(self.f5, text="土日", font=("GN-キルゴUかなO",20), command=self.btn_changed(1))
        self.b2.pack(fill=tk.BOTH, expand=True, side="left")
        self.b3 = tk.Button(self.f5, text="春夏平日", font=("GN-キルゴUかなO",20), command=self.btn_changed(2))
        self.b3.pack(fill=tk.BOTH, expand=True, side="left")
        self.b4 = tk.Button(self.f5, text="春夏土日", font=("GN-キルゴUかなO",20), command=self.btn_changed(3))
        self.b4.pack(fill=tk.BOTH, expand=True, side="left")

        self.start_timer()

    def closed(self, master):
        def inner():
            self.timer.cancel()
            master.destroy()
            sys.exit()

    def btn_changed(self, num):
        def inner():
            self.status = num
            self.update_disp()
        return inner

    def time2str(self, time):
        if(self.anm_status):
            msg = "{}:{}".format(str(time)[0:2], str(time)[2:4])
        else:
            msg = "{} {}".format(str(time)[0:2], str(time)[2:4])
        return msg

    def coming_soon(self, time, now, delta):
        m = now%100
        h = int(now/100)

        if(m+delta >= 60):
            over = int((m+delta)/60)
            m = m+delta-60
            h = h+1
        else:
            m = m+delta
            h = h

        added_time = h*100+m
        return added_time>time

    def update_disp(self):
        self.now = int(dt.datetime.now().strftime("%H%M"))
        self.anm_status = not self.anm_status
        self.tablelist_go   = [i for i in self.timetable.val74go_int[self.status] if int(i) > self.now]
        self.tablelist_come = [i for i in self.timetable.val74come_int[self.status] if int(i) > self.now]

        come_msg = "まもなく到着します"
        go_msg = "まもなく出発します"
        margin = 34

        if(len(self.tablelist_come) > 0):
            nxt_come = self.tablelist_come[0]
            self.l4["text"] = self.time2str(nxt_come)
            if(self.coming_soon(nxt_come, self.now, 5)):
                self.l32["text"] = " "*(margin-self.disp_come_msg)+come_msg+" "*self.disp_come_msg
                if(self.disp_come_msg >= margin):
                    self.disp_come_msg = 0
                else:
                    self.disp_come_msg += 1
            else:
                self.l32["text"] = ""
        else:
            self.l4["text"] = "--:--"
            self.l32["text"] = ""
            self.disp_come_msg = 0

        if(len(self.tablelist_go) == 0):
            self.l21["text"] = "サヨナラ！"
            self.l22["text"] = "アバーッ！"
            self.l12["text"] = ""
            self.disp_go_msg = 0
        else:
            if(self.coming_soon(nxt_come, self.now, 10)):
                self.l12["text"] = " "*(margin-self.disp_go_msg)+go_msg+" "*self.disp_go_msg
            else:
                self.l12["text"] = ""

            if(len(self.tablelist_go) == 1):
                self.l21["text"] = self.time2str(self.tablelist_go[0])
                self.l22["text"] = "次は最終バスです"
            else:
                self.l21["text"] = self.time2str(self.tablelist_go[0])
                self.l22["text"] = self.time2str(self.tablelist_go[1])

            if(self.disp_go_msg >= margin):
                self.disp_go_msg = 0
            else:
                self.disp_go_msg += 1

    def start_timer(self):
        self.today = dt.datetime.today()
        self.timer = threading.Timer(1, self.start_timer)
        self.update_disp()
        self.timer.start()

    def __del__(self):
        self.timer.cancel()

class TimeTable():
    def __init__(self):
        self.URL     = 'https://www.kanazawa-it.ac.jp/about_kit/yatsukaho.html'
        self.COME74 = 1
        self.GO74   = 6

        self.tables = []
        self.val74come_str = []
        self.val74come_int = []
        self.val74go_str   = []
        self.val74go_int   = []

        try:
            self.tables = pd.read_html(self.URL, match='74号館前', na_values="-", header=2)
        except Exception as e:
            for i in range(4):
                self.tables.append(pd.read_csv("csv/{}.csv".format(i), index_col=0))
            print("read csv")
        else:
            if(len(self.tables) == 4):
                for i in range(len(self.tables)):
                    self.tables[i].to_csv("csv/{}.csv".format(i))
                print("read html")
            else:
                for i in range(4):
                    self.tables.append(pd.read_csv("csv/{}.csv".format(i), index_col=0))
                print(len(self.tables))

        self.val74come_str = [[str(col).replace(":", "").replace("nan", "0") for col in table.values[:, self.COME74]] for table in self.tables]
        self.val74go_str   = [[str(col).replace(":", "").replace("nan", "0") for col in table.values[:, self.GO74]]   for table in self.tables]
        self.val74come_int = [[int(i) for i in row if int(i) > 0] for row in self.val74come_str]
        self.val74go_int   = [[int(i) for i in row if int(i) > 0] for row in self.val74go_str]

class Color(enum.Enum):
    ORANGE = "#ffb400"
    BLACK = "#212121"
    GRAY1 = "#474744"
    GRAY2 = "#757575"
    GRAY3 = "#BDBDBD"
    CYAN  = "#2994b2"
    WHITE = "#fffbe0"

root = tk.Tk()
app = Application(root)

app.mainloop()
