#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 10:07:52 2024

@author: stevenwaal
"""
import pandas
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit 
from lib.smath import increasing
from lib.ISO.ISO_11088.ISO_11088 import ISO11088

class ISO13992():
    def __init__(self, z_max=15):
        
        self.z_max = z_max
        
        table_2_file_path_and_name = '/Users/stevenwaal/Documents/Alpenflow Design/Python Scripts/lib/ISO/ISO_13992/ISO 13992 Table 2.csv'
        self.table_2 = pandas.read_csv(table_2_file_path_and_name) # Read CSV into a pandas dataframe
        
        self.update_all_values()
        
    def calc_boot_moments_div_BSL(self):
        self.table_2_Mz_div_BSL = []
        self.table_2_My_div_BSL = []
        i=0
        for z_value in self.table_2_z:
            self.table_2_Mz_div_BSL.append(self.table_2_Mz[i]/(self.table_2_BSL[i]/1000))
            self.table_2_My_div_BSL.append(self.table_2_My[i]/(self.table_2_BSL[i]/1000))
            i=i+1
        
    # -- Expanded Table 2 -----------------------------------------------------
    def calc_expanded_table_2(self):
        z_start = 10
        z_step  = 0.5
        
        self.z = self.table_2_z.copy()
        self.Mz = self.table_2_Mz.copy()
        self.My = self.table_2_My.copy()
        self.BSL = self.table_2_BSL.copy()
        self.Mz_div_BSL = self.table_2_Mz_div_BSL.copy()
        self.My_div_BSL = self.table_2_My_div_BSL.copy()

        i=1
        while True:
            z_new = z_start+z_step*i
            if z_new <= self.z_max:
                self.z.append(z_new)
                Mz = self.calc_Mz_of_z(z_new)
                My = self.calc_My_of_z(z_new)
                BSL = self.calc_BSL_of_z(z_new)
                self.Mz.append(Mz)
                self.My.append(My)
                self.BSL.append(BSL)
                self.Mz_div_BSL.append(Mz/(BSL/1000))
                self.My_div_BSL.append(My/(BSL/1000))
                i=i+1
            else:
                break
        
    # -- Mz as a function of Z curve fit --------------------------------------
    def calc_Mz_of_z(self, z):
        return z*10
         
    # -- My as a function of Z curve fit --------------------------------------
    def calc_My_of_z(self, z):
        a = self.My_of_z_fit_params[0]
        b = self.My_of_z_fit_params[1]
        c = self.My_of_z_fit_params[2]
        return self.fit_func_My_of_z(z, a, b, c)
        
    def fit_func_My_of_z(self, z, a, b, c):
        return a + b*z+ c*z**2
    
    def calc_curve_fit_My_of_z(self):
        param, param_cov = curve_fit(self.fit_func_My_of_z, self.table_2_z, self.table_2_My)
        return param
    
    # -- BSL as a function of Z curve fit -------------------------------------
    def calc_BSL_of_z(self, z):
        a = self.BSL_of_z_fit_params[0]
        b = self.BSL_of_z_fit_params[1]
        c = self.BSL_of_z_fit_params[2]
        return self.fit_func_BSL_of_z(z, a, b, c)
        
    def fit_func_BSL_of_z(self, z, a, b, c):
        return a + b*z**c
    
    def calc_curve_fit_BSL_of_z(self):
        param, param_cov = curve_fit(self.fit_func_BSL_of_z, self.table_2_z, self.table_2_BSL)
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
        param, param_cov = curve_fit(self.fit_func_z_of_Mz_div_BSL, self.Mz_div_BSL, self.z)
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
        param, param_cov = curve_fit(self.fit_func_z_of_My_div_BSL, self.My_div_BSL, self.z)
        return param



    # -- 'get' Functions ------------------------------------------------------
    def get_z(self):
        return self.z
    
    def get_Mz_div_BSL(self):
        return self.Mz_div_BSL
    
    def get_My_div_BSL(self):
        return self.My_div_BSL

    # -- Update all values ----------------------------------------------------
    def update_all_values(self):
        self.table_2_z = list(self.table_2.z)
        self.table_2_Mz = list(self.table_2.Mz)
        self.table_2_My = list(self.table_2.My)
        self.table_2_BSL = list(self.table_2.BSL)
        self.calc_boot_moments_div_BSL()
        
        self.My_of_z_fit_params = self.calc_curve_fit_My_of_z()
        self.BSL_of_z_fit_params = self.calc_curve_fit_BSL_of_z()
        self.calc_expanded_table_2()
        
        self.z_of_Mz_div_BSL_fit_params = self.calc_curve_fit_z_of_Mz_div_BSL()
        self.z_of_My_div_BSL_fit_params = self.calc_curve_fit_z_of_My_div_BSL()
        
        self.ISO11088 = ISO11088()
        
        self.z_continuous = increasing.createLinearArray(min(self.z), max(self.z), 0.1)
        self.Mz_curve_fit = []
        self.My_curve_fit = []
        self.BSL_curve_fit = []
        self.Mz_div_BSL_curve_fit = []
        self.My_div_BSL_curve_fit = []
        for z_value in self.z_continuous:
            Mz = self.calc_Mz_of_z(z_value)
            My = self.calc_My_of_z(z_value)
            BSL = self.calc_BSL_of_z(z_value)
            self.Mz_curve_fit.append(Mz)
            self.My_curve_fit.append(My)
            self.BSL_curve_fit.append(BSL)
            self.Mz_div_BSL_curve_fit.append(Mz/(BSL/1000))
            self.My_div_BSL_curve_fit.append(My/(BSL/1000))
            
        self.Mz_div_BSL_continuous = increasing.createLinearArray(min(self.Mz_div_BSL), max(self.Mz_div_BSL), 0.1)
        self.z_of_Mz_div_BSL_curve_fit = []
        for Mz_div_BSL_value in self.Mz_div_BSL_continuous:
            self.z_of_Mz_div_BSL_curve_fit.append(self.calc_z_of_Mz_div_BSL(Mz_div_BSL_value, round_bool=False))
            
        self.My_div_BSL_continuous = increasing.createLinearArray(min(self.My_div_BSL), max(self.My_div_BSL), 0.1)
        self.z_of_My_div_BSL_curve_fit = []
        for My_div_BSL_value in self.My_div_BSL_continuous:
            self.z_of_My_div_BSL_curve_fit.append(self.calc_z_of_My_div_BSL(My_div_BSL_value, round_bool=False))






    
    def plot_table_2_curve_fits(self):
        fig, axs = plt.subplots(3,3, figsize=(12,12))
        fig.suptitle('ISO 13992 Table 2 Curve Fits')    
        
        row=0
        col=0
        axs[row,col].plot(self.table_2_z, self.table_2_Mz, 'o', label='Table 2 Mz')
        axs[row,col].plot(self.z_continuous, self.Mz_curve_fit, label='Mz curve fit')
        axs[row,col].set_xlabel('z [-]')
        axs[row,col].set_ylabel('Mz [Nm]')
        axs[row,col].legend()
        
        row=0
        col=1
        axs[row,col].plot(self.table_2_z, self.table_2_My, 'o', label='Table 2 My')
        axs[row,col].plot(self.z_continuous, self.My_curve_fit, label='My curve fit')
        axs[row,col].set_xlabel('z [-]')
        axs[row,col].set_ylabel('My [Nm]')
        axs[row,col].legend()
        
        row=0
        col=2
        axs[row,col].plot(self.table_2_z, self.table_2_BSL, 'o', label='Table 2 BSL')
        axs[row,col].plot(self.z_continuous, self.BSL_curve_fit, label='BSL curve fit')
        axs[row,col].set_xlabel('z [-]')
        axs[row,col].set_ylabel('BSL [mm]')
        axs[row,col].legend()
        
        row=1
        col=0
        axs[row,col].plot(self.table_2_z, self.table_2_Mz_div_BSL, 'o', label='ISO 13992 Table 2')
        axs[row,col].plot(self.z_continuous, self.Mz_div_BSL_curve_fit, label='ISO 13992 Table 2 curve fit')
        axs[row,col].plot(self.ISO11088.get_table_B1_z(), self.ISO11088.get_table_B1_Mz_div_BSL_high(), label='ISO 11088 Table B1 high', color='gray', ls='-')
        axs[row,col].plot(self.ISO11088.get_table_B1_z(), self.ISO11088.get_table_B1_Mz_div_BSL_low(), label='ISO 11088 Table B1 low', color='gray', ls='--')
        axs[row,col].set_xlabel('z [-]')
        axs[row,col].set_ylabel('Mz/BSL [N]')
        axs[row,col].legend()
        
        row=1
        col=1
        axs[row,col].plot(self.table_2_z, self.table_2_My_div_BSL, 'o', label='ISO 13992 Table 2')
        axs[row,col].plot(self.z_continuous, self.My_div_BSL_curve_fit, label='ISO 13992 Table 2 curve fit')
        axs[row,col].plot(self.ISO11088.get_table_B1_z(), self.ISO11088.get_table_B1_My_div_BSL_high(), label='ISO 11088 Table B1 high', color='gray', ls='-')
        axs[row,col].plot(self.ISO11088.get_table_B1_z(), self.ISO11088.get_table_B1_My_div_BSL_low(), label='ISO 11088 Table B1 low', color='gray', ls='--')
        axs[row,col].set_xlabel('z [-]')
        axs[row,col].set_ylabel('My/BSL [N]')
        axs[row,col].legend()
        
        row=2
        col=0
        axs[row,col].plot(self.Mz_div_BSL, self.z, 'go', label='Extended Table 2 Inverse Mz/BSL')
        axs[row,col].plot(self.Mz_div_BSL_continuous, self.z_of_Mz_div_BSL_curve_fit, label='Curve fit', color='tab:orange')
        axs[row,col].set_xlabel('Mz/BSL [N]')
        axs[row,col].set_ylabel('z [-]')
        axs[row,col].legend()
        
        row=2
        col=1
        axs[row,col].plot(self.My_div_BSL, self.z, 'go', label='Extended Table 2 Inverse My/BSL')
        axs[row,col].plot(self.My_div_BSL_continuous, self.z_of_My_div_BSL_curve_fit, label='Curve fit', color='tab:orange')
        axs[row,col].set_xlabel('My/BSL [N]')
        axs[row,col].set_ylabel('z [-]')
        axs[row,col].legend()
        
        plt.tight_layout() # Adjusts layout so x and y labels don't overlap other plots
        
        fig, axs = plt.subplots(1,2, figsize=(14,7))
        fig.suptitle('ISO 13992 and ISO 11088 Comparison')    
        
        col=0
        axs[col].plot(self.table_2_z, self.table_2_Mz_div_BSL, 'o', label='ISO 13992 Table 2', zorder=10)
        axs[col].plot(self.z_continuous, self.Mz_div_BSL_curve_fit, label='ISO 13992 Table 2 curve fit', zorder=5)
        axs[col].plot(self.ISO11088.get_table_B1_z(), self.ISO11088.get_table_B1_Mz_div_BSL_high(), label='ISO 11088 Table B1 high', color='gray', ls='-', zorder=-10)
        axs[col].plot(self.ISO11088.get_table_B1_z(), self.ISO11088.get_table_B1_Mz_div_BSL_low(), label='ISO 11088 Table B1 low', color='gray', ls='--', zorder=-10)
        axs[col].plot(self.ISO11088.get_table_B1_z(), self.ISO11088.get_table_B1_Mz_div_BSL_mid(), 'o', label='ISO 11088 Table B1 mid', color='tab:purple', zorder=0)
        axs[col].plot(self.ISO11088.get_z_continuous(), self.ISO11088.get_Mz_div_BSL_curve_fit(), label='ISO 11088 Table B1 curve fit', color='tab:green', zorder=0)
        axs[col].set_xlabel('z [-]')
        axs[col].set_ylabel('Mz/BSL [N]')
        axs[col].legend()
        
        col=1
        axs[col].plot(self.table_2_z, self.table_2_My_div_BSL, 'o', label='ISO 13992 Table 2', zorder=10)
        axs[col].plot(self.z_continuous, self.My_div_BSL_curve_fit, label='ISO 13992 Table 2 curve fit', zorder=5)
        axs[col].plot(self.ISO11088.get_table_B1_z(), self.ISO11088.get_table_B1_My_div_BSL_high(), label='ISO 11088 Table B1 high', color='gray', ls='-', zorder=-10)
        axs[col].plot(self.ISO11088.get_table_B1_z(), self.ISO11088.get_table_B1_My_div_BSL_low(), label='ISO 11088 Table B1 low', color='gray', ls='--', zorder=-10)
        axs[col].plot(self.ISO11088.get_table_B1_z(), self.ISO11088.get_table_B1_My_div_BSL_mid(), 'o', label='ISO 11088 Table B1 mid', color='tab:purple', zorder=0)
        axs[col].plot(self.ISO11088.get_z_continuous(), self.ISO11088.get_My_div_BSL_curve_fit(), label='ISO 11088 Table B1 curve fit', color='tab:green', zorder=0)
        axs[col].set_xlabel('z [-]')
        axs[col].set_ylabel('My/BSL [N]')
        axs[col].legend()
        
        plt.tight_layout() # Adjusts layout so x and y labels don't overlap other plots   

        

    def print_table_2(self):
        print()
        print()
        print('==========================================================================')
        print('                           ISO 13992 Table 2')
        print('==========================================================================')
        print()
        print('Z [-]\t\tMz [Nm]\t\tMy [Nm]\t\tBSL [mm]\t\tMz/BSL [N]\tMy/BSL [N]')
        for i in range(len(self.z)):
            print(f'{self.z[i]:4.1f}\t\t\t{self.Mz[i]:5.1f}\t\t{self.My[i]:6.1f}\t\t{self.BSL[i]:3.0f}\t\t|\t{self.Mz_div_BSL[i]:6.1f}\t\t{self.My_div_BSL[i]:6.1f}')
            if self.z[i]==10:
                print('------- interpolated from above ----------')
        print()
        print()
        
        

if __name__=='__main__':
    plt.close('all')
    
    ISO13992 = ISO13992()
    ISO13992.print_table_2()
    ISO13992.plot_table_2_curve_fits()

    
    assert ISO13992.calc_z_of_Mz_div_BSL(ISO13992.Mz_div_BSL[1]) == ISO13992.z[1]
    assert ISO13992.calc_z_of_Mz_div_BSL(ISO13992.Mz_div_BSL[len(ISO13992.z)-1]) == ISO13992.z[len(ISO13992.z)-1]
    
    assert ISO13992.calc_z_of_My_div_BSL(ISO13992.My_div_BSL[1]) == ISO13992.z[1]
    assert ISO13992.calc_z_of_My_div_BSL(ISO13992.My_div_BSL[len(ISO13992.z)-1]) == ISO13992.z[len(ISO13992.z)-1]
    
    print()
    print()
    print('*****************************************')
    print('* Celebrate!! All of the tests passed!! *')
    print('*****************************************')
    print()
    print()
    