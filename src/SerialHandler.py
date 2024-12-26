import serial
import serial.tools.list_ports
import logging
import time


class SerialHandler():
    def __init__(self):
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
        
        # self.logger.addHandler(console_handler)
        
        # Setup the serial port
        self.timeout_duration = 2  # seconds
        baudrate = 115200
        comport = self.find_arduino_com_port()
        self.ser = serial.Serial(comport, baudrate, timeout=0.1)         # 1/timeout is the frequency at which the port is read
        self.reset_buffer() # Clear the input buffer
        
    def reset_buffer(self) -> None:
        self.ser.reset_input_buffer()
        
    def find_arduino_com_port(self) -> str:
        """Searches all com ports to find arduino and returns name of port
        
        The arduino responds to the command "3\n" with "AlpenFlow" confirming
        that it is the arduino running the correct firmware.

        Returns:
            str: ex. "COM4"
        """
        possible_ports = []
        # Initial pass through of potential ports
        for port in serial.tools.list_ports.comports():
            if "Arduino" in port.description:
                possible_ports.append(port.device)

        if len(possible_ports) == 0:
            self.logger.error("No Arduino found")
            raise LookupError("No Arduino found")
        
        else:
            # iterate through each port looking for confirmation from arduino
            for port in possible_ports:
                buffer = bytearray()  # Buffer to store incoming bytes
                start_time = time.time()
                self.logger.info("Arduino found at: " + port)
                test_ser = serial.Serial(port, 115200, timeout=0.5)
                test_ser.reset_input_buffer()  # Clear the input buffer
                test_ser.write("3\n".encode())
            
                while True:
                    if time.time() - start_time > self.timeout_duration:
                        print("Did not get confirmation from port: " + port)
                        break
                    
                    # Read bytes from the serial port
                    if test_ser.in_waiting > 0:
                        test_ser.write("3\n".encode())  # spam identification command
                        data = test_ser.read(test_ser.in_waiting)
                        buffer.extend(data)
                        
                        if b"AlpenFlow" in buffer:
                            self.logger.info("Got Confirmation from port: " + port)
                            return port
                
            self.logger.warning("Didn't explicitly find Arduino. Attempting port " + possible_ports[0])
            test_ser.close()
            return possible_ports[0]

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
            
    def set_my_state(self) -> None:
        """Tell the Arduino to use the Mz distance sensor
        """
        start_time = time.time()
        buffer = bytearray()  # Buffer to store incoming bytes

        # self.ser.reset_input_buffer()
        while True:
            if time.time() - start_time > self.timeout_duration:
                print("Did not get confirmation for switch to My testing")
                break
            
            # Read bytes from the serial port
            if self.ser.in_waiting > 0:
                self.ser.write("1\n".encode())  # spam identification command
                data = self.ser.read(self.ser.in_waiting)
                buffer.extend(data)
                
                if b"my" in buffer:
                    self.logger.info("Arduino confirmed switch to My")
                    break
                if b"ym" in buffer:
                    self.logger.info("Arduino is already in state my")
                    break
        # try:
        #     self.logger.info(f"msg from arduino: {self.ser.readline().decode()}")
        # except:
        #     self.logger.info(f"msg from arduino: {self.ser.readline().decode()}")
        # Alternative option is ser.write(byte_value.to_bytes(1, byteorder='big'))
        # w/ this on the recieve end uint8_t receivedByte = Serial.read(); // Read the incoming byte
        return None
        
    def set_mz_state(self) -> None:
        """Set the Arduino to use the My distance sensor
        """
        start_time = time.time()
        buffer = bytearray()  # Buffer to store incoming bytes
        self.ser.write("2\n".encode())
        
        while True:
            if time.time() - start_time > self.timeout_duration:
                print("Did not get confirmation for switch to Mz testing")
                break
            
            # Read bytes from the serial port
            if self.ser.in_waiting > 0:
                self.ser.write("2\n".encode())  # spam identification command
                data = self.ser.read(self.ser.in_waiting)
                buffer.extend(data)
                
                if b"mz" in buffer:
                    self.logger.info("Arduino confirmed switch to Mz")
                    break
                if b"zm" in buffer:
                    self.logger.info("Arduino is already in state mz")
                    break
        # self.ser.reset_input_buffer()
        # try:
        #     self.logger.info(f"msg from arduino: {self.ser.readline().decode()}")
        # except:
        #     self.logger.info(f"msg from arduino: {self.ser.readline().decode()}")
        return None
        




if __name__ == '__main__':

    ser = SerialHandler() # COM port, Baudrate
    count = 0
    time.sleep(1)
    ser.set_my_state()
    while True:
        data = ser.get_arduino_data()
        if data != None:
            print(data, time.time())
        
        count += 1
        if count == 1000000:
            print(count)
            print("switching state to mz")
            ser.set_mz_state()
        
        if count == 2000000:
            print("switching state to my")

            ser.set_my_state()
            count = 0
        

