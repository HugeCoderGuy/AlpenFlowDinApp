import serial
import logging


class SerialHandler():
    def __init__(self, comport: str='COM4', baudrate: int=115200):
        """Initalizes the serial port on the computer to talk to the arduino

        Args:
            comport (str): Name of the serial port (ex: COM4)
            baudrate (int): Speed of the serial port. Default is 115200
        """
        # Setup the internal logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        console_handler  = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        
        # Setup the serial port
        self.ser = serial.Serial(comport, baudrate, timeout=0.1)         # 1/timeout is the frequency at which the port is read
        self.ser.reset_input_buffer()  # Clear the input buffer

    def get_arduino_data(self) -> int:
        """Get the serial data transmitted by the arduino

        Returns:
            int: distance measurement broadcasted by the arduino
        """
        if self.ser.in_waiting > 0:
            byte_data = self.ser.read(1)  # Read one byte
            data = int.from_bytes(byte_data, byteorder='big')  # Convert byte to integer
            return data
        else:
            return None
            
    def set_mz_state(self) -> None:
        """Tell the Arduino to use the Mz distance sensor
        """
        self.ser.write("1\n".encode())
        self.logger.info(self.ser.readline().decode())
        # Alternative option is ser.write(byte_value.to_bytes(1, byteorder='big'))
        # w/ this on the recieve end uint8_t receivedByte = Serial.read(); // Read the incoming byte
        return None
        
    def set_my_state(self) -> None:
        """Set the Arduino to use the My distance sensor
        """
        self.ser.write("2\n".encode())
        self.logger.info(self.ser.readline().decode())
        return None
        




if __name__ == '__main__':

    ser = SerialHandler('COM4', 115200) # COM port, Baudrate
    count = 0
    while True:
        data = ser.get_arduino_data()
        print(data)
        
        # count += 1
        # if count == 10:
        #     ser.set_mz_state()
        
        # if count == 20:
        #     ser.set_my_state()
        #     count = 0
        

