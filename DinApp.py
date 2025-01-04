from typing import Tuple
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit, QCheckBox, QTableWidget, QTableWidgetItem, QAbstractScrollArea 
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QFile, QTextStream
import sys
from src.PhidgetHandler import PhidgetHandler
import numpy as np
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os
import logging
import time
from src.ISO_11088 import ISO11088
from src.ISO_13992 import ISO13992
try:
    import breeze_resources
    darkmode = True
except:
    print("Will not be using the darkmode rendering")
    darkmode = False


class AlpenFlowApp(QMainWindow):
    def __init__(self):
        
        # Setup the internal logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        console_handler  = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # kick off the UI
        super().__init__()
        self.setWindowTitle("DinApp")
        self.setGeometry(100, 100, 1500, 650)
        
        self.log_dir = os.path.join(os.path.normpath(os.getcwd() + os.sep), "Data")
            
        # setup log file paths
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # import Steven's ISO DIN standard converters
        self.iso13 = ISO13992()
        self.iso11 = ISO11088()
        self.timeout = 5  # time in seconds for the tof sensor to timeout

        self.phidget = PhidgetHandler()  # TODO UNCOMMNET THIS

        # Various shared variables
        self.max_raw_torques_index = 6000
        # use preinitalized arrays for increased speed
        self.raw_torques = np.zeros(self.max_raw_torques_index)
        self.raw_torque_times = np.zeros(self.max_raw_torques_index)
        self.sample_rate = .01
        
        # this text is used for the results output
        self.peak_torque_div_BSL_str = "Torque/BSL: \t\t"
        self.din_13_str = "Z value (ISO 13992): \t\t"
        self.din_11_str = "Z value (ISO 11088): \t\t"
        self.torque_wrench_reading_str = "Expected Wrench Val (N/m) \t"
        self.max_force_str = "Max Torque: \t\t"
        
        # logic flags to determine branches
        self.graph_numb = 0
        self.saved_the_data = False
        self.testing_My = True # Starts out as testing My
        
        self.initUI()
        
    def initUI(self) -> None:
        """Creates UI of the AlpenFlow din test application
        
        Parent layout (main_layout) is vertical
            * Top bar layout is horizontal (top_buttons)
            * Plot and controls are horizontal (plot_and_buttons)
            * buttons to right of plot are vertical sub layout (button_layout)
            * Table displaying times at each displacement is last item (main_layout)
        """
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)

        top_buttons = QHBoxLayout(main_widget)
        top_buttons.setSpacing(5)
        main_layout.addLayout(top_buttons)
        
        # Add the combo box to select din test
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Testing My \u2191  ", "Testing Mz \u2192  "])  # TODO add color to text
        self.combo_box.currentIndexChanged.connect(self.on_option_change)
        top_buttons.addWidget(self.combo_box)
        
        # allow for bsl input
        self.bsl_label = QLabel("BSL:")
        top_buttons.addWidget(self.bsl_label)
        # allow only integers for bsl input
        only_int_validator = QIntValidator()
        only_int_validator.setRange(200, 400)
        self.bsl_input_box = QLineEdit("300")
        self.bsl_input_box.setMaximumWidth(100)
        self.bsl_input_box.setValidator(only_int_validator)
        top_buttons.addWidget(self.bsl_input_box)
        
        self.torque_arm_lbl = QLabel("Torque Wrench Length (mm)")
        self.torque_arm_length_input = QLineEdit("535")
        top_buttons.addWidget(self.torque_arm_lbl)
        top_buttons.addWidget(self.torque_arm_length_input)
        
        # Add the input box and ability to save current data to a file
        file_name_label = QLabel("\t\t\tFile Name:")
        top_buttons.addWidget(file_name_label)
        self.csv_name_input = QLineEdit(f"Din_data_{self.bsl_input_box.text()}_My_{self.testing_My}" + datetime.now().strftime("%Y%m%d_%H%M"))
        top_buttons.addWidget(self.csv_name_input)
        self.csv_name_input.setFixedWidth(350)
        csv_label = QLabel(".csv")
        top_buttons.addWidget(csv_label)
        self.save_data_button = QPushButton("Save Data")
        self.save_data_button.clicked.connect(self.save_data)  # save function for button
        top_buttons.addWidget(self.save_data_button)
        
        # Next layout is horizontal for the plot and labels/buttons
        plot_and_buttons = QHBoxLayout()
        main_layout.addLayout(plot_and_buttons)
        
        # Vertical layout for the plot on the left side
        plot_layout = QVBoxLayout()
        self.plot_widget = FigureCanvas(plt.Figure())  # matplot lib graph
        plot_layout.addWidget(self.plot_widget)
        plot_and_buttons.addLayout(plot_layout)
        
        self.ax = self.plot_widget.figure.subplots()  # global ax variable
        self.plot_widget.setFixedSize(1300, 600) 
                
        # Add the buttons and value displays
        button_layout = QVBoxLayout()  # buttons are vertical
        button_layout.setSpacing(50)  # Set spacing between the widgets

        # button to kick off data collection and processing
        self.begin_data_button = QPushButton("Collect Data")
        self.begin_data_button.clicked.connect(self.initalize_data_collection)
        button_layout.addWidget(self.begin_data_button)
        self.original_begin_data_style = self.begin_data_button.styleSheet()

        # A series of labels to display relavent measurements
        self.peak_my_label = QLabel(self.peak_torque_div_BSL_str + "0N")
        button_layout.addWidget(self.peak_my_label)
        
        self.max_force_lbl = QLabel(self.max_force_str + "0 N/m")
        button_layout.addWidget(self.max_force_lbl)
        
        self.torque_wrench_output = QLabel(self.torque_wrench_reading_str + "0 N/m")
        button_layout.addWidget(self.torque_wrench_output)
        
        self.din_value_13 = QLabel(self.din_13_str + "<b>0</b>")
        button_layout.addWidget(self.din_value_13)
        
        self.din_value_11 = QLabel(self.din_11_str + "<b>0</b>")
        button_layout.addWidget(self.din_value_11)
        
        plot_and_buttons.addLayout(button_layout)
        
        # Add ability to keep graphs visible or to ignore them
        self.save_graph_checkbox = QCheckBox()
        self.save_graph_checkbox.setText(" Keep Graphs Visible")
        button_layout.addWidget(self.save_graph_checkbox)
        
        self.original_style = self.din_value_13.styleSheet()

    def reset_data(self) -> None: 
        """Function to clear collected data in memory and reset to initial vals
        """
        if not self.saved_the_data:
            self.logger.info("Data that was previously collected is no longer in memory")
            self.saved_the_data = False
    
    def initalize_data_collection(self):
        """Disables buttons durring data collection and begins Worker
        
        Worker is a thread that collects the data. Defined as a Qthread class
        """
        # Disable data and output message
        self.combo_box.setEnabled(False)
        self.save_data_button.setEnabled(False)
        self.begin_data_button.setText(f"Collecting Data for {self.timeout}s...")
        self.begin_data_button.setEnabled(False)
        self.begin_data_button.setStyleSheet("background-color: yellow")
        self.reset_data()
        self.safe_for_processing = False
        self.worker = self.Worker(self)
        self.worker.result.connect(self.handle_result)
        self.worker.finished.connect(self.task_finished)
        self.worker.start()
        
    def handle_result(self, result: tuple) -> None:
        """Takes result from data collection, processes it, and displays it
        
        This is the callback function for when the QThread worker function 
        completes. Output of function
        is visual feedback to the user and data that can be saved to csvs

        Args:
            result (tuple): tuple of three consisting of dist, force, and speed
        """
        # clear the scatter plot data and plot old processed data before new graphs
        if self.save_graph_checkbox.isChecked() and self.graph_numb == 1:
            self.ax.clear()
            self.ax.plot(self.raw_torque_times, self.raw_torques, label="Run 0")

        # unpack the worker results and analyze them
        self.raw_torques, self.raw_torque_times = result
        wrench_measured_torque = self.phidget.interpret_voltage_data(self.raw_torques, self.testing_My, return_val_in_newtons=True)
        wrench_measured_torque = wrench_measured_torque.max() * int(self.torque_arm_length_input.text()) / 1000

        # pick out key metrics here
        self.raw_torques = self.phidget.interpret_voltage_data(self.raw_torques, self.testing_My)
        BSL = int(self.bsl_input_box.text()) # [mm] Get BSL that the user inputted into the input box. 
        self.raw_torques_div_BSL = self.raw_torques / (BSL/1000)
        
        max_boot_torque_div_BSL =  self.raw_torques_div_BSL.max()

        
        # calculate the din values depending on test state
        if self.testing_My:
            iso13_din = self.iso13.calc_z_of_My_div_BSL(max_boot_torque_div_BSL, round_bool=False)
            iso11_din = self.iso11.calc_z_of_My_div_BSL(max_boot_torque_div_BSL, round_bool=False)
        else:
            iso13_din = self.iso13.calc_z_of_Mz_div_BSL(max_boot_torque_div_BSL, round_bool=False)
            iso11_din = self.iso11.calc_z_of_Mz_div_BSL(max_boot_torque_div_BSL, round_bool=False)
        self.logger.info(f"ISO13 {iso13_din}, ISO11: {iso11_din}")
        
        # add data to GUI labels for user to read
        self.peak_my_label.setText(self.peak_torque_div_BSL_str + str(round(max_boot_torque_div_BSL, 2)) + " N")
        self.max_force_lbl.setText(self.max_force_str + str(round(self.raw_torques.max(), 2)) + " N/m")
        self.torque_wrench_output.setText(self.torque_wrench_reading_str + str(round(wrench_measured_torque, 2)) +" N/m")
        self.din_value_13.setText(self.din_13_str + "<b>" + str(round(iso13_din, 2)) + "</b>") 
        self.din_value_11.setText(self.din_11_str + "<b>" + str(round(iso11_din, 2)) + "</b>")  
        
        # create the release curve plot for viewing
        if not self.save_graph_checkbox.isChecked():
            self.ax.clear()
            self.graph_numb = 0
            self.ax.scatter(self.raw_torque_times, self.raw_torques, alpha=.3, linewidths=.3)
        self.ax.plot(self.raw_torque_times, self.raw_torques, label="Run " + str(self.graph_numb))
        self.ax.set_title("Raw Torques Measured Durring Release")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Torque (N/m)")
        self.graph_numb += 1
        if self.save_graph_checkbox.isChecked():
            self.ax.legend()

        self.plot_widget.draw()
            
        
    def task_finished(self):
        """Renables all of the other functions of the GUI after data collection"""
        self.safe_for_processing = True
        self.begin_data_button.setText("Collect Data")  # replace label with original
        self.begin_data_button.setEnabled(True)
        self.begin_data_button.setStyleSheet(self.original_style)
        self.combo_box.setEnabled(True)
        self.save_data_button.setEnabled(True)
    
        
    class Worker(QThread):
        finished = pyqtSignal()
        result = pyqtSignal(tuple)

        def __init__(self, parent):
            """QThread that manages data collection from the phidget and arduino

            Args:
                QThread (class): parent class that helps manage the thread with pyQT
            """
            super().__init__(parent)
            self.self = parent
            self.raw_torques = np.zeros(parent.max_raw_torques_index)
            self.raw_torque_times = np.zeros(parent.max_raw_torques_index)
            
            # Setup the internal logger
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
            console_handler  = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            
            # self.logger.addHandler(console_handler)

        def run(self) -> tuple:
            """Continiously collects data from sensors until boot moves too far away
            
            Function runs as a thread. It samples at the same frequency as the 
            arduino. This is done by quering the arduino faster than the arduino
            reports data. Then python app only logs data when arduino reports 
            data. Thus, we rely on the arduino for deterministic timing and then
            log distance/force measurement based on that timing.

            Returns:
                tuple: distances, forces
            """
            raw_torque_index = 0
            start_time = time.time()
            
            # Collect data for 30s or until we have 200ms of too far of dists 
            while (time.time() - start_time) < self.self.timeout:
                current_torque = self.self.phidget.recent_measurement
                    
                # log the torques constantly. Don't correlate them with phidget measurement
                self.raw_torques[raw_torque_index] = current_torque
                self.raw_torque_times[raw_torque_index] = time.time() - start_time
                raw_torque_index += 1
                time.sleep(.001)
            
            self.result.emit((self.raw_torques[:raw_torque_index], self.raw_torque_times[:raw_torque_index]))
            self.finished.emit()

    def on_option_change(self):
        """Changes the state of the Arduino based on the selected option
        
        LED L is turned on when in state My. Upon state change, the Ard is queried
        until a confirmation response is found
        """
        if "Mz" in self.combo_box.currentText():
            self.testing_My = False
            self.combo_box.setStyleSheet(self.original_style)
            self.logger.info(f"Option changed to {self.combo_box.currentText()}")

        if "My" in self.combo_box.currentText():
            self.testing_My = True
            self.combo_box.setStyleSheet(self.original_style)
            self.logger.info(f"Option changed to {self.combo_box.currentText()}")
            
        
    def save_data(self):
        """Saves the dist/force data in memory to two csvs. Processed and raw"""
        f_name_raw_torque_div_BSL = self.csv_name_input.text() + "_raw_torque_div_bsl.csv"
        csv_fname_raw = os.path.join(self.log_dir, f_name_raw_torque_div_BSL)

        # Check if log exists and should therefore be rolled
        file_exits = os.path.isfile(csv_fname_raw)
        if file_exits:
            self.logger.error("Filename already exits: " + str(file_exits))
            self.save_data_button.setStyleSheet("background-color: red")
            self.save_data_button.setText("Error!")

            # Set a timer to revert the color after 2 seconds (2000 milliseconds)
            QTimer.singleShot(1500, self.revert_color)
            return
        else:
            # Stack the arrays column-wise
            raw_bsl_data = np.column_stack((self.raw_torque_times, self.raw_torques_div_BSL))

            # Save to CSV
            np.savetxt(csv_fname_raw, raw_bsl_data, delimiter=',', header='Time[s],Torque_div_BSL[N]', fmt='%.4f')
            
            self.logger.info(f"Saved data to: {csv_fname_raw}")
            
            # Change the button color
            self.save_data_button.setStyleSheet("background-color: green")
            self.save_data_button.setText("Saved!")

            # Set a timer to revert the color after 2 seconds (2000 milliseconds)
            QTimer.singleShot(1500, self.revert_color)
            
        self.saved_the_data = True

    def revert_color(self):
        """Revert the button color to the original style"""
        self.save_data_button.setStyleSheet(self.original_style)
        self.save_data_button.setText("Save Data")
        self.csv_name_input.setText(f"Din_data_{self.bsl_input_box.text()}_My_{self.testing_My}" + datetime.now().strftime("%Y%m%d_%H%M"))
        
# entry point of application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    if darkmode:
        file = QFile(":/dark/stylesheet.qss")
        file.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())
        
    mainWin = AlpenFlowApp()
    mainWin.show()
    sys.exit(app.exec_())