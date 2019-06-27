""" Display, Convert and Edit usbfan bitmap files """
import math
from tkinter import filedialog
# pylint: disable=wildcard-import
# pylint: disable=unused-wildcard-import
from tkinter import *
# pip install pillow
from PIL import Image, ImageTk
from usbfan import Colour
from povconvert import PovConvert


class Window(Frame):
    """ Main application"""

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.pack(fill=BOTH, expand=1)

        sourceframe=Frame(self)
        sourceframe.grid(row=0, column=0)

        img = Label(sourceframe)
        img.pack()

        self.lblImageCvt=Label(sourceframe,text="cvt")
        self.lblImageCvt.pack()

        img2=Label(self)
        img2.grid(row=0,column=1)
        self.lblImage1=img
        self.lblImage2=img2
        self.cvtimage=None
        img2.bind("<Button-1>",self.mouseclick)
        img2.bind("<Button-3>",self.mouseclick3)
        img2.bind("<B1-Motion>",self.mouseclick)
        img2.bind("<B3-Motion>",self.mouseclick3)

        buttonframe = Frame(master=self)
        buttonframe.grid(row=1,column=0,columnspan=2)
        button1= Button(master=buttonframe,text="Open", command=self.button1click)
        button1.pack(side=LEFT)
        self.inverted=IntVar()
        ckInverted=Checkbutton(master=buttonframe,text="Inverted",
                               variable=self.inverted,command=self.update)
        ckInverted.pack(side=LEFT)

        self.colour=StringVar()
        colours=Spinbox(master=buttonframe,textvariable=self.colour,
                        values=list(Colour.__members__.keys()),
                        command=self.update)
        colours.pack(side=LEFT)
        self.dither=IntVar()
        ckDither=Checkbutton(buttonframe,text="Dither", variable=self.dither, command=self.update)
        ckDither.pack(side=LEFT)

        bf2=Frame(self)
        bf2.grid(row=2,column=0,columnspan=2)

        button2=Button(bf2,text="Convert",command=self.loadconvert)
        button2.pack(side=LEFT)

        self.rotate=IntVar()
        ckRotate=Scale(bf2,to=359, orient=HORIZONTAL, variable=self.rotate, command=self.doconvert)
        ckRotate.pack(side=LEFT)
        self.original_image=None
        self.filename=None
        self.rendered_image=None
        self.cvtfilename=None
        self.loadimage(Image.open("wombatcvt.png"))

        self.scale=DoubleVar()
        self.scale.set(1.0)
        ckScale=Scale(bf2,from_=0.2, to=5, resolution=0.1, orient=HORIZONTAL,
                      variable=self.scale, command=self.doconvert)
        ckScale.pack(side=LEFT)

        self.square=BooleanVar()
        ckSquare=Checkbutton(bf2,text="Square",variable=self.square,command=self.doconvert)
        ckSquare.pack(side=LEFT)

        btnSave=Button(bf2,text="Save",command=self.askSave)
        btnSave.pack(side=LEFT)

    def loadimage(self,graphic):
        """ Load pov bitmap and display as it would look on pov"""
        self.original_image=graphic
        render = ImageTk.PhotoImage(self.original_image)
        self.lblImage1.configure(image=render)
        self.lblImage1.image=render
        self.update()

    def button1click(self):
        """ Load pov bitmap filename"""
        filename =  filedialog.askopenfilename(title = "Select file",
                                               filetypes = (("image files",("*.jpg","*.png")),
                                                            ("all files","*.*")))
        if filename!="":
            self.filename=filename
            print("Loading "+filename)
            self.loadimage(Image.open(filename))

    def askSave(self):
        """ Save pov bitmap file"""
        filename =  filedialog.asksaveasfilename(title = "Select file",
                                                 defaultextension=".png",
                                                 filetypes = (("image files",("*.jpg","*.png")),
                                                              ("all files","*.*")))
        if filename!="":
            self.original_image.save(filename)
            print("saved")

    def update(self):
        """ Update display """
        pc=PovConvert()
        inverted=bool(self.inverted.get())
        colour=pc.parseColour(self.colour.get())
        dither=bool(self.dither.get())
        print("Update ",inverted,colour)
        img=self.original_image
        if dither: img=img.convert("1")
        self.rendered_image=pc.renderdisplay(img,colour=colour,inverted=inverted)
        render2=ImageTk.PhotoImage(self.rendered_image)
        self.lblImage2.configure(image=render2)
        self.lblImage2.image=render2

    def loadconvert(self):
        """ Load an image to convert """
        filename =  filedialog.askopenfilename(title = "Select file",
                                               filetypes = (("image files",
                                                             ("*.jpg","*.png")),
                                                            ("all files","*.*")))
        if filename!="":
            self.cvtfilename=filename
            print("Converting "+filename)
            self.cvtimage=Image.open(filename)
            self.doconvert()

    def doconvert(self,arg=None):
        """ Convert image to POV bitmap format """
        # pylint: disable=unused-argument
        if self.cvtimage is None: return
        baseimage=self.cvtimage
        img=self.cvtimage
        if (img.width>320 or self.cvtimage.width>=320):
            img=img.copy()
            img.thumbnail((320,320))
        render=ImageTk.PhotoImage(img)
        self.lblImageCvt.configure(image=render)
        self.lblImageCvt.image=render
        square=self.square.get()
        pc=PovConvert()
        pc.OFFSET=self.rotate.get()
        scale=self.scale.get()
        if square: baseimage=baseimage.resize((pc.XRESOLUTION,pc.XRESOLUTION))
        self.original_image=pc.transformimage(baseimage,scale)
        self.loadimage(self.original_image)

    def mouseclick(self,event):
        """ Handle mouse drawing for button 1 """
        self.draw(event.x,event.y,True)

    def mouseclick3(self,event):
        """ Handle mouse drawing for button 3 """
        self.draw(event.x,event.y,False)

    def draw(self,dx,dy,pen):
        """ Manually edit POV bitmap. pen: True=draw, False=erase """
        pc=PovConvert()
        w,h=self.rendered_image.size
        x=dx-w//2
        y=dy-h//2
        angle=math.degrees(math.atan2(y,x))+90
        if angle<0: angle+=360
        xpos=round(angle*pc.XRESOLUTION/360)
        dist=math.sqrt(x*x+y*y)
        radius=w//2
        pixelsize=pc.PIXELS*pc.OUTER_DIAMETER/pc.INNER_DIAMETER
        innerpixel=pixelsize*pc.INNER_DIAMETER/pc.OUTER_DIAMETER
        ratio=radius/pixelsize
        ypos=round(dist/ratio)-innerpixel
        print(angle,dist,xpos,ypos,ratio,innerpixel)
        if xpos>=0 and xpos<pc.XRESOLUTION-pc.GAP and ypos>=0 and ypos<pc.PIXELS:
            pixels=self.original_image.load()
            pixels[xpos,(pc.PIXELS-ypos)-1]=255 if pen else 0
            self.loadimage(self.original_image)



root = Tk()
app = Window(root)
root.wm_title("Tkinter window")
root.mainloop()
