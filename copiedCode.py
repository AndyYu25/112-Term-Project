#File with all copied code/helper functions

#copied from https://www.diderot.one/course/34/chapters/2785/
def rgbString(red:int, green:int, blue:int)->str:  
    """returns hex values of colors combined in a string"""
    return "#%02x%02x%02x" % (red, green, blue)

#largely copied from https://www.diderot.one/course/34/chapters/2846/
def drawButton(canvas, cx, cy, w, h, onClick, text, color): 
    """Draws a button with the given parameters""" 
    textSize = int(h*0.225)
    canvas.create_rectangle(cx-w/2, cy-h/2, cx+w/2, cy+h/2, fill=color,  
                        onClick=onClick)  
    canvas.create_text(cx, cy, text=text, font = f'Arial {textSize}')