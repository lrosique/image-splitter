# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 23:14:40 2018

@author: soldier
"""

import tkinter 
from PIL import Image, ImageTk

max_width = 500
max_height = 500

root = tkinter.Tk()
im = Image.open("image/minirogue-3-3/minirogue-3-3_col-0_row-0.jpg")
width, height = im.size

factor = 1.0
if width > max_width:
    factor = width/max_width
if height > max_height:
    tmp_factor = height/max_height
    if tmp_factor > factor:
        factor = tmp_factor
        
new_width = int(width/factor)
new_height = int(height/factor)

im = im.resize((new_width, new_height), Image.ANTIALIAS)

tkimage = ImageTk.PhotoImage(im)
tkinter.Label(root, image=tkimage).pack() 

root.mainloop()