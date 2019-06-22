from usbfan import Colour, Column, Device, Message, Program, \
OpenTransition,CloseTransition,MessageStyle
from PIL import Image, ImageDraw

def buildimage(filename:str,colour:Colour=Colour.white,inverted:bool=False):
        img = Image.new('RGB', (Message.MAX_COLUMNS, Column.PIXELS))
        graphic = Image.open(filename)
        img.paste(graphic,(0,0))
        # Convert the image into one channel
        img_data = [True if p >= 128 else False for p in
                    img.convert('L').getdata(0)]

        # Convert the image into its columns
        columns = [Column(img_data[i:i+Column.PIXELS], colour) for i in
                   range(0, len(img_data), Column.PIXELS)]

        return columns
        
def makemessage(imagename:str, 
        colour:Colour,inverted:bool,
        messagemode:MessageStyle,
        closemode:CloseTransition,
        inverted:bool = False):
    return Message(buildimage(imagename,color,inverted),
                   messagemode,openmode,closemode)
                   
m0 = makemessage("floral.png",Colour.blue,OpenTransition.DownUp,MessageStyle.Anticlockwise,CloseTransition.UpDown)
m1 = makemessage("clockface.png",Colour.red,OpenTransition.DownUp,MessageStyle.Flash,CloseTransition.DownUp)
m2 = makemessage("pattern.png",Colour.white,OpenTransition.Clockwise,MessageStyle.Flash,CloseTransition.FromMiddle)
m3 = makemessage("clockface.png",Colour.yellow,OpenTransition.Clockwise,MessageStyle.Clockwise,CloseTransition.ToMiddle,True)

p = Program((m0,m1,m2,m3))
#p = Program((m3,))

# Open the device and program
d = Device()
d.program(p)
