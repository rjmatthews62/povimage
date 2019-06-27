# povimage
Handle image conversions for POV displays.

This is currently used with the usbfan library: 

pip install microwave-usbfan

## usage ##
```
usage: povconvert.py [-h] --action {load,convert,run,script} [--colour COLOUR]
                     [--inverted] [--open OPEN] [--close CLOSE]
                     [--display DISPLAY] [--rotate ROTATE]
                     infile [outfile]
```                     
### load ###
```
  --action="load"       load raw image into display. Expected to be 144x11 
  --colour COLOUR       red,blue,green,magenta,yellow,cyan,white
  --inverted            Invert pixel colours from black to white
  --open OPEN           LeftRight,RightLeft,UpDown,DownUp,FromMiddle,ToMiddle,
                        All,Anticlockwise,Clockwise
  --close CLOSE         RightLeft,LeftRight,DownUp,UpDown,ToMiddle,FromMiddle,
                        All,Clockwise,Anticlockwise
  --display DISPLAY     Anticlockwise,Clockwise,Flash,Remain
  infile               Name of image to display
```  
### convert ###
```
  --action="convert"    Convert an image into a file suitable for display, doing rotational transformations.
  --rotate ROTATE       Rotate image on convert (degrees)
  infile                File to convert
  outfile               Destination file.
```  
### run ###
```
  --action="run"       Convert then load converted image.
```
  
### script ###
```
  --action="script"    Translate infile as a script.
```

## Script Syntax ##
Up to 7 different images can be loaded into the standard usb fan. Use "script" to read a script file

```
# script format: filename colour inverted open display close
# Arguments left blank or with (-) will use defaults or command line values.
# = comments

wombatcvt.png blue true Clockwise Remain LeftRight
crosshairs.png red false - Flash -
```

# PovDispay #
povdisplay is a simple tkInter GUI application that allows viewing, converting and editing pov bitmap images.

```
py povdisplay.py
```

### Use ###
* Open - open a pov bitmap file (144x11) and display it as it would appear on the usbfan
* Inverted - if checked, will display black on colour instead of vice versa
* colour - select display colour
* dither - dither original image to get some sort of shading
* Convert - Load an image file and convert to a pov bitmap file
* rotate - slider to rotate the converted image. Mostly useful for working around the gap.
* scale - slider to scale the converted image.
* square - if ticked, will transform the image to a square before converting.
* Save - save the converted or edited pov image

You can also draw on the display image using the left and right mouse buttons: left will draw the colour, right will draw black.


