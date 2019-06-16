from usbfan import Colour, Column, Device, Message, Program

def sawtooth(i):
    j=i % 22;
    if j>=11: return 21-j
    return j

# A generic "Message" is made up of 1 to 144 "Column" object
# A "Column" has 11 boolean pixels and a "Colour"
columns=[]
rainbow_colours = [Colour.red, Colour.yellow, Colour.green,
                   Colour.cyan, Colour.blue, Colour.magenta]

for i in range(144):
    col = [True] * 11;
    col[sawtooth(i)]=False;
    columns.append(Column(col, rainbow_colours[i % 6]))
msg=Message(columns)
msg.openmode=Message.OPEN_DOWN_UP
msg.middlemode=Message.MIDDLE_CLOCKWISE
msg.closemode=Message.CLOSE_UP_DOWN
p = Program((msg,))

# Open the device and program
d = Device()
d.program(p)
