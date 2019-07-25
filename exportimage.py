import PIL
from PIL import Image
from povconvert import PovConvert

def exportimage(graphic, inverted=False):
    """ Build a list of columns for creating a usbfan Message """
    img=graphic.convert("L");
    data=img.load()
    print(graphic.width,"x",graphic.height);
    result=""
    for x in range(graphic.width):
        v=0
        for y in range(graphic.height):
            if (y>=32):
                break
            bit = data[x,y]<128
            if (inverted): bit = not(bit)
            if (bit):
                v=v+(1<<y)
        result+=hex(v)+","
    print(result)


def transformimage(fromfile,tofile):
    pov=PovConvert()
    pov.OUTER_DIAMETER=30
    pov.INNER_DIAMETER=8
    pov.PIXELS=32
    pov.XRESOLUTION=160
    pov.GAP=0
    pov.cvtimage(fromfile,tofile)
    
    
def exportzigzag(width,height):
    result=""
    y=0
    desc = False
    for x in range(width):
        v=(1<<y)
        if desc:
            y-=1
            if y<=0:
                desc=False
        else:
            y+=1
            if (y>=height-1):
                desc=True
        result+=hex(v)+","
    print(result)

    
transformimage("wombat.png","wombat160x32.png")
img=Image.open("wombat160x32.png")
exportimage(img,inverted=False)


