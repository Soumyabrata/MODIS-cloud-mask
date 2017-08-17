import numpy as np

def normalize_array( a ):
	
	min_value = np.amin(a)
	max_value = np.amax(a)
	
	norm_array = [None]*len(a)
	
	#print (a)
	
	for i in range(0,len(a)):
		
		norm_array[i] = (a[i]-min_value)/(max_value - min_value)
	
	#print (norm_array)
	return(norm_array)
