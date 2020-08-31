# https://stackoverflow.com/questions/19080499/transparent-background-in-a-tkinter-window
# windows
import tkinter as tk # Python 3
root = tk.Tk()

root.overrideredirect(True)
root.lift()
root.wm_attributes("-topmost", True)
root.attributes('-alpha', 0.5)

root.wm_attributes("-transparentcolor", "brown")
 
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
 
step_peprcentage = 0.1
step_width = int(screen_width * step_peprcentage)
step_height = int(screen_height * step_peprcentage)
 
c = tk.Canvas(root,height=screen_height, width=screen_width, bg = "brown")

c.delete('grid_line') 

max_size = 10
screen_width_count = 0
for i in range(0 , max_size):
    c.create_line([(screen_width_count, 0), (screen_width_count, screen_height)], tag='grid_line')
    screen_width_count = screen_width_count + step_width

screen_height_count = 0
for i in range(0 , max_size):
    c.create_line([(0, screen_height_count), (screen_width, screen_height_count)], tag='grid_line')
    screen_height_count = screen_height_count + step_height

 
c.pack(fill=tk.BOTH, expand=True)

column_count = 0
row_count = 0
for x in range(0, max_size):
    for y in range(0, max_size):
        column = int(column_count /step_height)
        row = int(row_count /step_width)
 
        number = row + 10*column+1
        l = tk.Label(root, text=str(number), bg="black",fg="white")
        l.place(relx=(row_count/screen_width), rely=(column_count/screen_height))

        column_count = column_count + step_height
    row_count = row_count + step_width
    column_count = 0
 
root.after(5*1000, lambda: root.destroy())
 
root.mainloop()
