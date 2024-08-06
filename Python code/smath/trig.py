#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 12:03:16 2023

@author: stevenwaal
"""


import math

def sin_deg(angle_deg):
    return math.sin(math.radians(angle_deg))

def asin_deg(ratio):
    return math.degrees(math.asin(ratio))

def cos_deg(angle_deg):
    return math.cos(math.radians(angle_deg))

def acos_deg(ratio):
    return math.degrees(math.acos(ratio))

def tan_deg(angle_deg):
    return math.tan(math.radians(angle_deg))

def atan_deg(ratio):
    return math.degrees(math.atan(ratio))



if __name__=='__main__':
    
    # Test cases
    assert sin_deg(0)==0, 'Should be 0'
    assert sin_deg(90)==1, 'Should be 1'
    
    assert asin_deg(0) == 0
    assert asin_deg(1) == 90
    
    assert cos_deg(0)==1, 'Should be 1'
    assert abs(cos_deg(90))<0.0001, 'Should be 0'
    
    assert acos_deg(1) == 0
    assert acos_deg(0) == 90
    
    assert tan_deg(45) == 0.9999999999999999
    assert tan_deg(0) == 0
    
    assert atan_deg(1) == 45
    
    
    print('All tests passed')
    