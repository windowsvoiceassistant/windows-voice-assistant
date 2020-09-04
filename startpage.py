import tkinter as tk
import webbrowser
import os
# from computercontrol import main

window = tk.Tk()
window.geometry('400x200')
window.columnconfigure(0, minsize=400)
window.rowconfigure(4, minsize=200)

def open_instructions_webpage(event):
    filepath = os.getcwd()
    url = "file:///"+filepath+"/demo/demo.html"
    webbrowser.open(url, new=0, autoraise=True)

def start_program(event):
    print("start")

tk.Label(
    window,
    text='Windows Voice Assistant',
    borderwidth=4,
    font=("Arial", 20)
).grid(row=0,column=0,sticky='n')

tk.Label(
    window,
    text='Powered by Google\'s Cloud Speech-to-Text API + Python',
    fg='black',
    wraplength=350,
    justify='center',
).grid(row=1,column=0,sticky='n')

start = tk.Button(
    window,
    text='Start',
    borderwidth=4
)
start.grid(row=2,column=0)
# start.bind("<Button-0>", start)

b = tk.Button(
    window,
    text='Voice Command Library',
    borderwidth=4
)
b.grid(row=3,column=0)

b.bind("<Button-1>", open_instructions_webpage)


window.mainloop()