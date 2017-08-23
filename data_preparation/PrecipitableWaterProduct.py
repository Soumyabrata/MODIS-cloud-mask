#!/usr/bin/env ipython3
import gdal
import numpy as np
from utility import *

# WARNING : There exist two versions of the products. For example, for the solar zenith it is:
 #('HDF4_SDS:UNKNOWN:"_data/data-2014-10-14/MOD05_L2.A2014287.0320.006.2015077151203.hdf":3',
  #'[406x270] Solar_Zenith (16-bit integer)'),
 #AND
  #('HDF4_EOS:EOS_SWATH:"_data/data-2014-10-14/MOD05_L2.A2014287.0320.006.2015077151203.hdf":mod05:Solar_Zenith',
  #'[406x270] Solar_Zenith mod05 (16-bit integer)'),
#I took the first one. I guess there are the same.


class PrecipitableWaterProduct:
    def __init__(self, filename, roi_lat = 1.342966, roi_long = 103.680594, roi_width_km = 100):
    #def __init__(self, filename, roi_lat = 30.5313889, roi_long = 114.3572222, roi_width_km = 100):
        self.filename = filename
        try:
            self.data_set = gdal.Open(filename)
            self.center = [roi_lat, roi_long]
            
            self.size5k = None
            self.georef_grid1k = None
        
            # Extract the georeferencing
            sub_lat_set = gdal.Open([sd for sd, descr in self.data_set.GetSubDatasets() if descr.endswith('Latitude (32-bit floating-point)')][0])
            sub_long_set = gdal.Open([sd for sd, descr in self.data_set.GetSubDatasets() if descr.endswith('Longitude (32-bit floating-point)')][0])
            self.georef_grid = np.dstack((sub_lat_set.ReadAsArray(), sub_long_set.ReadAsArray()))
            sub_lat_set = None
            sub_long_set = None
            self.size5k = []
            self.size1k = []
            
            # Definition of the roi to strip the data
            self.lrcrnX = 0          # Lower Right corner
            self.lrcrnY = 0
            self.ulcrnX = 0          # Upper Left corner
            self.ulcrnY = 0 
            self.geoSubSample(roi_lat, roi_long, roi_width_km)

        except:
            print("Error when reading file. Either file does not exist, or is not a valid MOD06 product")
            raise
        
    def geoSubSample(self, center_lat, center_long, width_km):
        assert width_km % 10 == 0, "The size of the roi must be a multiple of 10"
        
        center = np.array([center_lat, center_long])
        grid_center = closest_point(self.georef_grid, center)
        
        
        self.georef_grid = self.georef_grid[grid_center[0] - width_km/10 : grid_center[0] + width_km/10 + 1, \
                                            grid_center[1] - width_km/10 : grid_center[1] + width_km/10 + 1, :]
        grid_center = np.multiply(grid_center, 5)   # Coordinates to center the 1k dataset

        self.ulcrnX = grid_center[0] - width_km/2
        self.ulcrnY = grid_center[1] - width_km/2
        self.lrcrnX = grid_center[0] + width_km/2 + 1
        self.lrcrnY = grid_center[1] + width_km/2 + 1
        
        # Update size
        self.size5k = [self.georef_grid.shape[0], self.georef_grid.shape[1]]
        self.size1k = [width_km + 1, width_km + 1]
        # Update derived products
        self.__interpolateGeoreferencing()    
        
    def extractByName(self, description):
        try:
            sub_ds = gdal.Open([sd for sd, descr in self.data_set.GetSubDatasets() if descr.endswith(description)][0])
            return sub_ds.ReadAsArray()[self.ulcrnX:self.lrcrnX, self.ulcrnY:self.lrcrnY]
        except:
            print("Error while extracting product. Either file sub dataset does not exist,\
 or is not a valid MOD06 product")
            raise
    
    def __interpolateGeoreferencing(self):
        """ Interpolate the georeferencing 5k grid included in the product for 1k and 250m array. This has not
            be test in regard of MOD03 9? (contains 1k grid by NASA) but consistenty of result has been assessed.
            IMP: For this function to work correctly, the roi must contains at least more than 3 element,
            so we can safely interpolate a second dregree spline. 
        """
        latitude = np.dsplit(self.georef_grid, 2)[0]
        longitude = np.dsplit(self.georef_grid, 2)[1]
        from scipy import interpolate
        ## 1k interpolation
        # Indices for the 1k grid
        x = np.arange(latitude.shape[0])
        y = np.arange(latitude.shape[1])
        xx = np.linspace(x.min(), x.max(), self.size1k[0])
        yy = np.linspace(y.min(), y.max(), self.size1k[1])
        # Create the 1k grid : Latitude and longitude
        lat_1k = interpolate.RectBivariateSpline(x, y, latitude)(xx, yy)
        long_1k = interpolate.RectBivariateSpline(x, y, longitude)(xx, yy)
        # Merge
        self.georef_grid1k = np.dstack((lat_1k, long_1k))
   
    def extractSolarZenith_5k(self):
        """ Solar Zenith Angle, Cell to Sun. in degrees. """
        scale_factor = 0.01
        return np.multiply(self.extractByName('Solar_Zenith (16-bit integer)'), scale_factor)
    
    def extractSolarAzimuth_5k(self):
        """ Solar Azimuth Angle, Cell to Sun. in degrees. """
        scale_factor = 0.01
        return np.multiply(self.extractByName('Solar_Azimuth (16-bit integer)'), scale_factor)
    
    def extractWaterVaporNearInfrared_1k(self):
        """Total Column Precipitable Water Vapor - Near Infrared Retrieval in cm. """
        scale_factor = 0.001
        return np.multiply(self.extractByName('Water_Vapor_Near_Infrared (16-bit integer)'), scale_factor)
    
    def extractScanStartTime_5k(self):
        """ TAI Time at Start of Scan replicated across the swath in seconds since 1993-1-1 00:00:00.0 0"""
        return self.extractByName('Scan_Start_Time (64-bit floating-point)')

    def extractWaterVaporCorrectionFactors_1k(self):
        """ Aerosol Correction Factor for Water Vapor - Near Infrared Retrieval, No unit """
        scale_factor = 0.001
        return np.multiply(self.extractByName('Water_Vapor_Correction_Factors (16-bit integer)'), scale_factor)
        
  
    def extractCloudMaskQA_CloudMaskFlag_1k(self):
        """ MODIS Cloud Mask and Spectral Test Results: Cloud Mask Flag from bit 1.
           Cloud Mask Flag                      0 = not determined
                                                1 = determined
        """
        cloudMaskQA = self.extractByName('Cloud_Mask_QA (8-bit integer)')
        print(cloudMaskQA.shape)
        byte = np.unpackbits(cloudMaskQA)
        byte = byte.reshape(byte.size/8, 8).reshape(self.size1k[0], self.size1k[1], 8)
        cm_flag = byte[:,:,7]
        return cm_flag

    def extractCloudMaskQA_QualityFlag(self):
        """Return a numpy array for the 'Cloud_Mask Unobstructed FOV Quality Flag' from bit 2,1
           Value for each 1k square:          00 = cloud
                                              01 = 66% prob. clear
                                              10 = 95% prob. clear
                                              11 = 99% prob. clear
        """
        cloudMaskQA = self.extractByName('Cloud_Mask_QA (8-bit integer)')
        byte = np.unpackbits(cloudMaskQA)
        byte = byte.reshape(byte.size/8, 8).reshape(self.size1k[0], self.size1k[1], 8)
        q_flag = byte[:, :, 5:7]
        q_flag = np.squeeze(np.packbits(q_flag, axis=-1), axis=(2,)) # Reconstruct the array for Quality Flag
        return q_flag

    def extractCloudMaskQA_LandCoverFlag(self):
        """Return a numpy array for the 'Land or Water Path' from bit 7,6. 
           Value for each 1k square:    00 = Water
                                        01 = Coastal
                                        10 = Desert
                                        11 = Land
        """
        cloudMaskQA = self.extractByName('Cloud_Mask_QA (8-bit integer)')
        byte = np.unpackbits(cloudMaskQA)
        byte = byte.reshape(byte.size/8, 8).reshape(self.size1k[0], self.size1k[1], 8)
        lc_flag = byte[:,:,0:2]
        lc_flag = np.squeeze(np.packbits(lc_flag, axis=-1), axis=(2,))
        return lc_flag

    def dispayOnMap(self, product):
        """ Template function for displaying on a map. Not meant to be used as it is. Present
            a reference layout """
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        from matplotlib import colors
        from mpl_toolkits.basemap import Basemap
        import matplotlib as mpl


        fig, ax = plt.subplots()
        fig.set_facecolor('white')
        mpl.rc('font', family='sans-serif')
        mpl.rc('font', serif='Oxygen-Sans')
        mpl.rc('text', usetex='false')
        mpl.rcParams.update({'font.size': 11})

        # Basemap ('lcc' = lambert conformal conic).
        map = Basemap(projection = 'lcc', resolution='h', area_thresh=0.1,
            llcrnrlon=103, llcrnrlat=1,                     # A bit bigger area
            urcrnrlon=105, urcrnrlat=2,
            #llcrnrlon=103.529044, llcrnrlat=1.132124,      # Bounding box
            #urcrnrlon=104.160634, urcrnrlat=1.546439,
            lat_0 = 1.342966, lon_0 = 103.680594
            )
        ## Appearance
        map.drawcoastlines()
        
        if (product == 'LC'):
            cmap_bg = colors.ListedColormap(['blue', 'palegreen','red','green']) # red for desert, palegreen for coastal
            bounds_bg = [0, 64, 128, 192, 256]
            norm_bg = colors.BoundaryNorm(bounds_bg, cmap_bg.N)
            cax = map.pcolormesh(self.georef_grid1k[:, :, 1],
                                 self.georef_grid1k[:, :, 0],
                                 self.extractCloudMaskQA_LandCoverFlag(),
                                 shading='flat', cmap=cmap_bg, norm=norm_bg, latlon=True)
            ax.set_title('.'.join(self.filename.split('/')[-1].split('.')[0:-2]) + ' \n Land Cover Flag')
            cbar = fig.colorbar(cax, ticks=[32, 96, 160, 224])
            cbar.ax.set_yticklabels(['Water', 'Coastal', 'Desert', 'Land'])
            
        elif (product == 'CM_subsample'):
            "ax.set_title('.'.join(self.filename.split('/')[-1].split('.')[0:-2]) + ' \n Cloud Mask')"
            cmap = colors.ListedColormap(['gray','green','red', 'blue'])
            bounds =[0, 64, 128, 192, 256]
            norm = colors.BoundaryNorm(bounds, cmap.N)
            cax = map.pcolormesh(self.georef_grid1k[:, :, 1],
                                 self.georef_grid1k[:, :, 0],
                                 self.extractCloudMaskQA_QualityFlag(),
                                 shading='flat', cmap=cmap, norm=norm, latlon=True)
            cbar = fig.colorbar(cax, ticks=[32, 96, 160, 224])
            cbar.ax.set_yticklabels(['100% clouds', '60% cloud free', '92% cloud free', '98% cloud free'])
        elif (product == 'CM'):
            ax.set_title('.'.join(self.filename.split('/')[-1].split('.')[0:-2]) + ' \n Cloud Mask')
            cmap = colors.ListedColormap(['gray','green','red', 'blue'])
            bounds =[0, 64, 128, 192, 256]
            norm = colors.BoundaryNorm(bounds, cmap.N)
            cax = map.pcolormesh(self.georef_grid1k[:, :, 1],
                                 self.georef_grid1k[:, :, 0],
                                 self.extractCloudMaskQA_QualityFlag(),
                                 shading='flat', cmap=cmap, norm=norm, latlon=True)
            cbar = fig.colorbar(cax, ticks=[32, 96, 160, 224])
            cbar.ax.set_yticklabels(['100% clouds', '60% cloud free', '92% cloud free', '98% cloud free'])
        # Point for WSI position
        map.scatter(self.center[1], self.center[0], s=100, facecolor='none', edgecolors='g', latlon = True, alpha=1)
        fig.tight_layout()
        plt.show()
