from tkinter import filedialog
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
        img = Label(self)
        img.grid(row=0, column=0)
        img2=Label(self)
        img2.grid(row=0,column=1)
        self.lblImage1=img
        self.lblImage2=img2

        buttonframe = Frame(master=self)
        buttonframe.grid(row=1,column=0,columnspan=2)
        button1= Button(master=buttonframe,text="Open", command=self.button1click)
        button1.pack(side=LEFT)
        self.inverted=IntVar()
        ckInverted=Checkbutton(master=buttonframe,text="Inverted",variable=self.inverted,command=self.update)
        ckInverted.pack(side=LEFT)

        self.colour=StringVar()
        colours=Spinbox(master=buttonframe,textvariable=self.colour,values=list(Colour.__members__.keys()),
                        command=self.update)
        colours.pack(side=LEFT)                        
        self.loadimage(Image.open("wombatcvt.png"))


    def loadimage(self,graphic):
        self.original_image=graphic
        render = ImageTk.PhotoImage(self.original_image)
        self.lblImage1.configure(image=render)
        self.lblImage1.image=render
        self.update()

    def button1click(self):
        filename =  filedialog.askopenfilename(title = "Select file",
            filetypes = (("image files",("*.jpg","*.png")),("all files","*.*")))
        if (filename!=""):
            self.filename=filename
            print("Loading "+filename)
            self.loadimage(Image.open(filename))

    def update(self):
        pc=PovConvert()
        inverted=bool(self.inverted.get())
        colour=pc.parseColour(self.colour.get())
        print("Update ",inverted,colour)
        self.rendered_image=pc.renderdisplay(self.original_image,colour=colour,inverted=inverted)
        render2=ImageTk.PhotoImage(self.rendered_image)
        self.lblImage2.configure(image=render2)
        self.lblImage2.image=render2
        
        
root = Tk()
app = Window(root)
root.wm_title("Tkinter window")
root.mainloop()
