from PIL import Image, ImageDraw
from usbfan import Colour, Column, Device, Message, Program, OpenTransition,CloseTransition,MessageStyle
from typing import Union,Any
import math
import argparse

class PovConvert:
    OUTER_DIAMETER=160
    INNER_DIAMETER=80
    PIXELS=11
    XRESOLUTION=160
    GAP=16
    OFFSET=0


    def cvtimage(self, filename:str, destination:str):
        graphic=Image.open(filename);
        result=self.transformimage(graphic)
        result.save(destination,"PNG")
        
    def transformimage(self,graphic:Image):
        img = Image.new("L", (self.XRESOLUTION-self.GAP, self.PIXELS))
        w,h = graphic.size
        cx=w//2
        cy=h//2
        radius=min(cx,cy)
        ratio=(self.OUTER_DIAMETER-self.INNER_DIAMETER)/self.PIXELS
        rpixels=max(1,math.floor(ratio))
        imgdata=graphic.convert("L").load(); # Convert to levels.
        destmap=img.load()
        for x in range(self.XRESOLUTION-self.GAP):
                angle=math.radians(x*360/self.XRESOLUTION+self.OFFSET)
                mx=math.cos(angle)
                my=math.sin(angle)
                for y in range(self.PIXELS):
                        ny=(y*ratio)+self.INNER_DIAMETER
                        mr=ny * radius/self.OUTER_DIAMETER
                        pixel=0
                        cnt=0
                        px=round(mr*mx)+cx
                        py=round(mr*my)+cy
                        pixel=imgdata[px,py]
                        destmap[x,(self.PIXELS-y)-1]=pixel
        return img

    def getbwimage(self,img:Image) -> Image:
        return img.convert(mode="1")

    def buildimage(self,filename:str,colour:Colour=Colour.white,inverted:bool=False):
        graphic = Image.open(filename)
        return self.buildimagefromimage(graphic,colour,inverted)

    def buildimagefromimage(self,graphic:Image,colour:Colour=Colour.white,inverted:bool=False):
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
        colour:Colour,
        openmode:OpenTransition,
        messagemode:MessageStyle,
        closemode:CloseTransition,
        inverted:bool = False):
        if (isinstance(image,str)):
            image=Image.open(image)
        return Message(self.buildimagefromimage(image,colour,inverted),
                   messagemode,openmode,closemode)

    def runprogram(self,filename:str,colour:Colour, inverted:bool, openmode:OpenTransition, displaymode:MessageStyle, closemode:CloseTransition):
        m1=self.makemessage(filename,colour,openmode,displaymode,closemode,inverted)
        p = Program((m1,))
        d = Device()
        d.program(p)

    def example1(self):
        src="triangle.png"
        dst="testcvt6.png"
        pc=PovConvert()
        pc.OFFSET=180
        img=Image.open(src).resize((79,79),Image.BICUBIC)
        img=pc.getbwimage(img)
        img.save("tmp.png")
        img=pc.transformimage(img)
        img.save(dst);
        #pc.cvtimage(src,dst)
        print("Saved as ",dst)
        m4 = pc.makemessage(dst,Colour.cyan,OpenTransition.All,MessageStyle.Remain,CloseTransition.UpDown,False)

        p = Program((m4,))
        d = Device()
        d.program(p)

    def parseEnum(self,enum,value):
        key=value.strip().lower()
        for k,v in enum.__members__.items():
            if (k.lower()==key):
                return v
        msg = "%s is not a valid %s. Available values are: %s " % (value,enum.__name__,",".join(enum.__members__.keys()))
        raise argparse.ArgumentTypeError(msg)            
        
    def parseColour(self,s):
        return self.parseEnum(Colour,s)

    def parseOpen(self,s):
        return self.parseEnum(OpenTransition,s)

    def parseClose(self,s):
        return self.parseEnum(CloseTransition,s)

    def parseDisplay(self,s):
        return self.parseEnum(MessageStyle,s)
        
    def parsearguments(self,args=None):
        parser = argparse.ArgumentParser(description='POV Image Handler')
        parser.add_argument("--action",choices=["load","convert","run"],required=True,
                            help="load = send image to display, convert = create displayable image,run = convert then load")
        parser.add_argument("--colour",default="white",type=self.parseColour,help=",".join(Colour.__members__.keys()))
        parser.add_argument("--inverted",action="store_true",help="Invert pixel colours from black to white")
        parser.add_argument("--open",type=self.parseOpen,default="LeftRight",help=",".join(OpenTransition.__members__.keys()))
        parser.add_argument("--close",type=self.parseClose,default="RightLeft",help=",".join(CloseTransition.__members__.keys()))
        parser.add_argument("--display",type=self.parseDisplay,default="Clockwise",help=",".join(MessageStyle.__members__.keys()))
        parser.add_argument("--rotate",type=int,default=0,help="Rotate image on convert (degrees)")
        parser.add_argument("infile")
        parser.add_argument("outfile",nargs="?")
        parsed=parser.parse_args(args)
        print(parsed)
        if parsed.action in ("convert","run"):
            if (parsed.outfile==None):
                print("Need to declare outfile")
                return
            if (parsed.outfile==parsed.infile):
                print("Outfile needs to be different from infile")
                return
            image=Image.open(parsed.infile)
            self.OFFSET=parsed.rotate
            dest=self.transformimage(image)
            dest.save(parsed.outfile)
            print("Saved to "+parsed.outfile)

        if (parsed.action in ("load")):
            print("Loading "+parsed.infile)
            self.runprogram(parsed.infile,parsed.colour,parsed.inverted,parsed.open,parsed.display,parsed.close)

        if (parsed.action in ("run")):
            print("Loading "+parsed.outfile)
            self.runprogram(parsed.outfile,parsed.colour,parsed.inverted,parsed.open,parsed.display,parsed.close)

        
if __name__ == "__main__":
    pc=PovConvert()
    pc.parsearguments()
    #pc.parsearguments(["--action=load","--colour=blue","--open=CLockwise","testcvt6.png"])
