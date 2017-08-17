import csv
import datetime



#file_path = "./COT_values/2015/COT2015.txt"
#YEAR = 2015
#(datetime_COT,COT_values) = readingCOVERAGE(file_path,YEAR)

def readingCOVERAGE(file_path):
    

    
    #input_file = csv.DictReader(open(file_path), fieldnames = ["Image"," Date"," Time", " Cloud_Coverage"])
    input_file = csv.DictReader(open(file_path))
    
    #day_number = []
    datetime_COV = []
    COV_values = []
    #YEAR = 2015

    for row in input_file:
        #print (row)
    
        
    
        if (1):
            #day = int(row["DayNumber"])
            #date_object = datetime.datetime(YEAR, 1, 1) + datetime.timedelta(day - 1)
            
            date_string = row[" Date"]
            date_components = date_string.split(":")
            YEAR = int(date_components[0])
            MON = int(date_components[1])
            DAY = int(date_components[2])

    
            time_string = row[" Time"]
            time_components = time_string.split(":")
            HH = int(time_components[0])
            MINT = int(time_components[1])
            SEC = int(time_components[2])
            
            COV_item = float(row[" Cloud_Coverage "])
    
            sw = datetime.datetime(YEAR,MON,DAY,HH,MINT,SEC)
            datetime_COV.append (sw)    
    
            COV_values.append(COV_item)
    

    return (datetime_COV,COV_values)