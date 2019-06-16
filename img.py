from usbfan import Colour, Column, Device, Message, Program, \
OpenTransition,CloseTransition,MessageStyle
from PIL import Image, ImageDraw

def sawtooth(i):
    j=i % 22;
    if j>=11: return 21-j
    return j

def buildimage(filename,colour):
        img = Image.new('RGB', (Message.MAX_COLUMNS, Column.PIXELS))
        graphic = Image.open(filename)
        img.paste(graphic,(0,0))

        # Transpose the image
        img = img.transpose(Image.TRANSPOSE)

        # Convert the image into one channel
        img_data = [True if p >= 128 else False for p in
                    img.convert('L').getdata(0)]

        # Convert the image into its columns
        columns = [Column(img_data[i:i+Column.PIXELS], colour) for i in
                   range(0, len(img_data), Column.PIXELS)]

        return columns

def makemessage(imagename:str,color:Colour,
                openmode:OpenTransition,
                middlemode:MessageStyle,
                closemode:CloseTransition):
    return Message(buildimage(imagename,color),
                   middlemode,openmode,closemode)
                   
m0 = makemessage("floral.png",Colour.blue,OpenTransition.DownUp,MessageStyle.Anticlockwise,CloseTransition.UpDown)
m1 = makemessage("clockface.png",Colour.red,OpenTransition.DownUp,MessageStyle.Flash,CloseTransition.DownUp)
m2 = makemessage("pattern.png",Colour.white,OpenTransition.Clockwise,MessageStyle.Flash,CloseTransition.FromMiddle)

p = Program((m0,m1,m2))

# Open the device and program
d = Device()
d.program(p)
