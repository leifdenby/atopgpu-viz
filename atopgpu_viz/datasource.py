from io import StringIO
import subprocess
import pandas as pd
import datetime

# 00:00:02     busaddr   gpubusy  membusy  memocc  memtot memuse  gputype   _gpu_
# 00:10:02   0/0000:4A:0      0%       0%      1%  46068M   559M  NVIDIA_A40
# 0123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789
PERCENTAGE_COLUMNS = ["gpubusy", "membusy", "memocc"]
SIZE_COLUMNS = ["memtot", "memuse"]
DATA_COLUMNS = PERCENTAGE_COLUMNS + SIZE_COLUMNS
ALL_COLUMNS = ["time", "busaddr"] + DATA_COLUMNS + ["gputype"]
COLUMN_FORMAT = [
    (0, 11),  # time
    (11, 22), # busaddr
    (22, 30), # gpubusy
    (30, 39), # membusy
    (40, 47), # memocc
    (47, 55), # memtot
    (56, 62), # memuse
    (63, 74), # gputype
]

def _parse_dataframe(data: str, date: datetime.date):
    # Read the data into a DataFrame
    # create the fixed-width format DataFrame
    df = pd.read_fwf(
        StringIO(data),
        colspecs=COLUMN_FORMAT,
        skiprows=1,
        names=ALL_COLUMNS,
    )
    # Forward fill the 'time' column to fill the missing values
    df["time"] = df["time"].ffill()
    
    # parse the time column
    df["time"] = pd.to_datetime(df["time"], format="%H:%M:%S")
    
    # combine the date and time columns
    df["time"] = pd.to_datetime(df["time"].dt.strftime(f"{date} %H:%M:%S"))
    
    # parse the percentage columns
    for col in PERCENTAGE_COLUMNS:
        df[col] = df[col].str.rstrip("%").astype(float) / 100

    for col in SIZE_COLUMNS:
        df[col] = df[col].str.rstrip("M").astype(int)

    return df


def get_data(date: datetime.date = None):
    if date is None:
        date = datetime.datetime.now().date()

    t_str = date.strftime("%Y%m%d")
    t_str_end = (date + datetime.timedelta(days=1)).strftime("%Y%m%d%H%M")

    # Call the bash command
    process = subprocess.Popen(
        ["atopsar", "-r", t_str, "-e", t_str_end, "-g"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Get the output
    stdout, stderr = process.communicate()

    # Decode the output
    data = stdout.decode("utf-8")

    # remove the first five lines
    data = "\n".join(data.split("\n")[5:])
    
    df = _parse_dataframe(data=data, date=date)

    return df


if __name__ == "__main__":
    print(get_data())
