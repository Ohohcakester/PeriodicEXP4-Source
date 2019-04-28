import csv

CSVfileName = "/home/cirlab/PeriodicEXP3/simulationResults_FINAL/change_in_data_rates_office/EXP4/distanceToNashEquilibrium.csv"
with open(CSVfileName) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count > 0 and line_count < 1441:
             print("%.2f" %(float(row[1])), end=" ")
        line_count += 1