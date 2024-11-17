from Phidget22.Phidget import * 
from Phidget22.Devices.VoltageRatioInput import *
import numpy as np
import logging
import json

class PhidgetHandler():

    def __init__(self):
        """Class to control the phidget 1046_1 Wheatstone bridge data device
        """
        # Setup the internal logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        console_handler  = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        # self.logger.addHandler(console_handler)
        
        # load the calibration data
        with open('load_cell_calibration.json') as f:
            cal_data = json.load(f)
            self.my_cal = cal_data['My']
            self.mz_cal = cal_data['Mz']
            self.logger.info("Loaded calibration data: My = " + str(self.my_cal) + " Mz = " + str(self.mz_cal))
        
        # variables to track internal data
        self.recent_samples = np.array([0.0, 0.0])
        self.sample_index = 0
        self.recent_measurement = 0
        
        # setup an object referencing channel 0 of bridge
        self.ch = VoltageRatioInput()

        # set callback function to handle new data
        self.ch.setOnVoltageRatioChangeHandler(self.onVoltageRatioChange)
        self.ch.openWaitForAttachment(5000)
        
        # self.ch.setBridgeGain(BridgeGain.BRIDGE_GAIN_128)

        # minDataInterval = self.ch.getMinDataInterval()
        # print("Phidget MinDataInterval: " + str(minDataInterval))
        # minDataInterval = self.ch.getMaxDataInterval()
        # print("Phidget MaxDataInterval: " + str(minDataInterval))
        self.ch.setDataInterval(10)
        
        # voltageRatio = self.ch.getVoltageRatio()
        # print("Phidget VOLTERATIO: " + str(voltageRatio))
        
        self.ch.setBridgeGain(BridgeGain.BRIDGE_GAIN_128)
        
    def onVoltageRatioChange(self, other_self, voltageRatio):  # other self is reference to phidget
        """Callback function for phidget device when voltage ratio changes
        
        Voltage ratio measurement is captured by self.recent_measurement with 
        minimal sample averaging. Sample rate will be sent to 200Hz so each 
        measurement at 100hz will be the average of the past two measurements.
        Args:
            other_self (_type_): Unkown, but is kept from phidget documentation
            https://www.phidgets.com/?view=code_samples&lang=Python
            voltageRatio (float): Voltage ratio sampled by the phidget
        """
        # update np array with most recent sample at oldest index then take mean
        self.recent_samples[self.sample_index] = voltageRatio
        self.sample_index ^= 1
        self.recent_measurement = np.mean(self.recent_samples)
        # print(self.interpret_voltage_data(np.array(self.recent_measurement), True))
        
    def interpret_voltage_data(self, data: np.array, my_data: bool) -> np.array:
        """Takes voltage ratio data from phidget and converts to force in Newtons
        
        Args:
            data (np.array): voltage ratio data from phidget array
            my_data (bool): True if data is from My sensor, False if data is from Mz
        Returns:
            np.array: force in Newtons for each sample
        """
        # convert data to kg
        if my_data:
            weights = (data + self.my_cal['offset']) * self.my_cal['gain']
            weights *= self.my_cal['lever_arm']
        else:
            weights = (data + self.mz_cal['offset']) * self.mz_cal['gain']
            weights *= self.mz_cal['lever_arm']
        # forces = weights * 9.81  # convert to N
        forces = weights  # Handling the force conversion with the phidget UI
        return forces
        
    def close(self) -> None:
        self.ch.close()
    
    
if __name__ == "__main__":
    phidget = PhidgetHandler()
    
    try:
        input("press enter to exit")
    except:
        pass
    
    phidget.close()
    # forces = []
    # for i in range(100):
    #     forces[i] = phidget.recent_measurement
    #     forces = phidget.interpret_voltage_data(forces)
 
 