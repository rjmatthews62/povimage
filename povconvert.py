#!/usr/bin/env python3
"""
A library for manipulating images for a POV USB Fan
"""
from typing import Union
import math
import argparse
import PIL
from PIL import Image
from usbfan import Colour, Column, Device, Message, Program, \
    OpenTransition,CloseTransition,MessageStyle


class PovConvert:
    """ Main Conversion class """
    OUTER_DIAMETER=160
    INNER_DIAMETER=80
    PIXELS=11
    XRESOLUTION=160
    GAP=16
    OFFSET=0


    def cvtimage(self, filename:str, destination:str):
        """ Map rectangular image file to pov circular bitmap """
        graphic=Image.open(filename)
        result=self.transformimage(graphic)
        result.save(destination,"PNG")

    def renderdisplay(self, graphic:Image.Image,
                      width:int=320, colour:Colour=Colour.white,
                      inverted:bool=False) -> Image.Image:
        """
        Render an image as it would look on the POV
        """
        src=graphic.convert("L").load()
        dest=Image.new("RGB",(width,width))
        data=dest.load()
        d=PIL.ImageDraw.Draw(dest)
        cx=width//2
        cy=width//2
        radius=min(cx,cy)
        ratio=(self.OUTER_DIAMETER-self.INNER_DIAMETER)/self.PIXELS
        thickness=max(1,round(ratio)-1)
        wedge=180/self.XRESOLUTION
        try:
            dcolor=PIL.ImageColor.getcolor(colour.name,"RGB")
        except:
            dcolor=PIL.ImageColor.getcolor("white","RGB")

        black=PIL.ImageColor.getcolor("black","RGB")
        for x in range(self.XRESOLUTION-self.GAP):
            angle=math.radians(x*360/self.XRESOLUTION+self.OFFSET)
            anglemin=x*360/self.XRESOLUTION+self.OFFSET-wedge
            anglemax=x*360/self.XRESOLUTION+self.OFFSET+wedge
            mx=math.cos(angle)
            my=math.sin(angle)

            for y in range(self.PIXELS):
                ny=(y*ratio)+self.INNER_DIAMETER
                mr=ny*radius/self.OUTER_DIAMETER
                pixel=src[x,(self.PIXELS-y)-1]
                if inverted:
                    col=dcolor if pixel<128 else black
                else:
                    col=dcolor if pixel>=128 else black
                px=round(mr*mx)+cx
                py=round(mr*my)+cy
                d.arc((cx-mr,cy-mr,cx+mr,cy+mr),anglemin,anglemax,col,width=thickness)
                data[px,py]=col
        del d
        return dest.transpose(PIL.Image.ROTATE_90)

    def transformimage(self,graphic:Image.Image,scale=1.0):
        """ Map a square image to a POV bitmap """
        img = Image.new("L", (self.XRESOLUTION-self.GAP, self.PIXELS))
        w,h = graphic.size
        cx=w//2
        cy=h//2
        radius=min(cx,cy)
        ratio=(self.OUTER_DIAMETER-self.INNER_DIAMETER)/self.PIXELS
        imgdata=graphic.convert("L").load() # Convert to levels.
        destmap=img.load()
        for x in range(self.XRESOLUTION-self.GAP):
            angle=math.radians(x*360/self.XRESOLUTION+self.OFFSET)
            mx=math.cos(angle)
            my=math.sin(angle)
            for y in range(self.PIXELS):
                ny=(y*ratio)+self.INNER_DIAMETER
                mr=(ny/scale) * radius/self.OUTER_DIAMETER
                pixel=0
                px=round(mr*mx)+cx
                py=round(mr*my)+cy
                try:
                    pixel=imgdata[px,py]
                except:
                    pixel=0
                destmap[x,(self.PIXELS-y)-1]=pixel
        return img

    @staticmethod
    def getbwimage(img:Image.Image) -> Image.Image:
        """ Convert image to dithered bitmap """
        return img.convert(mode="1")

    def buildimage(self,filename:str,colour:Colour=Colour.white,inverted:bool=False):
        """ Build a list of columns for creating a usbfan Message, from an image file """
        graphic = Image.open(filename)
        return self.buildimagefromimage(graphic,colour,inverted)

    def buildimagefromimage(self,graphic:Image.Image,colour:Colour=Colour.white,inverted:bool=False):
        """ Build a list of columns for creating a usbfan Message """
        img = Image.new('RGB', (Message.MAX_COLUMNS, Column.PIXELS))
        img.paste(graphic,(0,0))
        img = img.transpose(Image.TRANSPOSE)

        # Convert the image into one channel
        if inverted:
            img_data = [True if p < 128 else False for p in
                        img.convert('L').getdata(0)]
        else:
            img_data = [True if p >= 128 else False for p in
                        img.convert('L').getdata(0)]

        # Convert the image into its columns
        columns = [Column(img_data[i:i+Column.PIXELS], colour) for i in
                   range(0, len(img_data), Column.PIXELS)]

        return columns

    def makemessage(self,image:Union[str,Image.Image],
                    colour:Colour=Colour.white,
                    openmode:OpenTransition=OpenTransition.LeftRight,
                    messagemode:MessageStyle=MessageStyle.Clockwise,
                    closemode:CloseTransition=CloseTransition.RightLeft,
                    inverted:bool = False)->Message:
        """ Create a usbfan Message. image can be a filename or a PIL.Image """
        if isinstance(image,str):
            image=Image.open(image)
        return Message(self.buildimagefromimage(image,colour,inverted),
                       messagemode,openmode,closemode)

    def runprogram(self,filename:str,colour:Colour, inverted:bool,
                   openmode:OpenTransition, displaymode:MessageStyle, closemode:CloseTransition):
        """ Program a usbfan device with a suitably formatted bitmap """
        m1=self.makemessage(filename,colour,openmode,displaymode,closemode,inverted)
        p = Program((m1,))
        d = Device()
        d.program(p)

    def runscript(self,filename, defaults):
        """
        script format: filename colour inverted open display close
        Arguments left blank or with (-) will use defaults or command line values.
        # = comments
        """
        if defaults is None:
            defaults=argparse.Namespace()
            defaults.inverted=False
            defaults.open=OpenTransition.LeftRight
            defaults.close=CloseTransition.RightLeft
            defaults.display=MessageStyle.Anticlockwise
            defaults.colour=Colour.white
        messages=[]
        with open(filename,"r") as f:
            for line in f:
                line=line.strip()
                if line=="" or line.startswith("#"):
                    continue
                msg={}
                msg["filename"]=""
                msg["inverted"]=defaults.inverted
                msg["colour"]=defaults.colour
                msg["open"]=defaults.open
                msg["close"]=defaults.close
                msg["display"]=defaults.display
                args=line.split()
                msg["filename"]=args[0]
                if (len(args)>1 and args[1]!="-"): msg["colour"]=self.parseColour(args[1])
                if (len(args)>2 and args[2]!="-"): msg["inverted"]=self.parseBool(args[2])
                if (len(args)>3 and args[3]!="-"): msg["open"]=self.parseOpen(args[3])
                if (len(args)>4 and args[4]!="-"): msg["display"]=self.parseDisplay(args[4])
                if (len(args)>5 and args[5]!="-"): msg["close"]=self.parseClose(args[5])
                print("Building message: ",msg)
                messages.append(self.makemessage(msg["filename"],msg["colour"],
                                                 msg["open"],msg["display"],msg["close"],
                                                 msg["inverted"]))
        p = Program(messages)
        d = Device()
        d.program(p)

    def example1(self):
        """ Example use """
        src="triangle.png"
        dst="testcvt6.png"
        pc=PovConvert()
        pc.OFFSET=180
        img=Image.open(src).resize((79,79),Image.BICUBIC)
        img=pc.getbwimage(img)
        img.save("tmp.png")
        img=pc.transformimage(img)
        img.save(dst)
        #pc.cvtimage(src,dst)
        print("Saved as ",dst)
        m4 = pc.makemessage(dst,Colour.cyan,OpenTransition.All,MessageStyle.Remain,
                            CloseTransition.UpDown,False)

        p = Program((m4,))
        d = Device()
        d.program(p)

    def parseBool(self,value):
        """ Sensibly handle possible boolean values in script """
        if value=="": return False
        if value.lower()[:1] in ('f','n','-'): return False
        if value=="0": return False
        return True

    def parseEnum(self,enum,value):
        """ Case insenstive conversion of str to enum."""
        key=value.strip().lower()
        for k,v in enum.__members__.items():
            if k.lower()==key:
                return v
        msg = "%s is not a valid %s. Available values are: %s " % \
        (value,enum.__name__,",".join(enum.__members__.keys()))
        raise argparse.ArgumentTypeError(msg)

    def parseColour(self,s):
        """ Convert string to Colour enum"""
        return self.parseEnum(Colour,s)

    def parseOpen(self,s):
        """ Convert string to OpenTransition enum"""
        return self.parseEnum(OpenTransition,s)

    def parseClose(self,s):
        """ Convert string to CloseTransition enum"""
        return self.parseEnum(CloseTransition,s)

    def parseDisplay(self,s):
        """ Convert string to MessageStyle enum"""
        return self.parseEnum(MessageStyle,s)

    def parsearguments(self,args=None):
        """ Process command line arguments"""
        parser = argparse.ArgumentParser(description='POV Image Handler')
        parser.add_argument("--action",choices=["load","convert","run","script"],default="load",
                            help="load = send image to display, "+
                            "convert = create displayable image, "+
                            "run = convert then load,"+
                            "script = infile is a text file with a list of files "+
                            "to load as one sequence.")
        parser.add_argument("--colour",default="white",type=self.parseColour,
                            help=",".join(Colour.__members__.keys()))
        parser.add_argument("--inverted",action="store_true",
                            help="Invert pixel colours from black to white")
        parser.add_argument("--open",type=self.parseOpen,default="LeftRight",
                            help=",".join(OpenTransition.__members__.keys()))
        parser.add_argument("--close",type=self.parseClose,default="RightLeft",
                            help=",".join(CloseTransition.__members__.keys()))
        parser.add_argument("--display",type=self.parseDisplay,default="Clockwise",
                            help=",".join(MessageStyle.__members__.keys()))
        parser.add_argument("--rotate",type=int,default=0,help="Rotate image on convert (degrees)")
        parser.add_argument("--scale",type=float, default=1.0,help="Scale image 1.0=normal")
        parser.add_argument("infile")
        parser.add_argument("outfile",nargs="?")
        parsed=parser.parse_args(args)
        print(parsed)
        if parsed.action in ("convert","run"):
            if parsed.outfile is None:
                print("Need to declare outfile")
                return
            if parsed.outfile==parsed.infile:
                print("Outfile needs to be different from infile")
                return
            image=Image.open(parsed.infile)
            self.OFFSET=parsed.rotate
            dest=self.transformimage(image,parsed.scale)
            dest.save(parsed.outfile)
            print("Saved to "+parsed.outfile)

        if parsed.action in "load":
            print("Loading "+parsed.infile)
            self.runprogram(parsed.infile,parsed.colour,parsed.inverted,
                            parsed.open,parsed.display,parsed.close)

        if parsed.action in "run":
            print("Loading "+parsed.outfile)
            self.runprogram(parsed.outfile,parsed.colour,parsed.inverted,
                            parsed.open,parsed.display,parsed.close)

        if parsed.action=="script":
            self.runscript(parsed.infile,parsed)


if __name__ == "__main__":
    povc=PovConvert()
    povc.parsearguments()
    #pc.parsearguments(["--action=load","--colour=blue","--open=CLockwise","testcvt6.png"])
