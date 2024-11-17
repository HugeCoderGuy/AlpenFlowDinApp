# A Ski Binding Data Collection Tool for [AlpenFlow Design](https://www.alpenflowdesign.com/?srsltid=AfmBOoq_nodg2ozLw1kKz-2c_BeYo06hfF1Qi-odZfMAEKACfAORmYSZ)
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

With the current configurations, digital pin 7 is used to turn on TOF sensor for Mz and digital pin 8 is for TOF sensor on the My axis. 

Arduino Pinout to Tof Sensor:
* Red to Arduino 5V
* Black to Arduino GRND
* Yellow to Arduino SCL
* Blue to Arduino SDA

Then the Tof select from the arduino is controlled using
* XSHUT of My to Arduino 8
* XSHUT of Mz to ARduino 7

Refer to `/DistanceSampler/DistanceSampler.ino` for notes on GPIO controlling the Tof sensor in use and ![this link](https://learn.adafruit.com/adafruit-vl53l4cd-time-of-flight-distance-sensor/pinouts) to find adafruit's documentation on the Tof sensor pinout.

### Installation
The dependencies for this application can be handled with 

```
pip install -r requirements.txt
```
The application can be initiated with
```
python3 .\AlpenFlowDinApp.py
```

## Data Processing Notes
Below are a series of notes that are important for user understanding of how the data is processed:

<b>First</b>, he data from the TOF sensor is discrete mm measurements. Of course these are noisy when being sampled at 100Hz (status quo). To counteract that, a moving average is reported by the micro noting the average of the last n values. To adjust the number of values in the moving average, refer to this code in the .ino file
```
const int numb_samples = 2;
int samples[numb_samples] = {0, 0};
```
Example change to 4 sample moving average would be setting `numb_samples = 4` and `samples[numb_samples] = {0, 0, 0, 0}`. 

<b>Second</b>, the python code processes the distances and forces data once it breaks from its sampling window after it has recieved n samples greater than 10mm of travel. Since the TOF sensor doesn't discriminate between .1mm and .9mm, I use an averaging algorithm for the displayed release curve. This averaging algorithm for distance x takes the second half of force measurements with x-1 and averages them with the first half of x force measurements. Assuming we have a constant boot release speed (which is part of the din standard), we are effectively saying that the force at 2mm is the average of all sampled forces between distances 1.5mm and 2mm. This <u>assumption is only valid of the release speed is constant.</u> To help improve the consistency of the release speed, the amount of time spent at each displacement is displayed in the tabluar view. 

To handle the instances when distance x isn't sampled, the algorithm just takes the mean of samples at distance x + 1mm. Ultametly though, the save data button saves both the processed and raw data enabling the user to do their own post processing as they see fit. 

## Shopping List:
* [TOF sensor](https://www.adafruit.com/product/5396)
* [Solder Breadboard](https://www.adafruit.com/product/1608) or a [shield like this](https://learn.adafruit.com/adafruit-proto-shield-arduino/overview)
* [Arduino Equivalent](https://www.adafruit.com/product/2488)

## Acknowledgments
Major kudos go out to the AlpenFlow engineers, Steven and Jesse, for providing their input durring this development and providing extremely thorough documentation of requirements!

Here's another image of the GUI running for yucks

![other_gui_img](/img/din_gui_running.png)
