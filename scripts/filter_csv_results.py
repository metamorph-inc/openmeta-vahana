import csv
data = []
with open('output_edited.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in reader:
        data.append(row)

filteredData = []
firstRow = True
for row in data:
    rowData = row[0].split(',')
    if firstRow:
        filteredData.append(row)
        firstRow = False
    elif (rowData[3] == '1.0') and (rowData[4] == '1.0') and (rowData[5] == '1.0') and (rowData[6] == '1.0') and (rowData[7] == '1.0') and (rowData[8] == '1.0'):
        filteredData.append(row)

with open('filtered_data.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for row in filteredData:
        writer.writerow(row)
