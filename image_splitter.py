# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 15:08:31 2018

@author: soldier
"""
import os
import cv2

def split_one_image(dir_img, dir_res, current_img, nb_col, nb_row, create_subfolder=True):
    if not os.path.exists(dir_img + "/" + current_img):
        raise Exception("Image not found !",dir_img + "/" + current_img)
        
    #Extract name of image, extension, col/row and create dir if needed to save results
    name = current_img.split(".")[0]
    extension = current_img.split(".")[-1]
    if "-" in dir_img:
        nb_col=int(dir_res.split("-")[1])
        nb_row=int(dir_res.split("-")[2])
    if "-" in current_img:
        nb_col=int(current_img.split("-")[1])
        nb_row=int(current_img.split("-")[2].split(".")[0].split(" ")[0])
    
    if create_subfolder:
        dir_res = dir_res+"/"+name
    if not os.path.exists(dir_res):
        os.mkdir(dir_res)
    
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
            cv2.imwrite(dir_res+"/"+name+"_col-"+str(i)+"_row-"+str(j)+"."+extension, copy)
            
    print("Finished !")

def split_all_folder(dir_img, dir_res, current_img, nb_col, nb_row, create_subfolder=False):
    dir_res = dir_res + "/" + dir_img.split("/")[-1]
    for img in os.listdir(dir_img):
        current_img = img
        split_one_image(dir_img, dir_res, current_img, nb_col, nb_row, create_subfolder=create_subfolder)

########
dir_img = "image/minirogue-3-3"
dir_res = "results"

########
#Name of image should be "name of game without . and -" + "-" + nb columns + "-" + nb rows + extension
current_img = "minirogue.png"

#default if not in name or in folder name
nb_row = 7
nb_col = 10

###################
### ONE IMAGE SPLIT
#split_one_image(dir_img, dir_res, current_img, nb_col, nb_row, create_subfolder=True)
    
####################
### SPLIT ALL FOLDER
split_all_folder(dir_img, dir_res, current_img, nb_col, nb_row, create_subfolder=False)