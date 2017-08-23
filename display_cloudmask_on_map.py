# -*- coding: utf-8 -*-
"""
Created on Wed Oct 07 13:02:44 2015

@author: SHILPA005
"""

# -*- coding: utf-8 -*-


#/usr/bin ipython3

"""
   This file is an example on how to use this modis framework. I provides various useful code snippets.
"""
from matplotlib.pyplot import imshow
import numpy as np
from utility import *

# The three classes corresponding to the products.
from PrecipitableWaterProduct import PrecipitableWaterProduct


# Parameters
location = [1.3483, 103.6831]     # Lat/Lon
roi_size = 50                     # km
date = '2015-12-25'                  # Format YYYY-MM-DD. WARNING: if month or day is in one number, i.e 3, put 3, not 03.
satellite = 'MYD'                   # Choices 'MYD' or 'MOD'
product = '05'                      # Choices '35', 'O6' or '05'


path_to_file = findProductPath(date, satellite, product, indice=0)
print(path_to_file)
# Remplace by the product you want to use. Once this stage is done, you have
# created an object containing the file. You can now use the method associated with
# this object.
precipitableWaterProduct = PrecipitableWaterProduct(path_to_file, location[0], location[1], roi_size)

# CM: Cloud Mask

CM = precipitableWaterProduct.extractCloudMaskQA_QualityFlag()
georef = precipitableWaterProduct.georef_grid1k

grid_location = closest_point(georef, location)

print("Center is: ", grid_location, 
      ", Value at center is: ", CM[grid_location[0], grid_location[1]])
      
CM_subsample = CM[grid_location[0]-1: grid_location[0]+2,
                    grid_location[1]-1: grid_location[1]+2 ]
                    
precipitableWaterProduct.dispayOnMap('CM_subsample')
