import numpy as np
import bisect



def nearest(ts,s):

	# Given a presorted list of timestamps:  s = sorted(index)
	i = bisect.bisect_left(s, ts)
	nearest_timestamp = min(s[max(0, i-1): i+2], key=lambda t: abs(ts - t))
	diff_timestamps = (nearest_timestamp - ts).total_seconds()
	return (nearest_timestamp,diff_timestamps)
	
	
	
def find_nearest_rainevent(time1_index, rain_array):

	rain_points = np.where(rain_array!= 0)[0]
	time2_index = np.argmin(numpy.abs(rain_points - time1_index))
	return (time2_index)
