#!/usr/bin/env python3

#this script will simply repeat same timestamp for all records in a measurement frame to make csv processing easier

import sys
from stretch_timestamps import stretch_timestamps
from pyboard_to_posix_timestamp import convert_to_posix
from datetime import timedelta
import pandas as pd
from io import StringIO
import os

if len(sys.argv) < 4:
    print("""Usage: {} <csv_file_1> [csv_file_2 [csv_file_3 [...]]] <datetime correction file> <output folder>
    This script does following:
    - concatenates all <csv_files>
    - adds missing timestamps
    - converts PyBoard timestamps to POSIX format
    - converts timestamps to local timezone
    - stretches timeline based on <datetime correction file> (to compensate for terribly lagging RTC of PyBoard Lite)
    - groups logs by day and saves them as csv files (one file per day) in <output folder>
    - specify NONE as datetime correction file name in case data doesn't need correction""".format(sys.argv[0]))
    exit(1)

#load files and add timestamps (may need to be removed in the future - I can just add timestamps by logger itself)
csv_filenames = sys.argv[1:-2]
data = list()
for filename in csv_filenames:
    print("Loading {}".format(filename))
    ts = ''
    with open(filename, "r") as f:
        for l in f.readlines():
            vals = l.split(',')
            if vals[0]:
                ts = vals[0]
            elif ts:
                vals[0] = ts
            new_line = ','.join(vals)
            data.append(new_line)

#convert PyBoard timestamps to POSIX
print("Converting PyBoard timestamps to POSIX format")
local_time_data = convert_to_posix(data)

#stretch time based on correction file. filename of correction data should be the last argument passed
print("Adjusting log timestamps based on correction file")
stretched_log = ["Time,Xacc,Yacc,Zacc\n"] #header
if sys.argv[-2] == 'NONE':
    filename = None
else:
    filename = sys.argv[-2]
stretched_log.extend(stretch_timestamps(local_time_data, filename))

#save updated log data into files grouped by day
#use pandas to manipulate dataset
print("Splitting log into daily buckets")
target_folder = sys.argv[-1]
CSV_DF = '%Y-%m-%d %H:%M:%S'
str_io = StringIO(''.join(stretched_log)) #lines already have end of new line in the end
dframe = pd.read_csv(str_io, header=0, index_col=0, parse_dates=True, infer_datetime_format=True)
start = dframe.first_valid_index()
end = dframe.last_valid_index()
days_span = (end - start).days
days = [(start + timedelta(days=delta)).strftime('%Y-%m-%d') for delta in range(0, days_span + 1)]
print("Saving into files")
for day in days:
    fname = os.path.join(target_folder, "{}.csv".format(day))
    print("Saving {}".format(fname))
    dframe[day].to_csv(fname)
# daily_logs = {day : dframe[day] for day in days}