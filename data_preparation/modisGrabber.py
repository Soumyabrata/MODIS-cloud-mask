#!/usr/bin/env ipython2
""" File: modisGrabber.py. 
    Author: Joseph Lemaitre <joseph.lemaitre@epfl.ch>
    Compagny: Illinois@Singapore Pte. Ldt

    Description: This script download MODIS product. It is part of a framework allowing to fetch and process
    MODIS Atmosphere products.

    Manual:
        1. Folder structure: this script should be in code/ModisGrabber/. Then you must create a directory named _data/ 
        in the code/ directory. This script will download the products there. Once a download is finished, you should
        move the data from the _data/ folder to the data/ one, so you can use them, and so that the grabber has a empty 
        directory for it next download.
            Final stucture:
                code/
                     _data/          # Use for download only.
                     data/           # Data already downloaded, to be use with the other scripts.
                     ModisGrabber/   # Location of this script.

       2. Once this is done, read the PARAMETERS section. Read the comments for the syntax, and modify them as you
       wish.
       3. Run the script. What it does,
            For each date**:
                 * Create a directory: _data/data-{DATE}/. If the directory exist, it *wipes* it !!!!!
                 * Download geolocalisation dataset. Parse the file to find when AQUA and/or TERRA was above the bounding box.
                 * Then select the right products, download them.
                 * Once the download of all the product is done, it put a flag. A flag is a file into the directory 
                     _data/data-{DATE}/. 
                        If this file name is FAILURE, do not use what was downloaded and re-launch the grabber
                            for this day.
                        If this file name is SUCCESS, you can move the folder (i.e day) to data/, and use the products
                        If there is no file, then probably the download isn't finished yet.
                   The file contains a timestamp, along the reason of the failure if it didn't work, along with the name
                   of the products concerned.
"""
    
from __future__ import print_function # We need the print function and not the print statement
from ftplib import FTP
import datetime, csv, re, os, shutil, sys, ftplib

# -------------------------------------------------------------------------------------------
# *********************************   PARAMETERS  *******************************************
# -------------------------------------------------------------------------------------------

# Dates to download. This is either a command line argument, or a string.
# Format: 
#       * One number D : a number of day before today's date. Example: "7" -> 7 days ago
#       * A date YYYY-MM-DD: download this date only. Example: "2015-2-3" -> the 3rd february 2015
#       * A date range: YYYY-MM-DD--YYYY-MM-DD : Download every day between the two date 
#           separated by the double-dash "--". Example: 2015-2-3--2015-2-6 -> 2015-2-3, 2015-2-4, 2015-2-5, 2015-2-6
#       * A date range and an increment YYYY-MM-DD--YYYY-MM-DD:I : Download every I day between the two dates. Increment
#           is separated by a dash. Example: 2015-2-3--2015-3-1:7 -> 2015-2-3, 2015-2-10, 2015-2-17, 2015-2-24 (i.e every Thursday)
if (len(sys.argv) > 1):
    input_date = sys.argv[1]
else:
    #input_date = "2015-2-3--2015-3-17"         # <--- Specify the date here.
    input_date = "2015-01-02" 
# FTP Server to get the data from.
ftp_address = 'ladsweb.nascom.nasa.gov'
# Prefix to the directory where the products are stored, we download from the latest collection: 6.
ftp_prefix = '/allData/6/'


# Bounding box for our area of interest, see the bounding box directory for more information.
bounding_box = {'north_lat' : 1.546439,
                'south_lat' : 1.132124,
                'west_long' : 103.529044,  ###for Singapore
                'east_long' : 104.160634}  


#bounding_box = {'north_lat' : 50.5641667,
#               'south_lat' : 50.1641667,  ## for Ukraine
#               'west_long' : 30.24666,
#                'east_long' : 30.6966}   ## exact location 50.3641667, 30.4966667

#bounding_box = {'north_lat' : 13.5358333,
#                'south_lat' : 13.9358333,  ## for Thailand
#                'west_long' : 100.73338889,
#                'east_long' : 100.233888} 
                ## exact location 13.7358333,100.533888
#bounding_box = {'north_lat' : 18.2613889,
#                'south_lat' : 18.6613889,  ## for Dominican
#                'west_long' : -69.7111111,
#                'east_long' : -70.1111111}       
                 ## exact location 18.4613889,-69.9111111
#bounding_box = {'north_lat' : -43.03,
#                'south_lat' : -42.63,  ## for Aus Hobart
#                'west_long' : 147.70,  ## -42.83,147.50
#                'east_long' : 147.30}  
#bounding_box = {'north_lat' : 40.552778,
#                'south_lat' : 39.9452778,  ## for Beijing
#                'west_long' : 116.5238889,  ## 40.2452778,116.2238889
#                'east_long' : 115.9238889} 
#bounding_box = {'north_lat' : 30.2313889,
#                'south_lat' : 30.8313889,  ## for Wuhaan
#                'west_long' : 114.0572222,  ## 30.5313889,114.3572222
#                'east_long' : 114.6572222} 
#bounding_box = {'north_lat' : 32.0008889,
#                'south_lat' : 31.6238889,  ## for Japan 31.8238889	130.5994444                          
#                'west_long' : 130.7994444 ,
#                'east_long' : 130.3994444 } 
#bounding_box = {'north_lat' : 20.0011111,
#               'south_lat' : 19.6011111,  ## for Hawaii 19.8011111,-155.4561111                        
#                'west_long' : -155.5561111 ,
#                'east_long' : -155.3261111 } 
# List the products to download. Uncomment the products you want to download
# Beware the comma: one comma between each element, no comma at the end.
product_list = [
                'MYD35_L2',    # Cloud Mask, Aqua
                'MOD35_L2',    # Cloud Mask, Terra
                'MYD05_L2',    # Total Precipitable Water, Aqua
                'MOD05_L2',    # Total Precipitable Water, Terra
                'MYD06_L2',    # Cloud Product, Aqua
                'MOD06_L2'     # Cloud Product, Terra
                ]

# False: Then we download only the products above singapore between 10 and 18 SGT (i.e 0200 and 1000 UTC), when the WSI is up.       [Default]
# True : All products in the bounding box, regardless of time. Warning : may download lots of data, where Singapore is on the border of the event. !
download_all_hours = False

# -------------------------------------------------------------------------------------------
# ***************************************  CODE  *********************************************
# -------------------------------------------------------------------------------------------

if ('-' in input_date):         # User input a date or a date range
    data_time = datetime.date(int(input_date.split('-')[0]), int(input_date.split('-')[1]), int(input_date.split('-')[2]))
else:                           # User input a number of day from today
    data_time = datetime.datetime.utcnow() + datetime.timedelta(-int(input_date))

final_date = data_time
date_increment = 1
if ('--' in input_date):       # User specify a date range
    final_date = input_date.split('--')[1].split(':')[0]
    final_date = datetime.date(int(final_date.split('-')[0]), int(final_date.split('-')[1]), int(final_date.split('-')[2]))
if(':' in input_date):
    date_increment = int(input_date.split(':')[-1])
date_increment = datetime.timedelta(days=date_increment)

while (data_time <= final_date):
    try:
        current_date = data_time.timetuple()
        print("MG: ========================================================================================")
        print("MG: Downloading products {0}, at date {1}-{2}-{3} [{4} th day of the year]".format(product_list, current_date.tm_year,
                                                                                                  current_date.tm_mon, current_date.tm_mday, current_date.tm_yday))
        # Prepare the downloading directory TODO: Long if several products
        dir_name = "../_data/data-{0}-{1}-{2}/".format(current_date.tm_year,current_date.tm_mon, current_date.tm_mday)
        
        print (dir_name)
        
        print("MG: Wiping Directory {0}".format(dir_name))
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
        os.makedirs(dir_name)
        
        print("MG: Initializing connection")
        # Start a connection to the ftp
        ftp_server = FTP(ftp_address)
        ftp_server.login()

        # We need the MOD03, the Geolocalisation Data Set, to know which frame to download. We could also download them all
        # but our connection is slow. We uses the server .txt files.
        print("MG: Downloading Geolocalisation Data Set")

        ftp_server.cwd('/geoMeta/6/AQUA/' + str(current_date.tm_year))
        geo_filename = 'MYD03_' + str(current_date.tm_year) + '-' + str(current_date.tm_mon).zfill(2) \
                    + '-' + str(current_date.tm_mday).zfill(2) + '.txt'
        ftp_server.retrbinary('RETR ' + geo_filename , open(dir_name + geo_filename, 'wb').write)

        # Parse Geolocalisation Data Set to obtains the frame that consitute our bounding box
        good_frame_aqua = []
        
        print (dir_name + geo_filename)
        f = open(dir_name + geo_filename, 'r')
        #for line in f[1:]:
        #    print (line)
        
        #with open(dir_name + geo_filename) as csvfile:

        #    read_data = csvfile.read()
        #    print (type(read_data))
        #    print (read_data)
                            
                            
        with open(dir_name + geo_filename) as csvfile:

            csvfile.readline()       # Delete the fist two lines so the dictionary contains the right values.
            #csvfile.readline()
            reader = csv.DictReader(csvfile, fieldnames = ["GranuleID","StartDateTime","ArchiveSet","OrbitNumber","DayNightFlag","EastBoundingCoord","NorthBoundingCoord","SouthBoundingCoord","WestBoundingCoord","GRingLongitude1","GRingLongitude2","GRingLongitude3","GRingLongitude4","GRingLatitude1","GRingLatitude2","GRingLatitude3","GRingLatitude4"])
            
            #for row in reader:
            #    print (row)
            for row in reader:

                if (float(row['SouthBoundingCoord']) <= bounding_box['north_lat'] and
                    float(row['NorthBoundingCoord']) >= bounding_box['south_lat'] and
                    float(row['WestBoundingCoord']) <= bounding_box['east_long'] and
                    float(row['EastBoundingCoord']) >= bounding_box['west_long']):
                    print ('printing bounding box')
                    print (float(row['SouthBoundingCoord']) , bounding_box['north_lat'])                   
                    if (2 <= int(row['StartDateTime'][-5:-3]) <= 10):
                            good_frame_aqua.append(row['GranuleID'])

        ftp_server.cwd('/geoMeta/6/TERRA/' + str(current_date.tm_year))
        geo_filename = 'MOD03_' + str(current_date.tm_year) + '-' + str(current_date.tm_mon).zfill(2) \
                    + '-' + str(current_date.tm_mday).zfill(2) + '.txt'
        ftp_server.retrbinary('RETR ' + geo_filename , open(dir_name + geo_filename, 'wb').write)

        good_frame_terra = []
        with open(dir_name + geo_filename) as csvfile:
            #csvfile.next()          # Delete the fist two lines so the dictionary contains the right values.
            csvfile.readline()
            reader = csv.DictReader(csvfile, fieldnames = ["GranuleID","StartDateTime","ArchiveSet","OrbitNumber","DayNightFlag","EastBoundingCoord","NorthBoundingCoord","SouthBoundingCoord","WestBoundingCoord","GRingLongitude1","GRingLongitude2","GRingLongitude3","GRingLongitude4","GRingLatitude1","GRingLatitude2","GRingLatitude3","GRingLatitude4"])
            for row in reader:
                if (float(row['SouthBoundingCoord']) <= bounding_box['north_lat'] and
                    float(row['NorthBoundingCoord']) >= bounding_box['south_lat'] and
                    float(row['WestBoundingCoord']) <= bounding_box['east_long'] and
                    float(row['EastBoundingCoord']) >= bounding_box['west_long']):
                    if (download_all_hours or 2 <= int(row['StartDateTime'][-5:-3]) <= 10):
                        good_frame_terra.append(row['GranuleID'])

        # Strip to optain the re-usable form of the name. We remove 
        # Name format spec : http://modis-atmos.gsfc.nasa.gov/products_filename.html
        good_frame_aqua = ['.'.join(x.rsplit('.')[1:4]) for x in good_frame_aqua]
        good_frame_terra = ['.'.join(x.rsplit('.')[1:4]) for x in good_frame_terra]
        
        print (good_frame_aqua)
        print (good_frame_terra)
        
        print("MG: Will download frames:\n    TERRA : {0}\n    AQUA : {1}".format(good_frame_terra, good_frame_aqua))

        # Extraction of the products
        for product in product_list:
            # We use zfill for zero-padding
            data_path = ftp_prefix + product + "/" + str(current_date.tm_year) + "/" + str(current_date.tm_yday).zfill(3)
            ftp_server.cwd(data_path)
            if (product.find('MYD') >= 0):
                good_frame = good_frame_aqua
            else:
                good_frame = good_frame_terra
            for frame in good_frame:
                regex = "{0}.{1}.*.hdf".format(product,frame)
                print("MG: Downloading: product: " + product + ", frame: " + frame)
                for filename in ftp_server.nlst():
                    if(re.search(regex, filename)):
                        with open(dir_name + filename, "wb") as file:
                            ftp_server.retrbinary('RETR %s' % filename, file.write)
                            
    except ftplib.all_errors as e:
        print("MG: (EE) FTP Connection error: {0}\n MG: Download Aborded, Sorry :/".format(e))
        # Create a file to indicate error
        file = open(dir_name + "FAILURE", 'a')
        file.write("TIMESTAMP: {0} UTC\n".format(datetime.datetime.utcnow()))
        file.write("PRODUCTS: {0}\n".format(product_list))
        file.write("MODIS GRABBER EXCEPTION: {0}\n".format(e))
        file.close()
    else:
        print("MG: Download success for this day :)")
        file = open(dir_name + "SUCCESS", 'a')
        file.write("TIMESTAMP: {0} UTC\n".format(datetime.datetime.utcnow()))
        file.write("PRODUCTS: {0}\n".format(product_list))
        file.close()
        
    data_time = data_time + date_increment
