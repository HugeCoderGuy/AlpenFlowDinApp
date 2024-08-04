from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import pyqtgraph as pg
import sys
from PhidgetHandler import PhidgetHandler
from SerialHandler import SerialHandler
import numpy as np
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os
import logging
import time


class AlpenFlowApp(QMainWindow):
    def __init__(self, com_port: str='COM4'):
        
        # Setup the internal logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        console_handler  = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        
        super().__init__()
        
        self.setWindowTitle("AlpenFlow Din Measurement App")
        self.setGeometry(100, 100, 1000, 600)
        
        self.log_dir = os.path.join(os.path.normpath(os.getcwd() + os.sep), "Data")
            
        # setup log file paths
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # self.phidget = PhidgetHandler()
        self.phidget = None
        self.serial = SerialHandler(com_port, 115200) # 1/timeout is the frequency at which the port is read

        self.max_index = 12000  # max data collection of 2 mins
        self.curr_data_i = 0
        self.max_data_count = 0
        # use preinitalized arrays for increased speed
        self.forces = np.zeros(self.max_index)
        self.distances = np.zeros(self.max_index)  # maybe specify data type
        self.max_strain_dist = 0
        self.max_strain = 0
        self.estimated_speed = 0
        
        # this text is used for the results output
        self.peak_my_str = "Peak My/BSL [N]: "
        self.din_13_str = "Z value (ISO 13992): "
        self.din_11_str = "Z value (ISO 11088): "
        self.estimated_speed_str = "Estimated Speed [m/s]: "
        self.max_force_at_str = "Max Force at [mm]: "
        
        self.initUI()
        
    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)

        top_buttons = QHBoxLayout(main_widget)
        top_buttons.setSpacing(5)
        main_layout.addLayout(top_buttons)
        
        # Add the combo box to select din test
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Testing Mz", "Testing My"])
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
        
        # Add the file name for saving data to csv
        file_name_label = QLabel("\t\t\tFile Name:")
        top_buttons.addWidget(file_name_label)
        self.csv_name_input = QLineEdit("Din_data_" + datetime.now().strftime("%Y%m%d_%H%M"))
        top_buttons.addWidget(self.csv_name_input)
        self.csv_name_input.setFixedWidth(250)
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
        # self.plot_widget = pg.PlotWidget()
        # plot_layout.addWidget(self.plot_widget)
        self.plot_widget = FigureCanvas(plt.Figure())  # matplot lib graph
        plot_layout.addWidget(self.plot_widget)
        plot_and_buttons.addLayout(plot_layout)
        
        self.ax = self.plot_widget.figure.subplots()  # global ax variable

        # Add the buttons and value displays
        button_layout = QVBoxLayout()  # buttons are vertical
        button_layout.setSpacing(50)  # Set spacing between the widgets

        self.begin_data_button = QPushButton("Collect Data")
        self.begin_data_button.clicked.connect(self.initalize_data_collection)
        button_layout.addWidget(self.begin_data_button)
        self.original_begin_data_style = self.begin_data_button.styleSheet()

        self.peak_my_label = QLabel(self.peak_my_str + "0")
        button_layout.addWidget(self.peak_my_label)
        
        self.max_force_at = QLabel(self.max_force_at_str + "0")
        button_layout.addWidget(self.max_force_at)
        
        self.din_value_13 = QLabel(self.din_13_str + "0")
        button_layout.addWidget(self.din_value_13)
        
        self.din_value_11 = QLabel(self.din_11_str + "0")
        button_layout.addWidget(self.din_value_11)
        
        self.estimated_speed_lbl = QLabel(self.estimated_speed_str + "0")
        button_layout.addWidget(self.estimated_speed_lbl)

        # Create a button to plot data
        self.button = QPushButton("Clear Graph", self)
        self.button.clicked.connect(self.plot_graph)
        button_layout.addWidget(self.button)
        
        plot_and_buttons.addLayout(button_layout)
        self.multiplier = 1
        
        self.original_style = self.din_value_13.styleSheet()

    def reset_data(self):
        self.curr_data_i = 0
        self.max_strain_dist = 0
        self.max_strain = 0
        self.estimated_speed = 0
        self.strains = np.zeros(self.max_index)
        self.distances = np.zeros(self.max_index)  # maybe specify data type
        self.logger.info("Any previous data values have been cleared.")
        
    # def sample_sensors(self):
    #     distance_measurement = self.serial.get_arduino_data()
    #     if distance_measurement != None:
    #         self.strains[self.curr_data_i] = self.phidget.recent_measurement
    #         self.distances[self.curr_data_i] = distance_measurement
    #         if len(np.where(self.distances > 10, self.distances)) > 10:
    #             # Stop data collection after 10 data samples greater than 10
    #             pass
    
    def initalize_data_collection(self):
        self.combo_box.setEnabled(False)
        self.save_data_button.setEnabled(False)
        self.begin_data_button.setText("Collecting Data...")
        self.begin_data_button.setEnabled(False)
        self.begin_data_button.setStyleSheet("background-color: yellow")
        self.reset_data()
        self.safe_for_processing = False
        self.worker = self.Worker(self)
        self.worker.result.connect(self.handle_result)
        self.worker.finished.connect(self.task_finished)
        self.worker.start()
        
    def handle_result(self, result):
        self.distances, self.forces, self.estimated_speed = result
        # self.forces = self.phidget.interpret_voltage_data(self.forces)
        self.max_force = self.forces.max()
        self.max_strain_dist = self.distances[self.strains.argmax()]
        
        my_per_bsl = str(round(self.max_force / int(self.bsl_input_box.text()), 2))
        self.peak_my_label.setText(self.peak_my_str + my_per_bsl)
        self.max_force_at.setText(self.max_force_at_str + str(self.max_strain_dist))
        self.din_value_13.setText(self.din_13_str + str(100))  # todo calc din
        self.din_value_11.setText(self.din_11_str + str(100))  # todo calc din
        self.estimated_speed_lbl.setText(self.estimated_speed_str + str(self.estimated_speed))
        
        self.ax.plot(self.distances, self.forces)
        self.ax.set_title("Force vs. Distance Curve")
        self.ax.set_xlabel("Distance (mm)")
        self.ax.set_ylabel("Force (N)")
        self.multiplier += 1
        print(self.multiplier)

        self.plot_widget.draw()
        
    def task_finished(self):
        self.safe_for_processing = True
        self.begin_data_button.setText("Collect Data")
        self.begin_data_button.setEnabled(True)
        self.begin_data_button.setStyleSheet(self.original_style)
        self.combo_box.setEnabled(True)
        self.save_data_button.setEnabled(True)
        
    class Worker(QThread):
        finished = pyqtSignal()
        result = pyqtSignal(tuple)

        def __init__(self, parent):
            super().__init__(parent)
            self.self = parent
            self.distances = np.zeros(parent.max_index)
            self.forces = np.zeros(parent.max_index)
            
        def run(self):
            time.sleep(2)
            index = 10
            multiplier = np.random.random()
            self.distances = np.linspace(0, self.self.max_index)
            self.forces = np.linspace(0, self.self.max_index) * multiplier
            estimated_speed = 1
            self.result.emit((self.distances[:index], self.forces[:index], estimated_speed))
            self.finished.emit()

        def actual_run(self):
            index = 0
            dist_counter = 0
            first_dist = False
            start_time = False
            while (index < self.self.max_index) and dist_counter < 10:
                distance_measurement = self.self.serial.get_arduino_data()
                if distance_measurement != None:
                    if not first_dist:
                        first_dist = distance_measurement
                    self.forces[index] = self.phidget.recent_measurement
                    self.distances[index] = distance_measurement - first_dist
                    index += 1
                    if not start_time and (distance_measurement - first_dist) > 1:
                        first_time = time.time()
                    if (distance_measurement - first_dist) > 10:
                        dist_counter += 1
            
            # .009m over n seconds minus 1/100 seconds per sample * 10 -> (.1)
            estimated_speed = .009 / (time.time() - first_time - .1)  
            self.result.emit((self.distances[:index], self.forces[:index], estimated_speed))
            self.finished.emit()
        
        # mz_arm_layout = QHBoxLayout()
        # mz_arm_layout.setSpacing(2)  # Set spacing between the widgets
        # lever_arm = QLabel("Mz Arm:")
        # mz_arm_layout.addWidget(lever_arm)
        # self.mz_arm_layout = QLineEdit("430")
        # self.mz_arm_layout.setFixedWidth(50)
        # mz_arm_layout.addWidget(self.mz_arm_layout)
        # mm_label = QLabel("mm")
        # mz_arm_layout.addWidget(mm_label)
        
        # button_layout.addLayout(mz_arm_layout)
        



    def on_button1_click(self):
        # Handle button 1 click
        print("Button 1 clicked")

    def on_button2_click(self):
        # Handle button 2 click
        print("Button 2 clicked")

    def on_option_change(self, index):
        # Handle combo box option change
        print(f"Option changed to {self.combo_box.currentText()}")
        
    def save_data(self):
        f_name = self.csv_name_input.text() + ".csv"
        csv_fname = os.path.join(self.log_dir, f_name)

        # Check if log exists and should therefore be rolled
        file_exits = os.path.isfile(csv_fname)
        if file_exits:
            self.logger.error("Filename already exits: " + str(file_exits))
            self.save_data_button.setStyleSheet("background-color: red")
            self.save_data_button.setText("Error!")

            # Set a timer to revert the color after 2 seconds (2000 milliseconds)
            QTimer.singleShot(1500, self.revert_color)
            return
        else:
            # Stack the arrays column-wise
            print(self.distances, "\n", self.forces)
            data = np.column_stack((self.distances, self.forces))

            # Save to CSV
            np.savetxt(csv_fname, data, delimiter=',', header='Distance[mm],Force[N]')
            
            self.logger.info("Saved data to: " + csv_fname)
            
            # Change the button color
            self.save_data_button.setStyleSheet("background-color: green")
            self.save_data_button.setText("Saved!")

            # Set a timer to revert the color after 2 seconds (2000 milliseconds)
            QTimer.singleShot(1500, self.revert_color)

    def revert_color(self):
        # Revert the button color to the original style
        self.save_data_button.setStyleSheet(self.original_style)
        self.save_data_button.setText("Save Data")
        self.csv_name_input.setText("Din_data_" + datetime.now().strftime("%Y%m%d_%H%M"))

        
    def plot_graph(self):
        # # Example data
        # x = np.linspace(0, 10, 100)
        # y = np.sin(x)

        # # Clear any existing plots
        # self.plot_widget.clear()

        # # Plot the data
        # self.plot_widget.plot(x, y, pen='b')  # 'b' stands for blue color
        
        self.ax.clear()

        # Example data
        x = np.linspace(0, 10, 100)
        y = np.sin(x) * self.multiplier

        self.ax.plot(x, y)
        self.ax.set_title("Sine Wave")
        self.ax.set_xlabel("X-axis")
        self.ax.set_ylabel("Y-axis")
        self.multiplier += 1
        print(self.multiplier)

        self.plot_widget.draw()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = AlpenFlowApp()
    mainWin.show()
    sys.exit(app.exec_())