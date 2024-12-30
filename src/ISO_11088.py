#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 08:29:19 2024

@author: stevenwaal
"""
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit 
import pandas as pd
import numpy as np
import math


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



class ISO11088():
    
    def __init__(self, z_max=15):
        table_B1_file_path_and_name = 'src/ISO 11088_2023 - Table B1 - Expanded.csv'
        self.df_table_B1 = pd.read_csv(table_B1_file_path_and_name) # Read CSV into a pandas dataframe
        self.z_max = z_max
        self.update_all_values()

    def calc_high_and_low_boot_moments_divided_by_BSL_from_table_B1(self):
        df_z_table = self.df_table_B1.loc[:, '230':'351']
        df_z_table = df_z_table.apply(pd.to_numeric, errors='coerce')
        df_BSL = pd.DataFrame(list(self.df_table_B1.loc[:, '230':'351']))
        df_BSL = df_BSL.apply(pd.to_numeric, errors='coerce')
        df_BSL = df_BSL.divide(1000)

        z_table = df_z_table.values.tolist()
        Mz = list(self.df_table_B1['Mz [Nm]'])
        My = list(self.df_table_B1['My [Nm]'])
        BSL = list(df_BSL[0])
        z_Mz_div_BSL = []
        z_My_div_BSL = []
        for i in range(len(z_table)):
            for j in range(len(z_table[0])):
                value = float(z_table[i][j])
                if math.isnan(value):
                    pass
                else:
                    z_Mz_div_BSL.append([z_table[i][j], Mz[i]/BSL[j]])
                    z_My_div_BSL.append([z_table[i][j], My[i]/BSL[j]])

        def _find_high_low(z_M_div_BSL):
            
            z = []
            for i in range(len(z_M_div_BSL)):
                z.append(z_M_div_BSL[i][0])
            
            z_unique = list(set(z))
            z_unique.sort()
            
            temp = {}
            high = {}
            low = {}
            for z_value in z_unique:
                temp[str(z_value)] = []
                high[str(z_value)] = None
                low[str(z_value)] = None
    
            for key in temp:
                key_value = float(key)
                for arr in z_M_div_BSL:
                    z = arr[0]
                    mz_div_bsl = arr[1]
                    
                    if z==key_value:
                        temp[key].append(mz_div_bsl)
    
            high = []
            low = []
            mid = []
            for key in temp:
                high.append(max(temp[key]))
                low.append(min(temp[key]))
                mid.append((max(temp[key]) + min(temp[key])) / 2)
                
            return [z_unique, high, low, mid]

        self.table_B1_z, self.table_B1_Mz_div_BSL_high, self.table_B1_Mz_div_BSL_low, self.table_B1_Mz_div_BSL_mid = _find_high_low(z_Mz_div_BSL)
        self.table_B1_z, self.table_B1_My_div_BSL_high, self.table_B1_My_div_BSL_low, self.table_B1_My_div_BSL_mid = _find_high_low(z_My_div_BSL)
        
    
    # -- Mz_div_BSL as a function of z ----------------------------------------    
    def calc_Mz_div_BSL(self, z):
        a = self.Mz_div_BSL_of_z_param[0]
        b = self.Mz_div_BSL_of_z_param[1]
        return self.fit_func_Mz_div_BSL_of_z(z, a, b)
        
    def fit_func_Mz_div_BSL_of_z(self, z, a, b):
        return a + z*b
    
    def calc_curve_fit_Mz_div_BSL_of_z(self):
        z_copy = self.table_B1_z.copy()
        z_copy.extend(z_copy)
        Mz_div_BSL_copy = self.table_B1_Mz_div_BSL_high.copy()
        Mz_div_BSL_copy.extend(self.table_B1_Mz_div_BSL_low)
        param, param_cov = curve_fit(self.fit_func_Mz_div_BSL_of_z, z_copy, Mz_div_BSL_copy)
        return param
    
    # -- My_div_BSL as a function of z ----------------------------------------    
    def calc_My_div_BSL(self, z):
        a = self.My_div_BSL_of_z_param[0]
        b = self.My_div_BSL_of_z_param[1]
        return self.fit_func_My_div_BSL_of_z(z, a, b)
        
    def fit_func_My_div_BSL_of_z(self, z, a, b):
        return a + z*b
    
    def calc_curve_fit_My_div_BSL_of_z(self):
        z_copy = self.table_B1_z.copy()
        z_copy.extend(z_copy)
        My_div_BSL_copy = self.table_B1_My_div_BSL_high.copy()
        My_div_BSL_copy.extend(self.table_B1_My_div_BSL_low)
        param, param_cov = curve_fit(self.fit_func_My_div_BSL_of_z, z_copy, My_div_BSL_copy)
        return param
    
    
    
    
    
    
    
    
    
    # -- z as a function of Mz/BSL curve fit ---------------------------------- 
    def calc_z_of_Mz_div_BSL(self, Mz_div_BSL, round_bool=True):
        a = self.z_of_Mz_div_BSL_fit_params[0]
        b = self.z_of_Mz_div_BSL_fit_params[1]
        c = self.z_of_Mz_div_BSL_fit_params[2]
        z = self.fit_func_z_of_Mz_div_BSL(Mz_div_BSL, a, b, c)
        if round_bool:
            return round(z)
        return z
    
    def fit_func_z_of_Mz_div_BSL(self, Mz_div_BSL, a, b, c):
        return a + b*Mz_div_BSL + c*Mz_div_BSL**2
        
    def calc_curve_fit_z_of_Mz_div_BSL(self):
        param, param_cov = curve_fit(self.fit_func_z_of_Mz_div_BSL, self.Mz_div_BSL_mid, self.z)
        return param
    
    # -- z as a function of My/BSL curve fit ----------------------------------
    def calc_z_of_My_div_BSL(self, My_div_BSL, round_bool=True):
        a = self.z_of_My_div_BSL_fit_params[0]
        b = self.z_of_My_div_BSL_fit_params[1]
        c = self.z_of_My_div_BSL_fit_params[2]
        z = self.fit_func_z_of_My_div_BSL(My_div_BSL, a, b, c)
        if round_bool:
            return round(z)
        return z
    
    def fit_func_z_of_My_div_BSL(self, My_div_BSL, a, b, c):
        return a + b*My_div_BSL + c*My_div_BSL**2
        
    def calc_curve_fit_z_of_My_div_BSL(self):
        param, param_cov = curve_fit(self.fit_func_z_of_My_div_BSL, self.My_div_BSL_mid, self.z)
        return param

        








    # -- 'get' functions ------------------------------------------------------    
    def get_table_B1_z(self):
        return self.table_B1_z
    
    def get_table_B1_Mz_div_BSL_high(self):
        return self.table_B1_Mz_div_BSL_high
    
    def get_table_B1_Mz_div_BSL_low(self):
        return self.table_B1_Mz_div_BSL_low
    
    def get_table_B1_Mz_div_BSL_mid(self):
        return self.table_B1_Mz_div_BSL_mid
    
    def get_table_B1_My_div_BSL_high(self):
        return self.table_B1_My_div_BSL_high
    
    def get_table_B1_My_div_BSL_low(self):
        return self.table_B1_My_div_BSL_low
    
    def get_table_B1_My_div_BSL_mid(self):
        return self.table_B1_My_div_BSL_mid
    
    def get_Mz_div_BSL(self):
        return self.Mz_div_BSL_mid
    
    def get_My_div_BSL(self):
        return self.My_div_BSL_mid
    
    def get_z(self):
        return self.z
    
    def get_z_continuous(self):
        return self.z_continuous
    
    def get_My_div_BSL_curve_fit(self):
        return self.My_div_BSL_curve_fit
    
    def get_Mz_div_BSL_curve_fit(self):
        return self.Mz_div_BSL_curve_fit
        
    # -- Update all -----------------------------------------------------------
    def update_all_values(self):
        
        self.calc_high_and_low_boot_moments_divided_by_BSL_from_table_B1()
        
        self.Mz_div_BSL_of_z_param = self.calc_curve_fit_Mz_div_BSL_of_z()
        self.My_div_BSL_of_z_param = self.calc_curve_fit_My_div_BSL_of_z()
            
        z_start = max(self.table_B1_z)
        z_step  = 0.5
        
        self.z = self.table_B1_z.copy()
        self.Mz_div_BSL_mid = self.table_B1_Mz_div_BSL_mid.copy()
        self.My_div_BSL_mid = self.table_B1_My_div_BSL_mid.copy()

        i=1
        while True:
            z_new = z_start+z_step*i
            if z_new <= self.z_max:
                self.z.append(z_new)
                self.Mz_div_BSL_mid.append(self.calc_Mz_div_BSL(z_new))
                self.My_div_BSL_mid.append(self.calc_My_div_BSL(z_new))
                i=i+1
            else:
                break
            
            
            
            
            
            
            
            
            
        self.z_of_Mz_div_BSL_fit_params = self.calc_curve_fit_z_of_Mz_div_BSL()
        self.z_of_My_div_BSL_fit_params = self.calc_curve_fit_z_of_My_div_BSL()
            
            
        
        self.z_continuous = createLinearArray(min(self.table_B1_z), self.z_max, 0.1)
        self.Mz_div_BSL_curve_fit = []
        self.My_div_BSL_curve_fit = []
        for z_value in self.z_continuous:
            self.Mz_div_BSL_curve_fit.append(self.calc_Mz_div_BSL(z_value))
            self.My_div_BSL_curve_fit.append(self.calc_My_div_BSL(z_value))
           
        self.Mz_div_BSL_continuous = createLinearArray(min(self.Mz_div_BSL_mid), max(self.Mz_div_BSL_mid), 0.1)
        self.z_of_Mz_div_BSL_curve_fit = []
        for Mz_div_BSL_value in self.Mz_div_BSL_continuous:
            self.z_of_Mz_div_BSL_curve_fit.append(self.calc_z_of_Mz_div_BSL(Mz_div_BSL_value, round_bool=False))
            
        self.My_div_BSL_continuous = createLinearArray(min(self.My_div_BSL_mid), max(self.My_div_BSL_mid), 0.1)
        self.z_of_My_div_BSL_curve_fit = []
        for My_div_BSL_value in self.My_div_BSL_continuous:
            self.z_of_My_div_BSL_curve_fit.append(self.calc_z_of_My_div_BSL(My_div_BSL_value, round_bool=False))


   
    # -- Plots ----------------------------------------------------------------
    def plot_boot_moments_divided_by_BSL(self):
        fig, axs = plt.subplots(1,2, figsize=(14,7))
        fig.suptitle('ISO 11088 Table B1')    
        
        col=0
        axs[col].plot(self.table_B1_z, self.table_B1_Mz_div_BSL_high, label='Table B1 High', color='gray', ls='-')
        axs[col].plot(self.table_B1_z, self.table_B1_Mz_div_BSL_low, label='Table B1 Low', color='gray', ls='--')
        axs[col].plot(self.table_B1_z, self.table_B1_Mz_div_BSL_mid, 'o', label='Table B1 Mid', color='tab:purple')
        axs[col].plot(self.z_continuous, self.Mz_div_BSL_curve_fit, label='Table B1 curve fit high/low', color='tab:green')
        # axs[col].plot(self.z, self.Mz_div_BSL_mid, 'o', label='Extended', ms=3, color='tab:red')
        axs[col].set_xlabel('z [-]')
        axs[col].set_ylabel('Mz/BSL [N]')
        axs[col].legend()
        
        col=1
        axs[col].plot(self.table_B1_z, self.table_B1_My_div_BSL_high, label='Table B1 High', color='gray', ls='-')
        axs[col].plot(self.table_B1_z, self.table_B1_My_div_BSL_low, label='Table B1 Low', color='gray', ls='--')
        axs[col].plot(self.table_B1_z, self.table_B1_My_div_BSL_mid, 'o', label='Table B1 Mid', color='tab:purple')
        axs[col].plot(self.z_continuous, self.My_div_BSL_curve_fit, label='Table B1 curve fit high/low', color='tab:green')
        # axs[col].plot(self.z, self.My_div_BSL_mid, 'o', label='Extended', ms=3, color='tab:red')
        axs[col].set_xlabel('z [-]')
        axs[col].set_ylabel('My/BSL [N]')
        axs[col].legend()
        
        plt.tight_layout() # Adjusts layout so x and y labels don't overlap other plots
    
    
    def plot_z_of_boot_moments_div_BSL(self):
        fig, axs = plt.subplots(1,2, figsize=(14,7))
        fig.suptitle('ISO 11088 Z as a function of boot moment/BSL')    
        
        col=0
        axs[col].plot(self.table_B1_Mz_div_BSL_high, self.table_B1_z,  label='Table B1 High', color='gray', ls='-')
        axs[col].plot(self.table_B1_Mz_div_BSL_low, self.table_B1_z, label='Table B1 Low', color='gray', ls='--')
        axs[col].plot(self.table_B1_Mz_div_BSL_mid, self.table_B1_z, 'o', label='Table B1 Mid', color='tab:purple')
        axs[col].plot(self.Mz_div_BSL_continuous, self.z_of_Mz_div_BSL_curve_fit, label='z of Mz/BSL curve fit', color='tab:green')
        axs[col].set_xlabel('Mz/BSL [N]')
        axs[col].set_ylabel('z [-]')
        axs[col].legend()
        
        col=1
        axs[col].plot(self.table_B1_My_div_BSL_high, self.table_B1_z, label='Table B1 High', color='gray', ls='-')
        axs[col].plot(self.table_B1_My_div_BSL_low, self.table_B1_z, label='Table B1 Low', color='gray', ls='--')
        axs[col].plot(self.table_B1_My_div_BSL_mid, self.table_B1_z, 'o', label='Table B1 Mid', color='tab:purple')
        axs[col].plot(self.My_div_BSL_continuous, self.z_of_My_div_BSL_curve_fit, label='z of My/BSL curve fit', color='tab:green')
        axs[col].set_xlabel('My/BSL [N]')
        axs[col].set_ylabel('z [-]')
        axs[col].legend()
        
        plt.tight_layout() # Adjusts layout so x and y labels don't overlap other plots
    
    
    
    
    
    
if __name__ == '__main__':
    plt.close('all')
    
    ISO11088 = ISO11088()
    ISO11088.plot_boot_moments_divided_by_BSL()
    ISO11088.plot_z_of_boot_moments_div_BSL()
    


