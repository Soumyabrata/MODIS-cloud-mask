# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 12:14:15 2015

@author: SHILPA005
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Apr 10 17:13:55 2015

@author: SHILPA005
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 14:09:31 2015

@author: SHILPA005
"""

#!/usr/bin/env ipython3
"""
   Perform an operation on a whole database, crawling through subfolders. This
   is a skeleton, it does nothing.
"""

"""
+   Perform an operation on a whole database, crawling through subfolders. This
+   is a skeleton, it does nothing.
+"""

import glob
from utility import *
from PrecipitableWaterProduct import PrecipitableWaterProduct
import numpy as np

products = ['05']
satellites = ['MOD']
extension = '.hdf'


roi_size = 50

location = [1.342541, 103.681085] ## Singapore
#location = [50.3641667, 30.4966667] ### Ukraine
#location = [13.7358333, 100.5338889]  ## for Thailand
#location = [30.5313889,114.3572222]  ## for Wuhaan
#location = [31.8238889,130.5994444] # for Japan
#location = [40.2452778,116.2238889] # for Beijing
sel = 3# Save a 3-by-3 box around the selected point

#mask_path = 'data/data-*' 
mask_path = 'data/data-2015-*-*' 
days = []
one_month = []
for day in glob.glob(mask_path):
    for satellite in satellites:
        s1 = day + '/' + satellite
        for product in products:
            s2 = s1 + product + '*' + extension
            for files in glob.glob(s2):
                try:
                    print('Processing File: ', files)
                    seed = '-'.join(files.split('.')[1:3])
                    
                    precipitableWaterProduct = PrecipitableWaterProduct(files, location[0], location[1], roi_size)
                    georef = precipitableWaterProduct.georef_grid1k
                    data = precipitableWaterProduct.extractCloudMaskQA_QualityFlag()
                
                    grid_location = closest_point(georef, location)
                    # Subsample data
                    data = data[grid_location[0]-sel//2 : grid_location[0]+sel//2+1 ,
                                grid_location[1]-sel//2 : grid_location[1]+sel//2+1 ]
                    #georef = georef[grid_location[0]-sel//2 : grid_location[0]+sel//2+1 
                                    #grid_location[1]-sel//2 : grid_location[1]+sel//2+1, : ]
                    #data = np.reshape(data,(5,5))
                    print(data)
                except:
                    print('ERROR:', files)
                else:
                    one_month.append(data)
                    #print(data)
#                    save_as_mat('georef-' + seed, georef)
                    #save_as_mat('MOD' + seed, data)
                    
                    #save_as_mat('Feb_2013', one_month)                    
                    save_as_mat('MOD_CloudMask-' + seed,data)
#save_as_mat('mask',one_month)
