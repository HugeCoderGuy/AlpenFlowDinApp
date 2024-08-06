#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 09:26:43 2023

@author: stevenwaal
"""

from lib.smath import increasing
import math

def integrate_degrees_moments(theta_start_deg, theta_stop_deg, theta_array_deg, moment_array_Nm):
    
    # Convert to radians
    theta_start_rad = math.radians(theta_start_deg)
    theta_stop_rad = math.radians(theta_stop_deg)
    
    # Convert to radians
    theta_array_rad = []
    for angle in theta_array_deg:
        theta_array_rad.append(math.radians(angle))
    
    return increasing.integrateTrapRule(theta_start_rad, theta_stop_rad, theta_array_rad, moment_array_Nm)


def integrate_millimeters_newtons(x1, x2, x_array, force_array):
    
    # Convert to m
    x1_m = x1/1000
    x2_m = x2/1000
    
    x_array_m = []
    for x in x_array:
        x_array_m.append(x/1000)
        
    return increasing.integrateTrapRule(x1_m, x2_m, x_array_m, force_array)



if __name__=='__main__':
    

    # Test data
    theta_array_deg = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    moment_array_Nm = [5,  5,  5,  5,  5,  5,  5,  5,  5,  5]
    
    # integrateDegreesMoments
    assert integrate_degrees_moments(0,90,theta_array_deg,moment_array_Nm) == 7.853981633974482
    
    print()
    print()
    print('*****************************************')
    print('* Celebrate!! All of the tests passed!! *')
    print('*****************************************')
    print()
    print()