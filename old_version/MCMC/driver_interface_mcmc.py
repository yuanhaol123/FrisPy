import ctypes
import numpy as np

#This function interfaces with the driver.so shared library
#It gathers all of the times and positions to pass back to
#the mcmc routines
def get_positions(initial_positions,coeffs,flight_time):

	#Change these to copied numpy arrays so that
	#it is gauranteed that they are contiguous in memory
	#This is a REQUIREMENT for arrays in c and isn't
	#fulfilled in python
	initial_positions = np.array(initial_positions, dtype=np.double).copy()
	coeffs = np.array(coeffs, dtype=np.double).copy()

	#Convert the initial angles and angular velocities in degrees to radians
	radians = np.pi/180. #used to convert to radians
	degrees = 180./np.pi #used to convert to degrees
	initial_positions[6:] = initial_positions[6:]*radians

	#Define the number of steps and find the timestep
	n_times = 400
	timestep = flight_time/n_times

		#Load the driver library and its funcitons
	#Then specify the arguement and return types
	driver_lib = ctypes.cdll.LoadLibrary('src/driver.so')
	driver = driver_lib.driver
	cleanup = driver_lib.cleanup
	driver.restype = ctypes.POINTER(ctypes.c_double)
	driver.argtypes = [ctypes.POINTER(ctypes.c_double),\
		ctypes.POINTER(ctypes.c_double),\
		ctypes.c_double,ctypes.c_int,\
		ctypes.POINTER(ctypes.c_double)]
	cleanup.restype = (None)
	cleanup.argtypes = [ctypes.POINTER(ctypes.c_double)]

	#Create the array that holds all of the positions and times
	all_positions = np.zeros(n_times*13,dtype=np.double)

	#Create instances of pointers pointing to the important arrays
	ip_out = initial_positions.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
	co_out = coeffs.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
	ap_out = all_positions.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

	#Call the driver and change back to degrees
	driver(ip_out,co_out,flight_time,n_times,ap_out)
	all_positions = np.array(ap_out[0:n_times*13]).reshape((n_times,13))
	all_positions[:,6:]*=degrees
        
	#Return the entire position array
	print "Returning positions array with shape:"
	print "\t",np.shape(all_positions)
	return [all_positions, n_times]
