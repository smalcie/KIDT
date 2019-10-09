import sys
sys.path.append(r'C:\Users\flowerm\PyDev\segyio\venv\Lib\site-packages')
import glob
import os.path
import re
import segyio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# path_to_files = 'data\\MATAI_2003\\'
path_to_files = 'data\\MATUKU-2D\\'




def get_file_names(path):
    return glob.glob(f'{path}*.sgy')


def parse_trace_headers(segyfile, n_traces):
    '''
    Parse the segy file trace headers into a pandas dataframe.
    Column names are defined from segyio internal tracefield
    One row per trace
    '''
    # Get all header keys
    headers = segyio.tracefield.keys
    # Initialize dataframe with trace id as index and headers as columns
    df = pd.DataFrame(index=range(1, n_traces + 1),
                      columns=headers.keys())
    # Fill dataframe with all header values
    for k, v in headers.items():
        df[k] = segyfile.attributes(v)[:]
    return df


def parse_text_header(segyfile):
    '''
    Format segy text header into a readable, clean dict
    '''
    raw_header = segyio.tools.wrap(segyfile.text[0])
    # Cut on C*int pattern
    cut_header = re.split(r'C ', raw_header)[1::]
    # Remove end of line return
    text_header = [x.replace('\n', ' ') for x in cut_header]
    text_header[-1] = text_header[-1][:-2]
    # Format in dict
    clean_header = {}
    i = 1
    for item in text_header:
        key = "C" + str(i).rjust(2, '0')
        i += 1
        clean_header[key] = item
    return clean_header


files = get_file_names(path_to_files)
df_dict = {}
for file in files:
    print(f'Processing file - {os.path.basename(file)}')
    segy_qc = {}
    with segyio.open(file, ignore_geometry=True) as f :
        segy_qc['n_traces'] = f.tracecount
        segy_qc['sample_rate'] = segyio.tools.dt(f) / 1000
        segy_qc['n_samples'] = f.samples.size
        segy_qc['twt'] = f.samples
        segy_qc['bin_headers'] = f.bin
        segy_qc['text_headers'] = segyio.tools.wrap(f.text[0])
        segy_qc['trace_headers'] = parse_trace_headers(f, f.tracecount)
        segy_qc['data'] = f.trace.raw[:]
        df_dict[os.path.basename(file)] = segy_qc

# plot setup for cdp xy locations
plt.style.use('ggplot')
fig1, ax1 = plt.subplots(1, 1, figsize=(12, 8))
ax1.set_xlabel('Easting (m)')
ax1.set_ylabel('Northing (m)')
ax1.set_title('Source XY QC')


fig2, ax2 = plt.subplots(1, 1, figsize=(18, 8))
ax2.set_xlabel('CDP number')
ax2.set_ylabel('TWT (ms)')
clip_percentile = 85
for k, v in df_dict.items():
    print(k)
    print(f"N Traces: {v['n_traces']}, N Samples: {v['n_samples']}, Sample rate: {v['sample_rate']}")
    extent = [1, v['n_traces'], v['twt'][-1], v['twt'][0]]
    vm = np.percentile(v['data'], clip_percentile)
    ax2.set_title(k)
    ax2.imshow(v['data'].T, cmap="seismic", vmin=-vm, vmax=vm, aspect='auto', extent=extent)
    fig2.savefig(f'{k}.png')
    plt.close(fig2)
    ax1.plot(v['trace_headers']['SourceX'], v['trace_headers']['SourceY'], label=k)
ax1.legend()
plt.show()


