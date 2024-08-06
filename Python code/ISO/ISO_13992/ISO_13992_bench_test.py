#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  1 10:01:14 2024

@author: stevenwaal
"""



import pandas
import matplotlib.pyplot as plt

# from lib.ISO.ISO_z_table import ISO_z_table_func
from lib.ISO.ISO_13992.abc_ISO_13992_plots import ABCISO13992Plots
# from lib.ISO_13992.ISO_13992_plots import ISO13992Plots, ISO13992PlotContainer

class ISO13992BenchTest(ABCISO13992Plots):
    
    def __init__(self, filepath, z_set, boot, test_axis, torque_wrench_type, legend_string):
        
        self.boot = boot
        self.legend_string = legend_string
        self.z_set = z_set # The Z setting value that the binding scale was set to (NOT the value that is measured!)
        
        elasticity_measurements, torque_wrench_readings = self.import_testing_data(filepath)
        self.elasticity_measurements = elasticity_measurements
        self.torque_wrench_readings = torque_wrench_readings
        
        if test_axis=="My":
            self.test_axis = "My"
        elif test_axis=="Mz":
            self.test_axis = "Mz"
        else:
            raise Exception('Invalid selection for test_axis. Choose either "My" or "Mz".')
            
        if torque_wrench_type == 'digital':
            self.torque_wrench_type = torque_wrench_type
        elif torque_wrench_type == 'beam':
            self.torque_wrench_type = torque_wrench_type
        else:
            raise Exception("Incorrect torque wrench type. Choose 'digital' or 'beam'.")   
        
        self.boot_moments = []
        self.boot_moments_divided_by_BSL = []
        self.elasticity = []
        
        self.process_data()

    def import_testing_data(self, filepath):
        '''
        A function to import the CSV data
    
        Parameters
        ----------
        filepath : str
            String representation of the absolute filepath of the testing data csv.
            The testing data CSV must contain two columns of data:
                column1: the elasticity measurements
                column2: the torque wrench readings
    
        Returns
        -------
        list
            Two lists: elasticity_measurements and torque_wrench_readings.
    
        '''
        
        data = pandas.read_csv(filepath) # Read CSV data and convert dataframe to array
        elasticity_measurements = data.iloc[:,0].to_numpy()
        torque_wrench_readings = data.iloc[:,1].to_numpy()
        
        return [elasticity_measurements, torque_wrench_readings]
    
    def process_data(self):
        
        for value in self.get_torque_wrench_readings():
            if self.get_test_axis() == "My":
                moment = self.calc_My(value, self.torque_wrench_type)
            else:
                moment = value
           
            
            force = moment/(self.get_boot_BSL()/1000) 
            
            self.boot_moments.append(moment)
            self.boot_moments_divided_by_BSL.append(force)
            
        # Zero out elasticity measurements
        for value in self.get_elasticity_measurements():
            self.elasticity.append(value - self.get_elasticity_measurements()[0])
       
    def calc_My(self, M_t, torque_wrench_type):
        # M_t = moment reading from torque wrench
                
        if torque_wrench_type == 'digital':
            L_t = 495 # [mm]
        elif torque_wrench_type == 'beam':
            L_t = 430 # [mm]
        else:
            raise Exception("Incorrect torque wrench type. Choose 'digital' or 'beam'.")
        
        L_f = 1490 # [mm] Length of Jerry's leg
        
        return (M_t/L_t) * (L_t + L_f)
   
    def plot_forces(self):
        
        fig, ax1 = plt.subplots()
        ax1.plot(self.get_elasticity(), self.get_boot_moments_divided_by_BSL())
        
        
        
        # Determine axis limits of plot
        ax1_x_limits = ax1.get_xlim()
        ax1_x_range = ax1_x_limits[1] - ax1_x_limits[0]
        
        # Add text to plot for Z values
        text_x_percentage = 1.02 # X position of text, specified as a "percentage" of the x limits
        text_x_pos = (text_x_percentage*ax1_x_range)+ax1_x_limits[0]
        # Plot heel force associated with each Z value
        
        # if self.get_test_axis()=="My":
        #     column_index = ISO_z_table_func.i_F_My
        # elif self.get_test_axis()=="Mz":
        #     column_index = ISO_z_table_func.i_F_Mz
        # else:
        #     raise Exception('Invalid selection for test_axis. Choose either "My" or "Mz".')
        
        # i_z = ISO_z_table_func.i_z
        
        # for row in ISO_z_table_func.iso_z_table:
        #     if row[i_z].is_integer():
        #         ax1.axhline(y = row[column_index], color = '0.9', linestyle = '-', linewidth=1, zorder=-10)
        #         ax1.text(text_x_pos, row[column_index], ('%i'%row[i_z]), backgroundcolor = 'w', verticalalignment='center')
        
        
        ax1.set_xlabel('Elasticity [mm]')
        ax1.set_ylabel('Boot moment/BSL [N]')
        
        ax1.set_title(f"{self.get_test_axis()}")

        plt.show()
        
        
###############  
        
    def get_test_axis(self):
        return self.test_axis

    def get_elasticity_measurements(self):
        return self.elasticity_measurements
    
    def get_torque_wrench_readings(self):
        return self.torque_wrench_readings
    
    def get_boot(self):
        return self.boot
    
    def get_boot_BSL(self):
        return self.boot.get_BSL()
    
    def get_boot_PSL(self):
        return self.boot.get_PSL()
    
    def get_boot_model(self):
        return self.boot.get_model()
    
    def get_boot_size(self):
        return self.boot.get_size()
    
    def get_elasticity(self):
        return self.elasticity
    
    def get_boot_moments(self):
        return self.boot_moments
    
    def get_boot_moments_divided_by_BSL(self):
        return self.boot_moments_divided_by_BSL
    
    def get_legend_string(self):
        return self.legend_string
    
    def get_z_set(self):
        return self.z_set
    
    # 'set' functions ---------------------------------------------------------
    def set_z_set(self, new_z_set):
        self.z_set = new_z_set
        
    def set_legend_string(self, new_legend_string):
        self.legend_string = new_legend_string
        
    
if __name__ == "__main__":
    
    from lib.boots import boot
    plt.close('all')
    
    
    filepath1 = '/Users/stevenwaal/Documents/Alpenflow Design/Python Scripts/testing/testing_data/My/My, 05-03-2024, Sonora on Chamonix, Z7 - Trial 1.csv'
    boot1 = boot.Boot('Tecnica Zero G Tour Pro', '270-275')
    
    test1 = ISO13992BenchTest(filepath1, 7, boot1, 'My','digital', 'Sonora, My, Trial 1, Z~7')
    test1.plot_forces()
    
    print()
    print()
    print('*****************************************')
    print('* Celebrate!! All of the tests passed!! *')
    print('*****************************************')
    print()
    print()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    