#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  9 10:58:11 2024

@author: stevenwaal
"""

# curve-fit() function imported from scipy
from scipy.optimize import curve_fit 
import numpy as np
from lib.ISO.ISO_13992.abc_ISO_13992_plots import ABCISO13992Plots

class ISO13992BenchTestCurveFit(ABCISO13992Plots):
    
    def __init__(self, bench_test_obj_list, legend_string):
    
        self.bench_test_obj_list = bench_test_obj_list
        self.legend_string = legend_string
        
        self.elasticity_data = [] # Aggregated data
        self.boot_moments_divided_by_BSL_data = [] # Aggregated data 
        self.elasticity = [] # Used to calculate the curve fit
        self.boot_moments_divided_by_BSL = [] # Calculated from curve fit
        
        self.aggregate_data()
        self.calc_curve_fit()
        
        self.test_axis = self.bench_test_obj_list[0].get_test_axis()
    
    def fit_func(self, x, a, b, c, d):
        return a - b**(c - (x/d) )
    
    def aggregate_data(self):
        
        z_set = self.bench_test_obj_list[0].get_z_set()
        
        max_elasticity_values = []
        
        for obj in self.bench_test_obj_list:
            self.elasticity_data.extend(obj.get_elasticity())
            self.boot_moments_divided_by_BSL_data.extend(obj.get_boot_moments_divided_by_BSL())
            
            max_elasticity_values.append(max(obj.get_elasticity())) # Get maximum elasticity values so that they can be averaged together to determine maximum elastic travel of curve fit
            
            if not(obj.get_z_set() == z_set):
                raise Exception('Error: Not all bench test objects are from the same Z value test. Only add bench test objects from the same Z value test.')
        self.z_set = z_set
        
        self.max_elastic_travel = sum(max_elasticity_values)/len(max_elasticity_values)
            
    def calc_curve_fit(self):
        initial_guess = [815, 45, 1.7, 4.3] # Based on solving the curve fit for Z=6
        param, param_cov = curve_fit(self.fit_func, self.elasticity_data, self.boot_moments_divided_by_BSL_data, p0=initial_guess)
        
        self.elasticity = np.linspace(min(self.elasticity_data), self.get_max_elastic_travel(), num=100)
        self.boot_moments_divided_by_BSL = self.fit_func(self.elasticity, param[0], param[1], param[2], param[3])
        
    def get_boot_moments_divided_by_BSL(self):
        return self.boot_moments_divided_by_BSL
    
    def get_elasticity(self):
        return self.elasticity
    
    def get_legend_string(self):
        return self.legend_string
    
    def get_test_axis(self):
        return self.test_axis
    
    def get_z_set(self):
        return self.z_set
    
    def get_max_elastic_travel(self):
        return self.max_elastic_travel
    
    # 'set' functions ---------------------------------------------------------
    def set_z_set(self, new_z_set):
        self.z_set = new_z_set
    
    def set_legend_string(self, new_legend_string):
        self.legend_string = new_legend_string
    
if __name__ == '__main__':
    
    import matplotlib.pyplot as plt
    from lib.ISO.ISO_13992.ISO_13992_plots import ISO13992Plots, ISO13992PlotContainer
    from lib.ISO.ISO_13992.ISO_13992_bench_test import ISO13992BenchTest
    from lib.boots.boot import Boot
    
    plt.close('all')
    
    # My, 05-07-2024, Sonora on Chamonix, Z4, Trials 1-3
    base_filepath = '/Users/stevenwaal/Documents/Alpenflow Design/Projects/1002 - Sonora/Testing/Release Curve Testing/Beam Torque Wrench/My, 05-07-2024, Sonora on Chamonix, Z4, Trials 1-3/'
    boot = Boot('Tecnica Zero G Tour Pro', '270-275')

    file_name = 'My, 05-07-2024, Sonora on Chamonix, Z4, Trial 1.csv'
    file_path = base_filepath + file_name
    z4_05072024_trial1 = ISO13992BenchTest(file_path, 4, boot, 'My', 'beam', 'Sonora, My, Z~4, Trial 1')

    file_name = 'My, 05-07-2024, Sonora on Chamonix, Z4, Trial 2.csv'
    file_path = base_filepath + file_name
    z4_05072024_trial2 = ISO13992BenchTest(file_path, 4, boot, 'My', 'beam', 'Sonora, My, Z~4, Trial 2')

    file_name = 'My, 05-07-2024, Sonora on Chamonix, Z4, Trial 3.csv'
    file_path = base_filepath + file_name
    z4_05072024_trial3 = ISO13992BenchTest(file_path, 4, boot, 'My', 'beam', 'Sonora, My, Z~4, Trial 3')
    
    
    z4_fit = ISO13992BenchTestCurveFit([z4_05072024_trial1,
                                        z4_05072024_trial2,
                                        z4_05072024_trial3],
                                       'Z~4 curve fit')
    
    object_list = []
    object_list.append(ISO13992PlotContainer(z4_05072024_trial1))
    object_list.append(ISO13992PlotContainer(z4_05072024_trial2))
    object_list.append(ISO13992PlotContainer(z4_05072024_trial3))
    object_list.append(ISO13992PlotContainer(z4_fit))
    iso_13992_plots = ISO13992Plots('My', object_list)
    iso_13992_plots.plot_forces_vs_elasticity()
    
    print()
    print()
    print('*****************************************')
    print('* Celebrate!! All of the tests passed!! *')
    print('*****************************************')
    print()
    print()
    