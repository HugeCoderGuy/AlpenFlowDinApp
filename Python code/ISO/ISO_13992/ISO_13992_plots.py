1#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  3 12:32:23 2024

@author: stevenwaal
"""

import matplotlib.pyplot as plt
import colorsys
from lib.ISO.ISO_11088.ISO_11088 import ISO11088
from lib.ISO.ISO_13992.ISO_13992_bench_test import ISO13992BenchTest
from lib.ISO.ISO_13992.ISO_13992_bench_test_curve_fit import ISO13992BenchTestCurveFit
from lib.ISO.ISO_13992.ISO_13992 import ISO13992
from lib.ISO.ISO_13992.abc_ISO_13992_plots import ABCISO13992Plots
from lib.binding_mechanisms.sonora_heel_latch_v2 import SonoraHeelLatchV2
from lib.binding_mechanisms.alpenflow_89_heel_latch import Alpenflow89HeelLatch
from lib.scolors.mixed_colors_hsl import MixedColorsHSL

class ISO13992Plots():
    
    def __init__(self, test_axis, object_list):
        
        self.object_list = object_list
        
        self.ISO13992 = ISO13992()
        self.ISO11088 = ISO11088()
        
        if test_axis=="My":
            self.test_axis = "My"
        elif test_axis=="Mz":
            self.test_axis = "Mz"
        else:
            raise Exception('Invalid selection for test_axis. Choose either "My" or "Mz".')
        
        # Error checking to make sure all objects in object_list contain the same type of data
        for obj in object_list:
            if isinstance(obj, ISO13992PlotContainer):
                pass
            else:
                raise Exception('ERROR: Objects in object_list must be from the class ISO13992PlotContainer')
            if self.test_axis == obj.get_plot_object().get_test_axis():
                pass
            else:
                raise Exception('Mismatched object in object_list. All objects in object_list must have the same value for test_axis (My or Mz).')
        
        # Create list of H values for colors for plots
        self.mixed_color_object = MixedColorsHSL(15, 4)
        self.z_color_list = self.mixed_color_object.get_H_list_mixed()    
        
    def plot_boot_moment_divided_by_BSL_vs_elasticity(self, z_scale='both'):
        if not (z_scale=='both' or z_scale=='ISO 13992' or z_scale=='ISO 11088'):
            raise Exception("ERROR: Incorrect selection for z_scale. Choose either 'both', 'ISO 13992', or 'ISO11088'")
        
        fig, ax1 = plt.subplots(figsize=(12,10))
        
        for obj in self.object_list:
            plot_object = obj.get_plot_object()
            linestyle = obj.get_linestyle()
            color = obj.get_color()
            z_order = obj.get_z_order()
            ax1.plot(plot_object.get_elasticity(), plot_object.get_boot_moments_divided_by_BSL(), ls=linestyle, label=plot_object.get_legend_string(), color=color, zorder=z_order)

        ax1.legend(bbox_to_anchor=(1.15, 1), loc="upper left")
        plt.subplots_adjust(right=0.6)
        ax1.set_xlabel('Elasticity [mm]')
        if self.test_axis=='My':
            ax1.set_ylabel('My/BSL [N]')
        elif self.test_axis=='Mz':
            ax1.set_ylabel('Mz/BSL [N]')
        ax1.set_title(f"Direction: {self.get_test_axis()}")
        self.add_z_scale_to_plot(ax1, z_scale)
            
    def plot_moments_vs_elasticity(self):
        pass

    # -- Utility functions ----------------------------------------------------    
    def add_z_scale_to_plot(self, axis, z_scale):
        
        # Determine axis limits of plot
        axis_x_limits = axis.get_xlim()
        axis_x_range = axis_x_limits[1] - axis_x_limits[0]
        
        if z_scale=='both' or z_scale=='ISO 13992':
            if self.get_test_axis()=="My":
                Mb_div_BSL = self.ISO13992.get_My_div_BSL()
            elif self.get_test_axis()=="Mz":
                Mb_div_BSL = self.ISO13992.get_Mz_div_BSL()
            else:
                raise Exception('Invalid selection for test_axis. Choose either "My" or "Mz".')
            
            z = self.ISO13992.get_z()
            
            # Add text to plot for Z values
            text_x_percentage = 1.025 # X position of text, specified as a "percentage" of the x limits
            text_x_pos = (text_x_percentage*axis_x_range)+axis_x_limits[0]
            
            i=0
            for z_value in z:
                if z_value.is_integer():
                    axis.axhline(y = Mb_div_BSL[i], color = '0.8', linestyle = '-', linewidth=1, zorder=-100)
                    t = axis.text(text_x_pos, Mb_div_BSL[i], ('%i'%z_value), backgroundcolor = 'w', verticalalignment='center')
                    if z_value>10:
                        t.set_bbox(dict(facecolor='w', pad=0.7))
                    else:
                        t.set_bbox(dict(facecolor='w', edgecolor='none'))
                i=i+1
            axis.text(1.025,1.01, 'ISO 13992', transform=axis.transAxes, rotation='vertical')
            
        if z_scale=='both' or z_scale=='ISO 11088':
            if self.get_test_axis()=="My":
                Mb_div_BSL = self.ISO11088.get_My_div_BSL()
            elif self.get_test_axis()=="Mz":
                Mb_div_BSL = self.ISO11088.get_Mz_div_BSL()
            else:
                raise Exception('Invalid selection for test_axis. Choose either "My" or "Mz".')
            
            z = self.ISO11088.get_z()
            
            # Add text to plot for Z values
            text_x_percentage = 1.08 # X position of text, specified as a "percentage" of the x limits
            text_x_pos = (text_x_percentage*axis_x_range)+axis_x_limits[0]
            
            i=0
            for z_value in z:
                if z_value.is_integer():
                    axis.axhline(y = Mb_div_BSL[i], xmax=text_x_percentage, color = '0.8', linestyle = ':', linewidth=1, zorder=-100, clip_on=False)
                    t = axis.text(text_x_pos, Mb_div_BSL[i], ('%i'%z_value), verticalalignment='center')
                    if z_value>10:
                        t.set_bbox(dict(facecolor='w', pad=0.5))
                    else:
                        t.set_bbox(dict(facecolor='w', edgecolor='none'))
                i=i+1
            axis.text(1.08,1.01, 'ISO 11088', transform=axis.transAxes, rotation='vertical')
        
        
    def get_test_axis(self):
        return self.test_axis
    
    




class ISO13992PlotContainer():
    
    def __init__(self, plot_object, color_selection='Auto', linestyle_selection='Auto'):
       
        self.mixed_color_object = MixedColorsHSL(15, 4)
        self.z_color_list = self.mixed_color_object.get_H_list_mixed() 
        # self.mixed_color_object.plot_mixed_colors()
        # self.mixed_color_object.plot_unmixed_colors()
        
        self.ISO13992 = ISO13992()
        
        # plot_object is an object that implements the abstract class
        # ABCISO13992Plots
        if not isinstance(plot_object, ABCISO13992Plots):
            raise Exception('ERROR: plot_object must be child of class ABCISO13992Plots')
        self.plot_object = plot_object
        
        if isinstance(color_selection, int):
            if color_selection>len(self.z_color_list) or color_selection<0:
                raise Exception(f'ERROR: Color integer out of bounds. Choose an integer between 0 and {len(self.z_color_list)} (inclusive)')
            self.color_selection = color_selection
        elif color_selection=='Auto':
            self.color_selection = color_selection
        else:
            raise Exception('ERROR: Incorrect value for color_selection. Choose either "Auto" or an integer.' )
               
        #todo: Add error checking for linestyle_selection
        self.linestyle_selection = linestyle_selection
        
        # Linestyle
        if self.linestyle_selection=='Auto':
            if isinstance(self.plot_object, ISO13992BenchTest):
                self.linestyle=':'
            elif isinstance(self.plot_object, ISO13992BenchTestCurveFit):
                self.linestyle='-'
            elif isinstance(self.plot_object, SonoraHeelLatchV2) or isinstance(self.plot_object, Alpenflow89HeelLatch):
                self.linestyle='-'
            else:
                self.linestyle='-'
        else:
            self.linestyle=self.linestyle_selection
        
        # Color
        # Set default color to gray
        hue = 0
        saturation = 0
        lightness = 0.5
        
        self.z_order = 0
        
        if isinstance(self.plot_object, ISO13992BenchTest):
            lightness = 0.7
            self.z_order = 0
        elif isinstance(self.plot_object, ISO13992BenchTestCurveFit):
            lightness = 0.7
            self.z_order = 5
        elif isinstance(self.plot_object, SonoraHeelLatchV2) or isinstance(self.plot_object, Alpenflow89HeelLatch):
            lightness = 0.45
            self.z_order = 10
        
        
        if self.color_selection == 'Auto':
            max_boot_heel_force = max(self.plot_object.get_boot_moments_divided_by_BSL())
            if self.plot_object.get_test_axis()=="My":
                z = self.ISO13992.calc_z_of_My_div_BSL(max_boot_heel_force)
            elif self.plot_object.get_test_axis()=="Mz":
                z = self.ISO13992.calc_z_of_Mz_div_BSL(max_boot_heel_force)
            else:
                raise Exception('Invalid selection for test_axis. Choose either "My" or "Mz".')
            
            try:
                hue = self.z_color_list[z-1]
            except IndexError:
                hue = self.z_color_list[len(self.z_color_list)-1]
                
            saturation=1
                
        elif isinstance(self.color_selection, int):
            if not self.color_selection == 0:
                hue = self.z_color_list[self.color_selection-1]
                saturation=1
        self.color = colorsys.hls_to_rgb(hue, lightness, saturation)

    
    def get_plot_object(self):
        return self.plot_object
    
    def get_linestyle(self):
        return self.linestyle
    
    def get_color(self):
        return self.color    
    
    def get_z_order(self):
        return self.z_order
        
    
if __name__=='__main__':
    
    from lib.boots import boot
    from lib.ISO.ISO_13992 import ISO_13992_bench_test
    
    plt.close('all')
    
    filepath1 = '/Users/stevenwaal/Documents/Alpenflow Design/Python Scripts/testing/testing_data/My/My, 05-03-2024, Sonora on Chamonix, Z7 - Trial 1.csv'
    boot1 = boot.Boot('Tecnica Zero G Tour Pro', '270-275')
    trial1 = ISO_13992_bench_test.ISO13992BenchTest(filepath1, 7, boot1, 'My', 'digital', 'Sonora, My, Trial 1, Z~7')

    filepath2 = '/Users/stevenwaal/Documents/Alpenflow Design/Python Scripts/testing/testing_data/My/My, 05-03-2024, Sonora on Chamonix, Z7 - Trial 2.csv'
    boot2 = boot.Boot('Tecnica Zero G Tour Pro', '270-275')
    trial2 = ISO_13992_bench_test.ISO13992BenchTest(filepath2, 7, boot2, 'My', 'digital', 'Sonora, My, Trial 2, Z~7')

    filepath3 = '/Users/stevenwaal/Documents/Alpenflow Design/Python Scripts/testing/testing_data/My/My, 05-03-2024, Sonora on Chamonix, Z7 - Trial 3.csv'
    boot3 = boot.Boot('Tecnica Zero G Tour Pro', '270-275')
    trial3 = ISO_13992_bench_test.ISO13992BenchTest(filepath3, None, boot3, 'My', 'digital', 'Sonora, My, Trial 3, Z~7')
    
    object_list = []
    object_list.append(ISO13992PlotContainer(trial1, color_selection=2, linestyle_selection='-'))
    object_list.append(ISO13992PlotContainer(trial2, linestyle_selection='-'))
    object_list.append(ISO13992PlotContainer(trial3))
    
    iso_plots = ISO13992Plots('My', object_list)
    iso_plots.plot_boot_moment_divided_by_BSL_vs_elasticity()
    
    
    iso_plots_Mz = ISO13992Plots('Mz', [])
    iso_plots_Mz.plot_boot_moment_divided_by_BSL_vs_elasticity()
    
    print()
    print()
    print('*****************************************')
    print('* Celebrate!! All of the tests passed!! *')
    print('*****************************************')
    print()
    print()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    