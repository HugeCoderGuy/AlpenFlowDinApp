#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  3 13:25:24 2024

@author: stevenwaal
"""


from abc import ABC, abstractmethod

class ABCISO13992Plots(ABC):
    
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def get_boot_moments_divided_by_BSL(self):
        '''
        Returns the equivalent force that would act on the heel in order to 
        create the calculated moment for a given BSL. The calculation is:
            boot_heel_force = moment_on_boot / BSL
        This is done to normalize the data so that it cam be compared between
        different tests and calculations.
        
        Returns
        -------
        An array of the equivalent boot heel forces.

        '''
        pass
    
    @abstractmethod
    def get_elasticity(self):
        pass
    
    @abstractmethod
    def get_legend_string(self):
        pass
    
    @abstractmethod
    def get_test_axis(self):
        pass
    
    @abstractmethod
    def get_z_set(self):
        pass
    
    # -- 'Set' Functions ------------------------------------------------------
    @abstractmethod
    def set_legend_string(self):
        pass
    
    