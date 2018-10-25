# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 20:00:51 2018

@author: lambe
"""

import numpy as np
import cv2

#300 DPI
page_width = 2480
page_height = 3508

#Create empty page
img = np.zeros((page_height,page_width,4),np.uint8)
img[:,:,3] = 255
img[:,:,1] = 255
cv2.imwrite("image.png",img)