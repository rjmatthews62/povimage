import PIL
from PIL import Image

def exportimage(graphic):
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
            if (data[x,y]<128):
                v=v+(1<<y)
        result+=hex(v)+","
    print(result)


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

    
#img=Image.open("clockface.png")
#exportimage(img)
exportzigzag(160,32)

