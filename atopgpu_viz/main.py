import pandas as pd
from io import StringIO
import re
import subprocess

data = """
00:10:02   0/0000:4A:0      0%       0%      1%  46068M   559M  NVIDIA_A40
           1/0000:61:0      0%       0%      1%  46068M   559M  NVIDIA_A40
           2/0000:CA:0      0%       0%      1%  46068M   559M  NVIDIA_A40
           3/0000:E1:0     36%      34%     73%  46068M 33822M  NVIDIA_A40
00:20:02   0/0000:4A:0      0%       0%      1%  46068M   559M  NVIDIA_A40
           1/0000:61:0      0%       0%      1%  46068M   559M  NVIDIA_A40
           2/0000:CA:0      0%       0%      1%  46068M   559M  NVIDIA_A40
           3/0000:E1:0     36%      34%     63%  46068M 29046M  NVIDIA_A40
00:30:02   0/0000:4A:0      0%       0%      1%  46068M   559M  NVIDIA_A40
           1/0000:61:0      0%       0%      1%  46068M   559M  NVIDIA_A40
           2/0000:CA:0      0%       0%      1%  46068M   559M  NVIDIA_A40
           3/0000:E1:0     34%      33%     73%  46068M 33822M  NVIDIA_A40
00:40:02   0/0000:4A:0      0%       0%      1%  46068M   559M  NVIDIA_A40
           1/0000:61:0      0%       0%      1%  46068M   559M  NVIDIA_A40
           2/0000:CA:0      0%       0%      1%  46068M   559M  NVIDIA_A40
           3/0000:E1:0     34%      32%     37%  46068M 17191M  NVIDIA_A40
00:50:02   0/0000:4A:0      0%       0%      1%  46068M   559M  NVIDIA_A40
           1/0000:61:0      0%       0%      1%  46068M   559M  NVIDIA_A40
           2/0000:CA:0      0%       0%      1%  46068M   559M  NVIDIA_A40
"""

def _parse_dataframe(data: str):
    # Read the data into a DataFrame
    # create the fixed-width format DataFrame
    format = [
        (0, 8),
        (8, 20),
        (20, 27),
        (27, 34),
        (34, 41),
        (41, 48),
        (48, 55),
        (55, 63),
        (63, 70),
    ]
    df = pd.read_fwf(
        StringIO(data),
        colspecs=format,
        skiprows=1,
        names=[
            "time",
            "busaddr",
            "gpubusy",
            "membusy",
            "memocc",
            "memtot",
            "memuse",
            "gputype",
            "_gpu_",
        ],
    )
    # Forward fill the 'time' column to fill the missing values
    df["time"].fillna(method="ffill", inplace=True)

    return df


def main():

    # Call the bash command
    process = subprocess.Popen(['atopsar', '-g'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Get the output
    stdout, stderr = process.communicate()

    # Decode the output
    data = stdout.decode('utf-8')
    
    # remove the first five lines
    data = '\n'.join(data.split('\n')[5:])
    
    df = _parse_dataframe(data)
    print(df)

main()

# Now you can use the 'data' variable as your data

