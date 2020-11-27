#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import datetime as dt
import tkinter as tk
import threading
import enum

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

        self.today = dt.datetime.today()
        self.timetable = TimeTable(self.today)
        self.status = 0
        self.disp_go_msg = 0
        self.disp_come_msg = 0

        self.f1 = tk.Frame(master, width=1280, height=165, bg=Color.GRAY2.value)
        self.f1.pack()
        self.f1.pack_propagate(0)
        self.l11 = tk.Label(self.f1, text="出発", font=("Yu Gothic", 100), bg=Color.GRAY1.value, fg=Color.WHITE.value)
        self.l11.pack(fill=tk.Y, expand=True, anchor=tk.NW, side="left")
        self.l12 = tk.Label(self.f1, text="", font=("GN-キルゴUかなO", 88), fg=Color.ORANGE.value, bg=Color.GRAY2.value)
        self.l12.pack(fill=tk.BOTH, expand=True, anchor=tk.NW, side="left")

        self.f2 = tk.Frame(master, width=1280, height=412)
        self.f2.pack()
        self.f2.pack_propagate(0)
        self.l21 = tk.Label(self.f2, text="00:00")
        self.l21.pack(fill=tk.NONE, expand=True)
        self.l22 = tk.Label(self.f2, text="00:00")
        self.l22.pack(fill=tk.BOTH, expand=True)

        self.f3 = tk.Frame(master, width=1280, height=165, bg=Color.GRAY2.value)
        self.f3.pack()
        self.f3.pack_propagate(0)
        self.l31 = tk.Label(self.f3, text="到着", font=("Yu Gothic", 100), bg=Color.GRAY1.value, fg=Color.WHITE.value)
        self.l31.pack(fill=tk.Y, expand=True, anchor=tk.NW, side="left")
        self.l32 = tk.Label(self.f3, text="", font=("GN-キルゴUかなO", 88), fg=Color.CYAN.value, bg=Color.GRAY2.value)
        self.l32.pack(fill=tk.BOTH, expand=True, anchor=tk.NW, side="left")

        self.f4 = tk.Frame(master, width=1280, height=206)
        self.f4.pack()
        self.f4.pack_propagate(0)
        self.l4 = tk.Label(self.f4, text="00:00", fg=Color.CYAN.value)
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

    def btn_changed(self, num):
        def inner():
            self.status = num
            self.update_disp()
        return inner

    def update_disp(self):
        tables_bool = self.timetable.tables_dt[self.status] > self.today
        tables_bool = tables_bool.values[:, self.timetable.INDEX74]
        tables_bool_come = tables_bool[:, 0]
        tables_bool_go   = tables_bool[:, 1]
        tables_74      = self.timetable.tables[self.status].values[:, self.timetable.INDEX74]
        tables_74_come = tables_74[:, 0]
        tables_74_come = tables_74_come[tables_bool_come]
        tables_74_go   = tables_74[:, 1]
        tables_74_go   = tables_74_go[tables_bool_go]
        tables_74dt    = self.timetable.tables_dt[self.status].values[:, self.timetable.INDEX74]
        tables_74dt_come = tables_74dt[:, 0]
        tables_74dt_come = tables_74dt_come[tables_bool_come]
        tables_74dt_go   = tables_74dt[:, 1]
        tables_74dt_go   = tables_74dt_go[tables_bool_go]
        come_msg = "まもなく到着します"
        go_msg = "まもなく出発します"

        if(len(tables_74_come) > 0):
            self.l4["text"] = tables_74_come[0]
            if(self.today+dt.timedelta(minutes=3)>pd.to_datetime(tables_74_come[0])):
                self.l32["text"] = come_msg[0:self.disp_come_msg+1]
                if(len(come_msg) > self.disp_come_msg):
                    self.disp_come_msg+=1
                else:
                    self.disp_come_msg = 0
            else:
                self.l32["text"] = ""
        else:
            self.l4["text"] = "--:--"
            self.l32["text"] = ""

        if(len(tables_74_go) == 0):
            self.l21["text"] = "サヨナラ！"
            self.l22["text"] = "アバーッ！"
            self.l12["text"] = ""
        else:
            if(self.today+dt.timedelta(minutes=5)>pd.to_datetime(tables_74_go[0])):
                self.l12["text"] = go_msg[0:self.disp_go_msg+1]
                if(len(go_msg) > self.disp_go_msg):
                    self.disp_go_msg+=1
                else:
                    self.disp_go_msg = 0
            else:
                self.l12["text"] = ""

            if(len(tables_74_go) == 1):
                self.l21["text"] = tables_74_go[0]
                self.l22["text"] = "次は最終バスです"
            else:
                self.l21["text"] = tables_74_go[0]
                self.l22["text"] = tables_74_go[1]

    def start_timer(self):
        self.today = dt.datetime.today()
        self.timer = threading.Timer(0.5, self.start_timer)
        self.update_disp()
        self.timer.start()

    def __del__(self):
        self.timer.cancel()

class TimeTable():
    def __init__(self, today):
        self.URL     = 'https://www.kanazawa-it.ac.jp/about_kit/yatsukaho.html'
        self.INDEX74 = [1, 6]
        self.tables = []

        try:
            self.tables = pd.read_html(self.URL, match='運休', na_values="-", header=2)
        except Exception as e:
            for i in range(4):
                self.tables.append(pd.read_csv("csv/{}.csv".format(i), index_col=0))
        else:
            if(len(self.tables) == 4):
                for i in range(len(self.tables)):
                    self.tables[i].to_csv("csv/{}.csv".format(i))

        self.tables_str = [today.strftime('%Y/%m/%d')+"-"+table for table in self.tables]
        self.tables_dt  = [table.astype("datetime64") for table in self.tables_str]

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
