# A Ski Binding Data Collection Tool for AlpenFlow Bindings
by Alex Lewis

![DINGUI](/img/dinGui.png)

## Overview
A series of simultanious force and displacement measurements are required to calculate the DIN setting of a binding or evaluate its performance as a ski boot releases in a controlled test setup. To alievate the serious heartache involved with manual data collection of a dynamic boot release, I have created this python application to provides these functionalities:
* Automate data collection using a phidget strain gauge data logger and a Time of Flight (TOF) sensor 
* Corresponding firmware for an arduino that samples the sensor and interacts with the python backend via serial
* Automatic connection to the Arduino with an acknowledgment from the micro upon connection
* An interactive PyQT GUI that allows user to configure the data collection setup such as define which TOF sensor to use
* An algorithm that compensates for discrete TOF measurements by interpolating the continious displacement/force sweep to select values 
* The ability to log data to csvs for future processing
* Options to overlay various boot releases or view single releases with additional measurement granularity

## User Setup
This data collection setup needs calibration data for the load cell since it is a series of strain gauges in a Wheatstone bridge format. The lever arm of the test aparatus must also be provided. Enter this information into `load_cell_calibration.json` and the calibration data will automatically be handled by the application. 

As noted earlier, the user does not need to manually add the microcontroller COM port. Same goes for the Phidget data logger. However, both of the Arduino and Phidget softwares will have to be installed on your machine to support the libraries used. 

### Hardware
![hardware](/img/Hardware_Setup.png)

This din setup requires these peices of hardware:
* 3000lb Load Cell
* Phidget 6061 bridge logger
* Arduino (or frankly any other micro)
* x2 ST VL53L4CD TOF sensors
* A nifty DIN setup the AlpenFlow guys made

### Installation
The dependencies for this application can be handled with 

# TODO Add requirements and make sure this is right
```
pip install -r requirements.tt
```
The application can be initiated with
```
python AlpenFlowDinApp.py
```

### Acknowledgments
Major kudos go out to the AlpenFlow engineers, Steven and Jesse, for providing their input durring this development and providing extremely thorough documentation of requirements!

Here's another image of the GUI running for yucks

![other_gui_img](/img/din_gui_running.png)