# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 15:08:31 2018

@author: soldier
"""
import os
import cv2

########
#Name of image should be "name of game without . and -" + "-" + nb columns + "-" + nb rows + extension
current_img = "secrethitler-4-3.jpg"
########
dir_img = "image"
#default if not in name
nb_row = 7
nb_col = 10

#Extract name of image, extension, col/row and create dir if needed to save results
name = current_img.split(".")[0]
extension = current_img.split(".")[-1]
if "-" in current_img:
    nb_col=int(current_img.split("-")[1])
    nb_row=int(current_img.split("-")[2].split(".")[0])
    
if not os.path.exists(dir_img+"/"+name):
    os.mkdir(dir_img+"/"+name)

#Load image and calculate splits sizes
img = cv2.imread(dir_img + "/" + current_img)
height, width, channels = img.shape
small_height = height//nb_row
small_width = width//nb_col
#Loop to create the new images
for i in range(nb_col):
    for j in range(nb_row):
        #Copy source image
        copy = img.copy()
        #Calculate position of the small image to cut
        y_min = j*small_height
        y_max = (j+1)*small_height
        x_min = i*small_width
        x_max = (i+1)*small_width
        #Cut
        copy = copy[y_min:y_max,x_min:x_max,:]
        #Save result
        cv2.imwrite(dir_img+"/"+name+"/"+name+"_col-"+str(i)+"_row-"+str(j)+"."+extension, copy)
        
print("Finished !")