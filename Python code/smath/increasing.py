#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  8 16:21:02 2023

@author: stevenwaal

Miscellaneous math functions written by Steven
"""

from scipy import integrate
import numpy as np

def createLinearArray(min_value, max_value, increment):
    '''
    Creates a linear array starting at min_value and going up to max_value

    Parameters
    ----------
    min_value : float
        The starting point or minimum value of the array.
    max_value : float
        The ending point or maximum value of the array.
    increment : float
        The desired step size between values in the array.

    Returns
    -------
    array : numpy array object
        The array containing the linear progression of values starting at 
        min_value and going up to max_value with an increment size of
        increment.

    '''
    num_values = int((max_value - min_value)/increment + 1) # [-] No. of values
    array = np.linspace(min_value, max_value, num=num_values)
    return array
    
def findNearestIndex(x, x_array, dir='fwd'):
    '''
    Finds the index of the nearest value in x_array to the value given by x. 
    The 'nearest value' is defined as either the value that is greater than x 
    (fowrard) or less than x (reverse)

    Parameters
    ----------
    x : float
        The desired X value you want to find the index of in x_array.
    x_array : list or array
        The array of values that you are interested in sorting through. The
        values in x_array must all be increasing or decreasing. There can be
        NO local minimums or maximums.
    dir : str, optional
        Specifies the direction to searh x_array. The default is 'fwd'. The
        opetions are:
            fwd - The array is searched normally. The nearest value is the
                  the closest value that is greater than or equal to x.
            rev - The array is searched in reverse order. The nearest value
                  is the closest value that is less than or equal to x.

    Returns
    -------
    i : int
        The index of the nearest value in x_array to the value given by x.

    '''
    # Forwards
    if dir == 'fwd':
        i = 0
        for value in x_array:
            if x <= value:
                break
            i=i+1
        return i
    # Reverse
    else:
        rev_x_array = x_array[::-1] # Reverses x_array
        i = len(rev_x_array)-1
        for value in rev_x_array:
            if x >= value:
                break
            i=i-1
        return i
        

def trimArray(x1, x2, x_array):
    '''
    Trims the array x_array by the values specified in x1 and x2. x1 and x2 
    sepcify the outer bounds of the trimmed array. For example:
        
        x_array = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        x1 = 0.12
        x2 = 0.79
        
    will return [0.2, 0.3, 0.4, 0.5, 0.6, 0.7] since 0.2 is the closest value 
    greater than or equal to x1, and 0.7 is the closest value less than or
    equal to x2.

    Parameters
    ----------
    x1 : float
        The lower bound value of the array that should be trimmed. MUST BE 
        LESS THAN x2.
    x2 : float
        The upper bound value of the array that should be trimmed. MUST BE
        GREATER THAN x1.
    x_array : list or array
        The list or array that we want to trim. MUST BE INCREASING!

    Returns
    -------
    list or array
        The trimmed list/array, or 0 if there was an error.

    '''
        
    # Error checking
    if x2<=x1:
        return 0
    
    x1_index = findNearestIndex(x1, x_array)
    x2_index = findNearestIndex(x2, x_array) # Come from the same direction!!!!
    # x2_index = findNearestIndex(x2, x_array, dir='rev') # Reverse to make sure values are inclusive
        
    return x_array[x1_index:x2_index+1]

def trimArrayXandY(x1, x2, x_array, y_array):
    # Trim both the x and y arrays
    
    # if not is_increasing(x_array):
    #     raise Exception('X array is not increasing!')
    
    x1_index = findNearestIndex(x1, x_array)
    x2_index = findNearestIndex(x2, x_array) # Come from the same direction!!!!
    # x2_index = findNearestIndex(x2, x_array, dir='rev') # Reverse to make sure values are inclusive
    
    x_array_trim = trimArray(x1, x2, x_array)
    y_array_trim = y_array[x1_index:x2_index+1]
    
    return [x_array_trim, y_array_trim]
        

def integrateTrapRule(x1, x2, x_array, y_array):
    '''
    Integrates y_array on the interval x1 to x2 using 
    scipy.integrate.cumulative_trapezoid(). 

    Parameters
    ----------
    x1 : float
        Lower bound of integration. MUST BE LESS THAN x2.
    x2 : TYPE
        Upper bound of integration. MUST BE GREATER THAN x1.
    x_array : list or array
        The list or array of x values. MUST BE THE SAME LENGTH AS y_array.
    y_array : list or array
        The list or array of y values to integrate. MUST BE THE SAME LENGTH AS
        x_array.

    Returns
    -------
    float
        The value of the integral.

    '''
    
    # Error checking
    if x2<=x1:
        return 0
    
    if len(x_array)!=len(y_array):
        return 0
    
    # x1_index = findNearestIndex(x1, x_array)
    # x2_index = findNearestIndex(x2, x_array, dir='rev') # Reverse to make sure values are inclusive
    
    # x_array = trimArray(x1, x2, x_array)
    # y_array = y_array[x1_index:x2_index+1]
    
    x_array_trim, y_array_trim = trimArrayXandY(x1, x2, x_array, y_array)
    
    # Integrate
    integration_array = integrate.cumulative_trapezoid(y_array_trim, x_array_trim)
    # Return only last value
    area = integration_array[len(integration_array)-1]
    
    return area
    

def findClosestIntersection(x1, x2, x_array, y1_array, y2):
    '''
    Find x coordinate and index of the intersection of y1_array anxd y2_array in
    between the search zone specified by x1 and x2
    x_array must be increasing!

    Parameters
    ----------
    x1 : float
        The lower bound of the search zone.
    x2 : float
        The upper bound of the search zone.
    x_array : list
        A list containing the x values that correspond to .
    y1_array : numpy array or list
        A list containing the y values of the function.
    y2 : float or list
        A single y value or a list of y values (function) that you want to find the intersection with.

    Returns
    -------
    list
        [x_array_intersection_value, x_array_intersection_index].

    '''
    
    # Check if x_array is a numpy array object. If it is, convert it to a list.
    if isinstance(x_array, np.ndarray):
        x_array = x_array.tolist()
    
    # If y2 is a constant, create array of constants with the same length as
    # y1_array
    if not(hasattr(y2, '__iter__')):
        y2_array = [y2 for _ in range(len(y1_array))]
        
    else:
        y2_array = y2
    
    # trim arrays to search zone
    x_array_trim, y1_array_trim = trimArrayXandY(x1, x2, x_array, y1_array)
    x_array_trim, y2_array_trim = trimArrayXandY(x1, x2, x_array, y2_array)
    
    difference = []
    i=0
    for y1 in y1_array_trim:
        difference.append(abs(y1 - y2_array_trim[i]))
        i+=1
    
    x_array_trim_intersection_index = difference.index(min(difference))
    x_array_intersection_value = x_array_trim[x_array_trim_intersection_index]
    
    x_array_intersection_index = x_array.index(x_array_intersection_value)
    
    return [x_array_intersection_value, x_array_intersection_index]


# def findIntersection(x1, x2, x_array, y1_array, y2):
#     # Finds a more exact intersection using linear interpolation. Does not 
#     # return the index of the nearest element
#     x_closest, x_closest_index = findClosestIntersection(x1, x2, x_array, y1_array, y2)
    
#     # If y2 is a constant, create array of constants with the same length as
#     # y1_array
#     if not(hasattr(y2, '__iter__')):
#         print(f'{y2} is not iterable')
#         y2_array = [y2 for _ in range(len(y1_array))]
#         print(type(y2_array))
        
#     else:
#         print(f'{y2} is iterable')
#         y2_array = y2
        
#     y1_a = y1_array[x_closest_index - 1]
#     y1_b = y1_array[x_closest_index + 1]



def is_increasing(array):
    # determines if the array is increasing
    
    max_value = array[len(array)-1]
    for value in array:
        if value > max_value:
            return False
        
    return True




if __name__=='__main__':
    
    # Test code
    
    x_array =  [ 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    y_array =  [12,  13,  14,  15,  16,  17,  18,  17,  16,  15, 14]
    y2_array = [ 6,   7,   10, 14,  16,  18,  20,  22,  25,  30, 32]
    x1 = 0.12
    x2 = 0.79
    y1_array = y_array
    y2 = 16
    y2_numpy_array = np.array(y2_array)

    # x_array = [0, 1, 2, 3, 4, 5]
    # y_array = [2, 2, 2, 2, 2, 2]
    # x1 = 0
    # x2 = 5
    
    print('Find index (fwd): ' + str(findNearestIndex(x1, x_array)))
    print('Find index (rev): ' + str(findNearestIndex(x2, x_array, dir='rev')))
    print('Trim array: ' + str(trimArray(x1, x2, x_array)))
    print('Integrate trap rule: ' + str(integrateTrapRule(x1, x2, x_array, y_array)))
    print('Trim array X and Y: ' + str(trimArrayXandY(x1, x2, x_array, y_array)))
    print('findClosestIntersection() - y2 is an array: ' + str(findClosestIntersection(x1, x2, x_array, y1_array, y2_array)))
    print('findClosestIntersection() - y2 is a constant: ' + str(findClosestIntersection(x1, x2, x_array, y1_array, y2)))
    print('findClosestIntersection() - y2 is a numpy array: ' + str(findClosestIntersection(x1, x2, x_array, y1_array, y2_numpy_array)))



    # createLinearArray()
    print(f'createLinearArray(): {createLinearArray(0,5,1)}')

    assert is_increasing(x_array) == True
    assert is_increasing(y_array) == False
    
    
    print()
    print()
    print('*****************************************')
    print('* Celebrate!! All of the tests passed!! *')
    print('*****************************************')
    print()
    print()
