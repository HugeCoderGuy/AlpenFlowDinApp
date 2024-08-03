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

        self.initUI()
        # TODO bring code over from qtplot to this application
        
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
        
    def reset_data(self):
        self.curr_data_i = 0
        self.max_strain_dist = 0
        self.max_strain = 0
        self.strains = np.zeros(self.max_index)
        self.distances = np.zeros(self.max_index)  # maybe specify data type
        
    # def sample_sensors(self):
    #     distance_measurement = self.serial.get_arduino_data()
    #     if distance_measurement != None:
    #         self.strains[self.curr_data_i] = self.phidget.recent_measurement
    #         self.distances[self.curr_data_i] = distance_measurement
    #         if len(np.where(self.distances > 10, self.distances)) > 10:
    #             # Stop data collection after 10 data samples greater than 10
    #             pass
    
    def initalize_data_collection(self):
        self.safe_for_processing = False
        self.worker = self.Worker(self)
        self.worker.result.connect(self.handle_result)
        self.worker.finished.connect(self.task_finished)
        self.worker.start()
        self.label.setText("Working...")
        
    def handle_result(self, result):
        self.distances, self.forces = result
        self.max_force = self.forces.max()
        
    def task_finished(self):
        self.safe_for_processing = True
            
    class Worker(QThread):
        finished = pyqtSignal()
        result = pyqtSignal(tuple)

        def __init__(self, parent):
            super().__init__(parent)
            self.self = parent
            self.distances = np.zeros(parent.max_index)
            self.forces = np.zeros(parent.max_index)

        def run(self):
            index = 0
            dist_counter = 0
            while (index < self.self.max_index) and dist_counter < 10:
                distance_measurement = self.self.serial.get_arduino_data()
                if distance_measurement != None:
                    self.forces[index] = self.phidget.recent_measurement
                    self.distances[index] = distance_measurement
                    index += 1
                    if distance_measurement > 10:
                        dist_counter += 1
            
            self.result.emit((self.distances[:index],self.forces[:index]))
            self.finished.emit()
                            
    # Below is the pyQT code
    def process_results(self):
        self.max_strain = self.strains.max()
        self.max_strain_dist = False #Need to find index of max
        
    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout(main_widget)

        top_buttons = QHBoxLayout(main_widget)
        top_buttons.setSpacing(5)
        layout.addLayout(top_buttons)
        # Add the combo box to select options
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Testing Mz", "Testing My"])
        self.combo_box.currentIndexChanged.connect(self.on_option_change)
        top_buttons.addWidget(self.combo_box)
        
        self.bsl_label = QLabel("BSL:")
        top_buttons.addWidget(self.bsl_label)
        # allow only integers
        onlyInt = QIntValidator()
        onlyInt.setRange(200, 400)
        self.line_edit = QLineEdit("300")
        self.line_edit.setMaximumWidth(100)
        self.line_edit.setValidator(onlyInt)
        # self.line_edit.setMaxLength(3)
        
        top_buttons.addWidget(self.line_edit)
        
        #         lever_arm_layout = QHBoxLayout()
        # lever_arm_layout.setSpacing(2)  # Set spacing between the widgets
        lever_arm = QLabel("\t\t\tFile Name:")
        top_buttons.addWidget(lever_arm)
        self.csv_name_input = QLineEdit("Din_data_" + datetime.now().strftime("%Y%m%d_%H%M"))
        top_buttons.addWidget(self.csv_name_input)
        self.csv_name_input.setFixedWidth(250)
        mm_label = QLabel(".csv")
        top_buttons.addWidget(mm_label)
        self.button1 = QPushButton("Save Data")
        self.button1.clicked.connect(self.save_data)
        top_buttons.addWidget(self.button1)
        
        
        # button_layout.addLayout(lever_arm_layout)


        # Add the graph
        plot_and_buttons = QHBoxLayout()
        layout.addLayout(plot_and_buttons)
        
        # Vertical layout for the plot on the left side
        plot_layout = QVBoxLayout()
        # self.plot_widget = pg.PlotWidget()
        # plot_layout.addWidget(self.plot_widget)
        self.plot_widget = FigureCanvas(plt.Figure())
        # self.canvas.setFixedSize(400, 300)
        plot_layout.addWidget(self.plot_widget)
        plot_and_buttons.addLayout(plot_layout)
        
        self.ax = self.plot_widget.figure.subplots()


        # Add the buttons and value displays
        button_layout = QVBoxLayout()
        button_layout.setSpacing(50)  # Set spacing between the widgets

        self.button_reset = QPushButton("Reset Data")
        self.button_reset.clicked.connect(self.on_button1_click)
        button_layout.addWidget(self.button_reset)

        self.value_display1 = QLabel("Peak My/BSL(N): 0")
        button_layout.addWidget(self.value_display1)
        
        self.value_display1 = QLabel("Z value (ISO 13992): 0")
        button_layout.addWidget(self.value_display1)
        
        self.value_display1 = QLabel("Z value (ISO 11088): 0")
        button_layout.addWidget(self.value_display1)

        # Create a button to plot data
        self.button = QPushButton("Plot Graph", self)
        self.button.clicked.connect(self.plot_graph)
        button_layout.addWidget(self.button)
        
        plot_and_buttons.addLayout(button_layout)
        self.multiplier = 1



        
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
            return
        else:
            # Stack the arrays column-wise
            data = np.column_stack((self.distances, self.forces))

            # Save to CSV
            np.savetxt(csv_fname, data, delimiter=',', header='Distance[mm],Force[N]')
            
            self.logger.info("Saved data to: " + csv_fname)
            
            self.original_style = self.button.styleSheet()

            # Change the button color
            self.button1.setStyleSheet("background-color: green")
            self.button1.setText("Saved!")

            # Set a timer to revert the color after 2 seconds (2000 milliseconds)
            QTimer.singleShot(1000, self.revert_color)

    def revert_color(self):
        # Revert the button color to the original style
        self.button1.setStyleSheet(self.original_style)
        self.button1.setText("Save Data")
            
        
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