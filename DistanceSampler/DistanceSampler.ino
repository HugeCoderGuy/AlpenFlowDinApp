#include <Arduino.h>
#include <Wire.h>
#include <vl53l4cd_class.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <assert.h>
#include <stdlib.h>

#define DEV_I2C Wire

// Components.
VL53L4CD dist_sensor(&DEV_I2C, A1);
int My_Pin = 8;
int Mz_Pin = 7;
int LED_PIN = 13;

bool testing_my = false;

const int numb_samples = 5;
int samples[numb_samples] = {0, 0, 0, 0, 0};
int indexer = 0;

byte average() {
  int res=0;
  for (int i=0; i<numb_samples; i++) {
    res += samples[i];
  }
  return res/numb_samples;
}

/* Setup ---------------------------------------------------------------------*/
void SetupMy(bool My) {
  /* Function to use xShut pin to decide which dist sensor to use
   *  input:
   *    My (bool): True if you're setting up My. False if setting up Mz
   */

  if (My) {
    digitalWrite(My_Pin, HIGH);
    digitalWrite(Mz_Pin, LOW);
    testing_my = true;
  }
  else {
    digitalWrite(My_Pin, HIGH);
    digitalWrite(Mz_Pin, LOW);
    testing_my = false;
  }
  delay(10);  // Allow sensor to power up
  
  // Configure VL53L4CD satellite component.
  dist_sensor.begin();

  // Program the highest possible TimingBudget, without enabling the
  // low power mode. This should give the best accuracy
  dist_sensor.VL53L4CD_SetRangeTiming(10, 0);

  // Start Measurements
  dist_sensor.InitSensor();

  dist_sensor.VL53L4CD_StartRanging();

}

void set_sensor_state() {
  /* Read serial input from computer to decide which dist sensor to be using. 
   *  input:
   *    None: write 1 to serial line means use My. 0 means Mz
   */
  if (Serial.available() > 0) { // Check if there is data in the serial buffer
    int input = Serial.parseInt(); // Read the integer from the serial buffer
    
    if ((input == 1) and !(testing_my)) {
      SetupMy(true);
      digitalWrite(LED_PIN, HIGH);
    }
    else if ((input == 2) and testing_my) {
      SetupMy(false);
      digitalWrite(LED_PIN, LOW);
    }
    else if (input == 3) {
      Serial.println("AlpenFlow");
    }
  }
}

void setup()
{
  // Initialize serial for output.
  Serial.begin(115200);

  pinMode(LED_PIN, OUTPUT);

  // Initialize I2C bus.
  DEV_I2C.begin();

  // Default to the My axis test
  SetupMy(true);
  digitalWrite(LED_PIN, HIGH);  // indicate My mode

  
  unsigned long StartTime = millis();
}

void loop()
{
  uint8_t NewDataReady = 0;
  VL53L4CD_Result_t results;
  uint8_t status;
  char report[64];
  byte measurement;
  
  // Check Serial input to see if user requests changing test axis
  set_sensor_state();
  
  // Wait for sensor to make measurement
  do {
    status = dist_sensor.VL53L4CD_CheckForDataReady(&NewDataReady);
  } while (!NewDataReady);

  if ((!status) && (NewDataReady != 0)) {
    // (Mandatory) Clear HW interrupt to restart measurements
    dist_sensor.VL53L4CD_ClearInterrupt();

    // Read measured distance. RangeStatus = 0 means valid data
    dist_sensor.VL53L4CD_GetResult(&results);
    if (results.distance_mm > 255) {
      measurement = 254;
    }
    else {
      measurement = results.distance_mm;
    }
    if (measurement == 0) {
      // handle bad measurement (0) with last measurement
      measurement = samples[indexer];
    }
    samples[indexer] = measurement;
    indexer += 1;
    if (indexer == numb_samples) {
      indexer = 0;
    }
    Serial.write(average());
  }
}
