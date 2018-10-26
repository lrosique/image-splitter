# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 20:00:51 2018

@author: lambe
"""
import os
import numpy as np
import cv2
from PIL import Image
import copy

#300 DPI
page_size = 2480,3508       #210mm x 297mm (A4 width x height)
margins = 100,100           #1mm = 59.04 (left/right x top/bottom)
ecart = 2                   #A l'origine : 2.835

#calculate_cards_per_page(card_size=tarot)
#TAROT
tarot = 827,1418           #70mm x120mm (widthxheight) #ratio:1.7146 #max_cards:4
#POKER
poker = 750,1050           #63.5mm x88.9mm (widthxheight) #ratio:1.4 #max_cards:9
#BRIDGE
bridge = 662,1050          #56mm x88.9mm (widthxheight) #ratio:1.5861 #max_cards:9
#CURRENT CARDS
mycards = 650,1004         #Dans AI : 241,156 #ratio = 1.5446 #max_cards:10

#MAX_SIZE
#best_card_size_for_maxXcards(15,wanted_ratio=1.5446)
#calculate_card_size(3,5)
#For 9 cards per page
cmax9cards = 713,1101       #max:759,1101 with ratio:1.45 ##loss:46 #order:3x3
#For 10 cards per page
cmax10cards = 1020,660      #max:1139,660 with ratio:1.7257 ##loss:119 #order:2x5
#For 12 cards per page
cmax12cards = 569,878       #max:569,1100 with ratio:1.93 ##loss:224 #order:4x3
#For 15 cards per page
cmax15cards = 569,878       #max:758,660 with ratio:1.15 ##loss:169 #order:3x5

#SQUARE
#best_card_size_for_maxXcards(9,wanted_ratio=1)
#calculate_card_size(3,5)
smax2cards = 1139,1139       #loss:2169 #order:2x1
smax3cards = 758,758         #loss:2549 #order:3x1
smax4cards = 1139,1139       #loss:514 #order:2x2
smax6cards = 1101,1101       #loss:37 #order:2x3
smax8cards = 825,825         #loss:313 #order:2x4
smax9cards = 758,758         #loss:343 #order:3x3

#Create empty page
def initialize_new_page():
    img = np.zeros((page_size[1],page_size[0],4),np.uint8)
    img[:,:,:] = 255 #white
    #img[:,:,3] = 255 #black
    return img

#Save planche at 300dpi
def save_img(img, path="image/planche.png"):
    cv2.imwrite(path,img)
    im = Image.open(path)
    im.save(path, dpi=(300,300))

def rotate_image(img,symmetry=False):
    if symmetry:
        return img.swapaxes(1,0)[:,::-1,:]
    else:
        return img.swapaxes(1,0)[::-1,:,:]

#Load an image from disk and resize it to prefered size
def load_resize_img(path,wanted_size=mycards,symmetry=False):
    if not os.path.exists(path):
        raise Exception("Image not found !",path)
    img = cv2.imread(path)
    h,w,d = img.shape
    if (wanted_size[0] > wanted_size[1] and w < h) or (wanted_size[0] < wanted_size[1] and w > h):
        img = rotate_image(img,symmetry=symmetry)
    img = cv2.resize(img,wanted_size)
    return img

#Add the image to the page at (x,z)
def include_img_in_page(i,p,x,z):
    hi,wi,di = i.shape
    hp,wp,dp = p.shape
    max_x = wi + x
    max_z = hi + z
    if max_x > wp or max_z > hp or di > dp:
        raise Exception("L'image à insérer est trop grande !")
    else:
        p[z:max_z,x:max_x,0:di]=i
        return p

#Calculate the width/height of the card to best fill X columns and Y rows of page
def calculate_card_size(nb_col,nb_row, wanted_ratio=None):    
    max_width = page_size[0] - 2*margins[0]
    max_height = page_size[1] - 2*margins[1]
    card_max_width = max_width/nb_col - (nb_col-1)*ecart/nb_col
    card_max_height = max_height/nb_row - (nb_row-1)*ecart/nb_row
    ratio = card_max_width/card_max_height if card_max_width > card_max_height else card_max_height/card_max_width
    loss = (0,0)
    if card_max_width > card_max_height and wanted_ratio is not None:
        if ratio < wanted_ratio:
            loss = (0,card_max_height)
            card_max_height = card_max_height/wanted_ratio*ratio
            loss = (0,loss[1]-card_max_height)
        elif ratio > wanted_ratio:
            loss = (card_max_width,0)
            card_max_width = card_max_width*wanted_ratio/ratio
            loss = (loss[0]-card_max_width,0)
        ratio = card_max_width/card_max_height if card_max_width > card_max_height else card_max_height/card_max_width
    elif card_max_width < card_max_height and wanted_ratio is not None:
        if ratio > wanted_ratio:
            loss = (0,card_max_height)
            card_max_height = card_max_height*wanted_ratio/ratio
            loss = (0,loss[1]-card_max_height)
        elif ratio < wanted_ratio:
            loss = (card_max_width,0)
            card_max_width = card_max_width/wanted_ratio*ratio
            loss = (loss[0]-card_max_width,0)
        ratio = card_max_width/card_max_height if card_max_width > card_max_height else card_max_height/card_max_width
    return (card_max_width, card_max_height), ratio, loss

def divisorGenerator(n):
    divisors = []
    for i in range(1,int(n/2)+1):
        if n%i == 0:
            divisors.append(i)
    return divisors

def best_card_size_for_maxXcards(maxXcards,wanted_ratio=None):
    best_card = None
    best_order = (0,0)
    for i in divisorGenerator(maxXcards):
        d = int(maxXcards/i)
        c = calculate_card_size(d,i,wanted_ratio=wanted_ratio)
        if best_card is None:
            best_card = c
            best_order = (d,i)
        elif best_card[2][0]+best_card[2][1] > c[2][0]+c[2][1]:
            best_card = c
            best_order = (d,i)
    return best_card, best_order

def calculate_cards_per_page_for_fixed_size(nb_cards,card_size):
    need_rotation = False
    for i in divisorGenerator(nb_cards):
        d = int(nb_cards/i)
        total_width = card_size[0]*d + (d-1)*ecart + 2*margins[0]
        total_height = card_size[1]*i + (i-1)*ecart + 2*margins[1]
        if total_width <= page_size[0] and total_height <= page_size[1]:
            return d,i,need_rotation
        
    card_size = (card_size[1],card_size[0])
    need_rotation = True
    for i in divisorGenerator(nb_cards):
        d = int(nb_cards/i)
        total_width = card_size[0]*d + (d-1)*ecart + 2*margins[0]
        total_height = card_size[1]*i + (i-1)*ecart + 2*margins[1]
        if total_width <= page_size[0] and total_height <= page_size[1]:
            return d,i,need_rotation
    raise Exception("Impossible to get that many cards for this size ! Sorry !")

def calculate_cards_per_page(card_size=mycards):
    w,h = card_size
    max_width = page_size[0] - 2*margins[0]
    max_height = page_size[1] - 2*margins[1]
    hl_w = int(max_width/w)
    hl_h = int(max_height/h)
    nb_cards_horizontal_layout = hl_w*hl_h
    vl_w = int(max_height/w)
    vl_h = int(max_width/h)
    nb_cards_vertical_layout = vl_w*vl_h
    need_rotation = False
    if nb_cards_horizontal_layout >= nb_cards_vertical_layout:
        return hl_h,hl_w,need_rotation
    else:
        need_rotation = True
        return vl_h, vl_w,need_rotation

def map_tuple_gen(func, tup):
    return tuple(func(itup) for itup in tup)

def pixels_to_cm(pi):
    return pi*210/2480/10
    
def cm_to_pixels(cm):
    return cm*10*2480/210

def calculate_x_z_positions_page(nb_col,nb_row,card_size=mycards):
    dist_marg_left = page_size[0] - margins[0]*2 - card_size[0]*nb_col - ecart*(nb_col - 1)
    dist_marg_left = int(dist_marg_left/2)
    dist_marg_top = page_size[1] - margins[1]*2 - card_size[1]*nb_row - ecart*(nb_row - 1)
    dist_marg_top = int(dist_marg_top/2)
    x = [margins[0] + dist_marg_left + card_size[0]*i + ecart*i for i in range(nb_col)]
    z = [margins[1] + dist_marg_top + card_size[1]*i + ecart*i for i in range(nb_row)]
    return x, z

def fill_page_with_cards(p,images,parameters, start_image=0):
    images = images[start_image:]
    card_size = parameters["card_size"]
    if parameters["type_generation"] == "apply_parameters":
        nb_col,nb_row,need_rotation=calculate_cards_per_page_for_fixed_size(parameters["nb_cards_per_page"],card_size)
        if need_rotation:
            card_size = (card_size[1],card_size[0])
    elif parameters["type_generation"] == "optimize_nb_for_cardsize":
        nb_col,nb_row,need_rotation=calculate_cards_per_page(card_size=card_size)
        if need_rotation:
            card_size = (card_size[1],card_size[0])
    elif parameters["type_generation"] == "optimize_cardsize_for_nb":
        cs,(nb_col,nb_row)=best_card_size_for_maxXcards(parameters["nb_cards_per_page"],wanted_ratio=parameters["wanted_ratio"])
        card_size = map_tuple_gen(int,cs[0])
    
    cpt = 0
    x,z = calculate_x_z_positions_page(nb_col,nb_row,card_size=card_size)
    for k in range(len(z)):
        for j in range(len(x)):
            if cpt >= len(images) and not parameters["repeat_image"]:
                break
            elif cpt >= len(images):
                cpt = 0
            i = load_resize_img(images[cpt],card_size,symmetry=parameters["symmetry"])
            horizontal_position = j
            if parameters["symmetry"]:
                horizontal_position = len(x)-j-1
            a = x[horizontal_position]
            b = z[k]
            p = include_img_in_page(i,p,a,b)
            cpt += 1
    if parameters["add_layout"]:
        p = add_grid_layout(x,z,p, color_layout=parameters["color_layout"])
    return p, nb_col*nb_row
        
def add_grid_layout(x,z,p,color_layout=(255,0,0)):
    for k in range(len(z)+1):
        zmin = 0
        zmax = page_size[0]-1
        if k == len(z):
            xmin = page_size[1]-z[0]-2
            xmax = page_size[1]-z[0]-1
        else:
            xmin = z[k]-2
            xmax = z[k]-1
        p[xmin:xmax,zmin:zmax,0:1] = color_layout[2] #blue -> triplet rgb
        p[xmin:xmax,zmin:zmax,1:2] = color_layout[1] #green -> triplet rgb
        p[xmin:xmax,zmin:zmax,2:3] = color_layout[0] #red -> triplet rgb
    for j in range(len(x)+1):
        xmin = 0
        xmax = page_size[1]-1
        if j == len(x):
            zmin = page_size[0]-x[0]-2
            zmax = page_size[0]-x[0]-1
        else:
            zmin = x[j]-2
            zmax = x[j]-1
        p[xmin:xmax,zmin:zmax,0:1] = color_layout[2] #blue -> triplet rgb
        p[xmin:xmax,zmin:zmax,1:2] = color_layout[1] #green -> triplet rgb
        p[xmin:xmax,zmin:zmax,2:3] = color_layout[0] #red -> triplet rgb
    return p

def generate_pages_with_images(parameters, images, verso=False):
    nb_cards_generated = 0
    cpt = 0
    if verso:
        params = copy.deepcopy(parameters)
        params["repeat_image"] = True
        params["symmetry"] = True
    else:
        params = parameters
    while nb_cards_generated < len(images):
        name = parameters["planche"].split(".")[0]+"_"+str(cpt)+"."+parameters["planche"].split(".")[1]
        p = initialize_new_page()
        p,nb = fill_page_with_cards(p,images,params,start_image=nb_cards_generated)  
        save_img(p,path=name)
        nb_cards_generated += nb
        cpt += 1
    return p

#Splits cards names depending on nb of recto/verso "recto1 (X).png and verso1 (X).png"
def get_all_images(folder):
    cartes_recto={}
    cartes_verso={}
    for name in os.listdir(folder):
        if name.startswith("recto"):
            numero_recto = name.split(" ")[0].split("recto")[1]
            if "." in numero_recto:
                numero_recto = numero_recto.split(".")[0]
            if numero_recto in cartes_recto:
                cartes_recto[numero_recto].append(folder+name)
            else:
                cartes_recto[numero_recto] = [folder+name]
        elif name.startswith("verso"):
            numero_verso = name.split(" ")[0].split("verso")[1]
            if "." in numero_verso:
                numero_verso = numero_verso.split(".")[0]
            if numero_verso in cartes_verso:
                cartes_verso[numero_verso].append(folder+name)
            else:
                cartes_verso[numero_verso] = [folder+name]
    return cartes_recto, cartes_verso

def generate_all_pages(parameters):
    cartes_recto, cartes_verso = get_all_images(parameters["folder_source_image"])
    planche = parameters["planche"].split(".")[0]
    extension = parameters["planche"].split(".")[1]
    for key, value in cartes_recto.items():
        images_recto = value
        images_verso = cartes_verso[key]
        #recto
        parameters["planche"] = planche + "_recto_" + str(key) + "." + extension
        generate_pages_with_images(parameters,images_recto)
        #verso
        parameters["planche"] = planche + "_verso_" + str(key) + "." + extension
        generate_pages_with_images(parameters,images_verso, verso=True)
        

#########################
parameters_default={
        "folder_source_image"   : "image/secrethitler-4-3/", #source
        "planche"               : "image/planche.png", #result
        
        #optimize_cardsize_for_nb #optimize_nb_for_cardsize #apply_parameters
        "type_generation"       : "optimize_nb_for_cardsize",
        "card_size"             : mycards,
        "nb_cards_per_page"     : 20, #used only if generate_at_fixed_size == False
        
        "repeat_image"          : False, #loop over images in folder to fill the page
        "symmetry"              : False, #for "verso", turn all images to the right instead of left
        
        "add_layout"            : True, #add the grid for printing
        "color_layout"          : (255,0,0), #red grid
        
        "wanted_ratio"          : 1.5446 #ratio width/height, used only if generate_at_fixed_size == False
        }
###
generate_all_pages(parameters_default)