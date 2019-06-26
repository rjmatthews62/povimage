from tkinter import *
from povconvert import PovConvert
from usbfan import Colour

# pip install pillow
from PIL import Image, ImageTk

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.pack(fill=BOTH, expand=1)
        pc=PovConvert()
        load = pc.renderdisplay(Image.open("wombatcvt.png"),colour=Colour.yellow,inverted=True)
        
        self.image=load
        render = ImageTk.PhotoImage(load)
        img = Label(self, image=render)
        img.image = render
        img.place(x=0, y=0)

        
root = Tk()
app = Window(root)
root.wm_title("Tkinter window")
root.geometry("%dx%d" % app.image.size)
root.mainloop()
