import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# right click the file and copy relative path
csv_file_relative_path = "Data\Alpenflow 89, My, PL=2.6, 20241228, Trial 1_raw_torque_div_bsl.csv"


with open(csv_file_relative_path) as file:
    first_line = file.readline()
    xlabel = first_line.split(",")[0]
    ylabel = first_line.split(",")[1][:-1]  # ignore new line
    

data = pd.read_csv(csv_file_relative_path)
sns.scatterplot(data, x=xlabel, y=ylabel)
plt.xlabel(xlabel[2:])
plt.ylabel(ylabel)
plt.title(csv_file_relative_path.split("\\")[-1])
plt.show()
    
