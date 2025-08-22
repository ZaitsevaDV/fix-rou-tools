#!/usr/bin/python3
import glob
import os
import re
from datetime import datetime, timedelta
import argparse

# default values for argparse
PATHNAME = 'rou/'
DAY = '250813'
TFORM = '%Y%m%d%H%M%S'
TFORM_CHOICES = ["%y%m%d%H%M%S", "%Y%m%d%H%M%S"]

SAMPLING_PERIOD = 3
PRE = 'ZSS'

def parse_block_lines(lines, file_name):
    blocks = []
    current_block = []
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue
        if stripped_line.startswith('ROU'):
            if current_block:
                blocks.append(current_block)
            current_block = [stripped_line]
        else:
            current_block.append(stripped_line)
    if current_block:
        blocks.append(current_block)
    return blocks

def validate_block(block, file_name):
    if len(block) != 5:
        return False, f"Invalid block length in file {file_name}: {block[0]}"
    
    time_str = block[0].split()[1]
    try:
        datetime.strptime(time_str, args.tform) #, '%Y%m%d%H%M%S')
    except ValueError:
        return False, f"Invalid time format in file {file_name}: {time_str}"
    
    heights = block[1].split()[1:]
    n_heights = len(heights)
    
    for i in range(2, 5):
        data_line = block[i]
        if data_line.startswith('S') or data_line.startswith('N'):
            data = data_line.split()[2:]
        else:  # VR line
            data = data_line.replace('-',' -').split()[1:]
        if len(data) != n_heights:
            return False, f"Data length mismatch in file {file_name}: {data_line}"
    
    return True, ""

def process_files(pathname, day, sampling_period):
    files = glob.glob(f'{pathname}*{day}*')
    files.sort();

    if not files:
        print(f"No files found for day {day}")
        return

    ind = files[0].index(day)+len(day);
    T0 = files[0][ind:ind+6];
    
    # First, read all files to collect all blocks and find all antennas
    all_blocks = []
    antennas = set()
    all_heights = None
    height_str = None
    templates = {}
    
    for file_name in files:
        print(f"Processing file: {file_name}")
        with open(file_name, 'r') as f:
            lines = f.readlines()
        
        blocks = parse_block_lines(lines, file_name)
        for block in blocks:
            is_valid, error_msg = validate_block(block, file_name)
            if not is_valid:
                print(f"Error: {error_msg}")
                return
            
            time_str = block[0].split()[1]
            antenna = block[2].split()[1]
            time_val = datetime.strptime(time_str, args.tform) # '%Y%m%d%H%M%S')
            
            antennas.add(antenna)
            all_blocks.append((time_val, antenna, block))
            
            if all_heights is None:
                all_heights = block[1].split()[1:]
            if height_str is None:
                height_str = block[1]
            
            if antenna not in templates:
                templates[antenna] = block[0]
    
    if not all_blocks:
        print("No valid blocks found")
        return
    
    # Sort antennas
    antennas = sorted(antennas)
    
    # Find min and max time
    times = [block[0] for block in all_blocks]
    min_time = min(times)
    max_time = max(times)
    
    # Generate all time points from min_time to max_time with step sampling_period
    current_time = min_time
    all_times = []
    while current_time <= max_time:
        all_times.append(current_time)
        current_time += timedelta(seconds=sampling_period)
    
    # Create a dictionary for quick access to blocks
    blocks_dict = {}
    for time_val, antenna, block in all_blocks:
        if time_val not in blocks_dict:
            blocks_dict[time_val] = {}
        blocks_dict[time_val][antenna] = block
    
    # Create output data
    output_lines = []
    for time_val in all_times:
        time_str = time_val.strftime(args.tform) #'%Y%m%d%H%M%S')
        
        for antenna in antennas:
            if time_val in blocks_dict and antenna in blocks_dict[time_val]:
                # Use existing block
                block = blocks_dict[time_val][antenna]
                output_lines.extend(block)
                #print(f'time ok: {time_val}');
            else:
                # Create zero block
                zero_block = create_zero_block(time_str, antenna, height_str, templates[antenna])
                output_lines.extend(zero_block)
                #print(f'missed time: {time_val}');
    
    # Write output file
    with open(f'{args.pre}_{day}{T0}-clued.rou', 'w') as f:
        for i, line in enumerate(output_lines):
            f.write(line)
            if i < len(output_lines) - 1:
                f.write('\n')

def create_zero_block(time_str, antenna, heights, template_line):
    parts = re.split(r'(\s+)', template_line)
    # Извлекаем только непустые элементы (не пробелы)
    non_space_indices = [i for i, part in enumerate(parts) if part.strip()]
    parts[non_space_indices[1]] = time_str
    header = ''.join(parts)
    
    zero_data = ['0.0'] * len(heights.split()[1:])
    zero_data_vr = ['0.00'] * len(heights.split()[1:])
    
    block = [
        header,
        heights,
        f'S {antenna}    ' + '   '.join(zero_data),
        f'N {antenna}    ' + '   '.join(zero_data),
        f'VR{antenna}   ' + '  '.join(zero_data_vr)
    ]
    return block

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clue ROU files')
    parser.add_argument('--pathname', type=str, default=PATHNAME, help=f'Path to directory files; default: {PATHNAME}')
    parser.add_argument('--day', type=str, default=DAY, help=f'Day to process; default: {DAY}')
    parser.add_argument('--tform', default=TFORM, 
                        choices= TFORM_CHOICES,
                        help=f'Time format; default: {TFORM.replace("%","%%")}');
    parser.add_argument('--sampling', type=int, default=SAMPLING_PERIOD, help=f'Sampling period, sec; default: {SAMPLING_PERIOD}')
    parser.add_argument('--pre', type=str, default=PRE, help=f'Prefix for output file; default: {PRE}')
    args = parser.parse_args()
    process_files(args.pathname, args.day, args.sampling_period)
