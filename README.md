# povimage
Handle image conversions for POV displays.

This is currently used with the usbfan library: 

pip install microwave-usbfan

## usage
```
usage: povconvert.py [-h] --action {load,convert,run,script} [--colour COLOUR]
                     [--inverted] [--open OPEN] [--close CLOSE]
                     [--display DISPLAY] [--rotate ROTATE]
                     infile [outfile]
```                     
### load                     
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
### convert
```
  --action="convert"    Convert an image into a file suitable for display, doing rotational transformations.
  --rotate ROTATE       Rotate image on convert (degrees)
  infile                File to convert
  outfile               Destination file.
```  
### run
```
  --action="run"       Convert then load converted image.
```
  
### script
```
  --action="script"    Translate infile as a script.
```

## Script Syntax
Up to 7 different images can be loaded into the standard usb fan. Use "script" to read a script file

```
# script format: filename colour inverted open display close
# Arguments left blank or with (-) will use defaults or command line values.
# = comments

wombatcvt.png blue true Clockwise Remain LeftRight
crosshairs.png red false - Flash -
```


