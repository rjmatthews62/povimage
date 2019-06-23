from PIL import Image, ImageDraw
from usbfan import Colour, Column, Device, Message, Program, OpenTransition,CloseTransition,MessageStyle

import math

class PovConvert:
    OUTER_DIAMETER=160
    INNER_DIAMETER=80
    PIXELS=11
    XRESOLUTION=160
    GAP=16


    def cvtimage(self, filename:str, destination:str):
        graphic=Image.open(filename);
        result=self.transformimage(graphic)
        result.save(destination,"PNG")
        
    def transformimage(self,graphic:Image):
        img = Image.new('RGB', (self.XRESOLUTION-self.GAP, self.PIXELS))
        w,h = graphic.size
        cx=w//2
        cy=h//2
        radius=min(cx,cy)
        ratio=(self.OUTER_DIAMETER-self.INNER_DIAMETER)/self.PIXELS
        imgdata=graphic.load()
        destmap=img.load()
        for x in range(self.XRESOLUTION-self.GAP):
                angle=math.radians(x*360/self.XRESOLUTION)
                mx=math.cos(angle)
                my=math.sin(angle)
                for y in range(self.PIXELS):
                        ny=(y*ratio)+self.INNER_DIAMETER
                        mr=ny * radius/self.OUTER_DIAMETER
                        px=round(mr*mx)+cx
                        py=round(mr*my)+cy
                        pixel=imgdata[px,py]
                        destmap[x,(self.PIXELS-y)-1]=pixel
        return img

    def buildimage(self,filename:str,colour:Colour=Colour.white,inverted:bool=False):
        img = Image.new('RGB', (Message.MAX_COLUMNS, Column.PIXELS))
        graphic = Image.open(filename)
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
        
    def makemessage(self,imagename:str, 
        colour:Colour,
        openmode:OpenTransition,
        messagemode:MessageStyle,
        closemode:CloseTransition,
        inverted:bool = False):
        return Message(self.buildimage(imagename,colour,inverted),
                   messagemode,openmode,closemode)


if __name__ == "__main__":
    src="testcircle1.png"
    dst="testcvt1.png"
    pc=PovConvert()
    pc.cvtimage(src,dst)
    print("Saved as ",dst)
    m4 = pc.makemessage(dst,Colour.cyan,OpenTransition.Clockwise,MessageStyle.Clockwise,CloseTransition.ToMiddle,False)

    p = Program((m4,))
    d = Device()
    d.program(p)

    