from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit, QCheckBox, QTableWidget, QTableWidgetItem, QAbstractScrollArea 
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QFile, QTextStream
import sys
from src.PhidgetHandler import PhidgetHandler
from src.SerialHandler import SerialHandler
import numpy as np
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os
import logging
import time
from src.AggregateRawData import descrete_dist_to_corresponding_force
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
        self.setWindowTitle("AlpenFlow Din Measurement App")
        self.setGeometry(100, 100, 1000, 635)
        
        self.log_dir = os.path.join(os.path.normpath(os.getcwd() + os.sep), "Data")
            
        # setup log file paths
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # import Steven's ISO DIN standard converters
        self.iso13 = ISO13992()
        self.iso11 = ISO11088()
        
        # self.phidget = PhidgetHandler()  # TODO UNCOMMNET THIS
        self.phidget = None
        try:
            self.serial = SerialHandler() # 1/timeout is the frequency at which the port is read
        except:
            self.logger.error("Did not find Arduino on a USB port")
            self.serial = None

        # Various shared variables
        self.max_index = 3000  # max data collection of 2 mins
        self.curr_data_i = 0
        self.max_data_count = 0
        # use preinitalized arrays for increased speed
        self.forces = np.zeros(self.max_index)
        self.distances = np.zeros(self.max_index, dtype=np.uint8)  # maybe specify data type
        self.aggregate_dist = np.zeros(10)
        self.aggregate_force = np.zeros(10)
        self.max_strain_dist = 0
        self.max_strain = 0
        self.sample_rate = .01
        
        # this text is used for the results output
        self.peak_torque_str = "Torque/BSL: \t\t"
        self.din_13_str = "Z value (ISO 13992): \t\t"
        self.din_11_str = "Z value (ISO 11088): \t\t"
        self.estimated_speed_str = "Estimated Speed: \t"
        self.max_force_at_str = "Max Force at: \t\t"
        
        # logic flags to determine branches
        self.graph_numb = 0
        self.saved_the_data = False
        self.testing_My = False
        
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
        
        # Add the input box and ability to save current data to a file
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
        self.plot_widget = FigureCanvas(plt.Figure())  # matplot lib graph
        plot_layout.addWidget(self.plot_widget)
        plot_and_buttons.addLayout(plot_layout)
        
        self.ax = self.plot_widget.figure.subplots()  # global ax variable

        # Add the buttons and value displays
        button_layout = QVBoxLayout()  # buttons are vertical
        button_layout.setSpacing(50)  # Set spacing between the widgets

        # button to kick off data collection and processing
        self.begin_data_button = QPushButton("Collect Data")
        self.begin_data_button.clicked.connect(self.initalize_data_collection)
        button_layout.addWidget(self.begin_data_button)
        self.original_begin_data_style = self.begin_data_button.styleSheet()

        # A series of labels to display relavent measurements
        self.peak_my_label = QLabel(self.peak_torque_str + "0N")
        button_layout.addWidget(self.peak_my_label)
        
        self.max_force_at = QLabel(self.max_force_at_str + "0mm")
        button_layout.addWidget(self.max_force_at)
        
        self.din_value_13 = QLabel(self.din_13_str + "<b>0</b>")
        button_layout.addWidget(self.din_value_13)
        
        self.din_value_11 = QLabel(self.din_11_str + "<b>0</b>")
        button_layout.addWidget(self.din_value_11)
        
        self.estimated_speed_lbl = QLabel(self.estimated_speed_str + "0m/s")
        button_layout.addWidget(self.estimated_speed_lbl)
        
        plot_and_buttons.addLayout(button_layout)
        
        # Add ability to keep graphs visible or to ignore them
        self.save_graph_checkbox = QCheckBox()
        self.save_graph_checkbox.setText(" Keep Graphs Visible")
        button_layout.addWidget(self.save_graph_checkbox)
                        
        self.table_of_counts = QTableWidget()
        self.table_of_counts.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.table_of_counts.resizeColumnsToContents()
        self.table_of_counts.setRowCount(1)
        self.table_of_counts.setColumnCount(10)
        self.table_of_counts.setHorizontalHeaderLabels(["1mm", "2mm", "3mm", "4mm", "5mm", "6mm", "7mm", "8mm", "9mm", "10mm"])
        for i in range(10):
            self.table_of_counts.setColumnWidth(i, 90)
        self.populate_distance_times_table(self.distances)
        main_layout.addWidget(self.table_of_counts)
        
        self.original_style = self.din_value_13.styleSheet()

    def reset_data(self) -> None: 
        """Function to clear collected data in memory and reset to initial vals
        """
        self.curr_data_i = 0
        self.max_strain_dist = 0
        self.max_strain = 0
        self.forces = np.zeros(self.max_index)
        self.distances = np.zeros(self.max_index, dtype='uint8')  # maybe specify data type
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
        self.begin_data_button.setText("Collecting Data for 30s...")
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
            self.ax.plot(self.aggregate_dist, self.aggregate_force, label="Run 0")

        # unpack the worker results and analyze them
        self.distances, self.forces = result
        
        if np.any(self.distances) and np.any(self.forces):
            # only process data if there is data. No data is all 0s
            mask = (self.distances < 11) & (self.distances >= 0)
            self.distances = self.distances[mask]
            self.forces = self.forces[mask]
            estimated_speed = self.derive_speed_from_distances(self.distances)

            # pick out key metrics here
            # self.forces = self.phidget.interpret_voltage_data(self.forces)
            max_force = self.forces.max()
            self.max_strain_dist = self.distances[self.forces.argmax()]
            self.aggregate_dist, self.aggregate_force = descrete_dist_to_corresponding_force(self.distances, self.forces)
            dist_print_msg = [int(i) for i in self.aggregate_dist]
            force_print_msg = [float(i) for i in self.aggregate_force]
            self.logger.info(f"aggregate_dist:\t{dist_print_msg}")
            self.logger.info(f"aggregate_force:\t{force_print_msg}")
            
            # calculate the din values depending on test state
            force_per_bsl = round(max_force / int(self.bsl_input_box.text()), 2)
            if self.testing_My:
                iso13_din = self.iso13.calc_z_of_My_div_BSL(force_per_bsl)
                iso11_din = self.iso11.calc_z_of_My_div_BSL(force_per_bsl)
            else:
                iso13_din = self.iso13.calc_z_of_Mz_div_BSL(force_per_bsl)
                iso11_din = self.iso11.calc_z_of_Mz_div_BSL(force_per_bsl)
            
            # add data to GUI labels for user to read
            self.peak_my_label.setText(self.peak_torque_str + str(force_per_bsl) + "N")
            self.max_force_at.setText(self.max_force_at_str + str(self.max_strain_dist) + "mm")
            self.din_value_13.setText(self.din_13_str + "<b>" + str(iso13_din) + "</b>") 
            self.din_value_11.setText(self.din_11_str + "<b>" + str(iso11_din) + "</b>")  
            self.estimated_speed_lbl.setText(self.estimated_speed_str + str(estimated_speed) + "m/s")
            
            self.populate_distance_times_table(self.distances)  # update speeds table
            
            # create the release curve plot for viewing
            if not self.save_graph_checkbox.isChecked():
                self.ax.clear()
                self.graph_numb = 0
                self.ax.scatter(self.distances, self.forces, alpha=.3, linewidths=.3)
            self.ax.plot(self.aggregate_dist, self.aggregate_force, label="Run " + str(self.graph_numb))
            self.ax.set_title("Force vs. Distance Curve")
            self.ax.set_xlabel("Distance (mm)")
            self.ax.set_ylabel("Force (N)")
            self.graph_numb += 1
            if self.save_graph_checkbox.isChecked():
                self.ax.legend()

            self.plot_widget.draw()
            
        else:
            self.logger.error("Data collection failed")
        
    def task_finished(self):
        """Renables all of the other functions of the GUI after data collection"""
        self.safe_for_processing = True
        self.begin_data_button.setText("Collect Data")  # replace label with original
        self.begin_data_button.setEnabled(True)
        self.begin_data_button.setStyleSheet(self.original_style)
        self.combo_box.setEnabled(True)
        self.save_data_button.setEnabled(True)
        
    def populate_distance_times_table(self, distances: np.array) -> None:
        """Takes the counts of nonzero distance values and determines durration
        
        Helps the user know if they had a fairly consistent velocity on the
        din release by identifying how long they spent in each distance. Could
        be considered equivalent to speed per mm of release

        Args:
            distances (np.array): distances collected durring the sampling
        """
        unique_dist = np.unique(distances)
        unique_dist = np.sort(unique_dist)

        for i in range(1, 11):
            number_samples = np.sum(distances[distances == i])
            durration = self.sample_rate * number_samples
            durration = round(durration, 2)
            self.table_of_counts.setItem(0, i-1, QTableWidgetItem(str(durration) + "s"))

        
    def derive_speed_from_distances(self, dists: np.array) -> float:
        """Calculates the speed of the boot release based on sample rate + distance
        
        Over the distance of 2mm to 10mm we travel .08 meters. Each sample is 
        taken at the same sample rate. Thus, we can derive speed

        Args:
            dists (np.array): distances returned durring data collection

        Returns:
            float: speed in meters per second
        """
        try:
            numb_distances = np.sum((dists >= 2) & (dists < 10))
            durration = numb_distances * self.sample_rate  # seconds
            speed = (.01 - .002) / durration  # meters per second
            return round(speed, 2)
        except ZeroDivisionError:
            self.logger.error("Could not derive speed from distance measurements: \n", dists)
            return 0
        
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
            self.distances = np.zeros(parent.max_index)
            self.forces = np.zeros(parent.max_index)
            
            # Setup the internal logger
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
            console_handler  = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)

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
            index = 0  # tracks location in numpy arrays for dist/force
            dist_counter = 0  # force function end after 10 instances of boot gone
            first_dist = False
            self.self.serial.reset_buffer()
            
            # Collect data for 30s or until we have 200ms of too far of dists 
            while (index < self.self.max_index) and dist_counter < 20:
                # get the arduino distance measurement to log or synchronize
                distance_measurement = self.self.serial.get_arduino_data()
                if distance_measurement != None:
                    # Want to normalize distance relative to initial distance
                    if not first_dist:
                        first_dist = distance_measurement
                    # since arduino reported data, we get phidget data and log it
                    self.forces[index] = index
                    # self.forces[index] = self.phidget.recent_measurement
                    self.distances[index] = distance_measurement - first_dist
                    index += 1
                    if (distance_measurement - first_dist) > 11:
                        dist_counter += 1
                        
                    # distance is constrained by byte of range
                    if first_dist > 240:
                        self.logger.warning("The Boot is too far away from the sensor. 240mm is the maximum distance.")
                        self.distances = np.zeros(self.self.max_index)
                        self.forces = np.zeros(self.self.max_index)
                        break
            
            self.result.emit((self.distances[:index], self.forces[:index]))
            self.finished.emit()

    def on_option_change(self):
        """Changes the state of the Arduino based on the selected option
        
        LED L is turned on when in state My. Upon state change, the Ard is queried
        until a confirmation response is found
        """
        if "Mz" in self.combo_box.currentText():
            self.serial.set_mz_state()
            self.testing_My = False
            self.combo_box.setStyleSheet(self.original_style)
            self.logger.info(f"Option changed to {self.combo_box.currentText()}")

        if "My" in self.combo_box.currentText():
            self.serial.set_my_state()
            self.testing_My = True
            self.combo_box.setStyleSheet(self.original_style)
            self.logger.info(f"Option changed to {self.combo_box.currentText()}")
        
    def save_data(self):
        """Saves the dist/force data in memory to two csvs. Processed and raw"""
        f_name = self.csv_name_input.text() + ".csv"
        f_graphed_name = self.csv_name_input.text() + "_graphed" + ".csv"
        csv_fname = os.path.join(self.log_dir, f_name)
        csv_graphed_name = os.path.join(self.log_dir, f_graphed_name)

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
            data = np.column_stack((self.distances, self.forces))
            graphed_data = np.column_stack((self.aggregate_dist, self.aggregate_force))

            # Save to CSV
            np.savetxt(csv_fname, data, delimiter=',', header='Distance[mm],Force[N]', fmt='%.4f')
            np.savetxt(csv_graphed_name, graphed_data, delimiter=',', header='Distance[mm],Force[N]', fmt='%.4f')
            
            self.logger.info("Saved data to:\n\t" + csv_fname + " and \n\t" + csv_graphed_name)
            
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
        self.csv_name_input.setText("Din_data_" + datetime.now().strftime("%Y%m%d_%H%M"))
        
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