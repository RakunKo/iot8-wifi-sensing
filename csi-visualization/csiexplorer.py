'''
    ======= Plot type =======
    1.Amplitude-Packet Index (Default)
    2.Amplitude-Time
    3.Amplitude-Packet Heatmap
    4.Amplitude-Time Heatmap
    5.Amplitude-Subcarrier Index
    6.Amplitude-Subcarrier Index Flow
'''
import os
import argparse
import pandas as pd
import util

from cfg import config
from plot.ampPlotter import AmpPlotter, AmpTimePlotter, AmpSubcarrierPlotter, AmpSubcarrierFlowPlotter
from plot.heatmap import heatmap, timeHeatmap


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('directory', type=str, help='name of CSI data directory')
parser.add_argument('-p', '--plt', type=int, default=1, help='Select Plot type')
parser.add_argument('--sub', type=util.str2bool, default=False, help='Use specific subcarriers(Boolean)')
parser.add_argument('--smp', type=util.str2bool, default=False, help='Use data sampling(Boolean)')

args = parser.parse_args()

csi_dir = args.directory
use_specific_sub = args.sub

try:
    data_path = os.path.join('./data', csi_dir)
    csi_list = os.listdir(data_path)
except FileNotFoundError as e:
    print(e)
    print('Exit program')
    exit()

# Check Plot type index
plot_type_idx = args.plt
if not 1 <= plot_type_idx <= 6:
    print('Wrong Plot type Index!')
    exit()

# Read from config file
plot_params_dict = config.PLOT_PARAMETER
null_pilot_dict = config.NULL_PILOT_SUBCARRIER
extractor_dict = config.EXTRACTOR_CONFIG

bandwidth = extractor_dict['bandwidth']
null_list = null_pilot_dict['null_' + bandwidth]
pilot_list = null_pilot_dict['pilot_' + bandwidth]

use_sampling = args.smp

if use_sampling is True:
    # Sampling index (default is 0 to 1000)
    sampling_idx_list = plot_params_dict['sampling_idx']

# If use specific subcarriers(Not all subcarriers)
if use_specific_sub is True:
    sub_list = plot_params_dict['specific_subcarriers']


if __name__ == "__main__":

    for csi_fname in csi_list:

        if csi_fname == '.DS_Store':
            continue

        csi_path = os.path.join(data_path, csi_fname)

        # Read csi.csv
        df = pd.read_csv(csi_path, encoding='windows-1252')

        # Remove MAC address, timestamp
        csi_df = df.iloc[:, 2:]

        # Convert complex number to amplitude
        csi_df = util.complexToAmp(csi_df)

        # Remove outlier
        if plot_params_dict['rmv_outlier'] is True:
            csi_df = csi_df[(csi_df < plot_params_dict['outlier_thres'])]

        csi_df = csi_df.drop(columns=null_list, errors='ignore')
        csi_df = csi_df.drop(columns=pilot_list, errors='ignore')

        # #####  Plot  #####

        # 1.Amplitude-Packet Index (Default)
        if plot_type_idx == 1:
            # Set sampling index
            if use_sampling is True:
                sample_start = sampling_idx_list[0]
                sample_end = sampling_idx_list[1]
            else:
                sample_start = 0
                sample_end = len(csi_df)

            # If use only few subcarriers
            if use_specific_sub is True:
                print(sub_list)
                AmpPlotter(csi_df, sample_start, sample_end, csi_fname, sub_list)
            # Use all subcarriers
            else:
                AmpPlotter(csi_df, sample_start, sample_end, csi_fname)

    

        # 3.Amplitude - Packet Heatmap
        elif plot_type_idx == 3:
            # Set sampling index
            if use_sampling is True:
                sample_start = sampling_idx_list[0]
                sample_end = sampling_idx_list[1]
            else:
                sample_start = 0
                sample_end = len(csi_df)

            heatmap(csi_df, sample_start, sample_end, csi_fname)

    
        # 5.Amplitude-Subcarrier Index
        elif plot_type_idx == 5:
            # Set sampling index
            if use_sampling is True:
                sample_start = sampling_idx_list[0]
                sample_end = sampling_idx_list[1]
            else:
                sample_start = 0
                sample_end = len(csi_df)

            AmpSubcarrierPlotter(csi_df, sample_start, sample_end)

        # 6.Amplitude-Subcarrier Index Flow
        elif plot_type_idx == 6:
            # Set sampling index
            if use_sampling is True:
                sample_start = sampling_idx_list[0]
                sample_end = sampling_idx_list[1]
            else:
                sample_start = 0
                sample_end = len(csi_df)

            AmpSubcarrierFlowPlotter(csi_df, sample_start, sample_end)