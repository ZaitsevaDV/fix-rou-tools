import os
import re
from datetime import datetime, timedelta
from collections import defaultdict
import argparse

# default parameters
TFORM="%y%m%d%H%M%S"
TFORM_CHOICES = ["%y%m%d%H%M%S", "%Y%m%d%H%M%S"]
FILE_PATH = "rou/klmeast-250725092106_MSK.rou"  # Пример файла
SAMPLING_PERIOD = 3  # Период измерений в секундах
SUF = "_fixed" # suffix for output file


def process_multi_antenna_file(file_path, sampling_period, time_format, N, output_suffix):
    # Проверка существования файла
    if not os.path.exists(file_path):
        print(f"Ошибка: файл {file_path} не существует")
        return

    # Извлекаем временную метку из названия файла
    file_name = os.path.basename(file_path)
    re_pattern = r'\d'*N;
    time_match = re.search(r'('+re_pattern+')', file_name)
    if not time_match:
        print(f"Не удалось найти временную метку в названии файла: {file_name}")
        return
    
    start_time_str = time_match.group(1)
    try:
        current_time = datetime.strptime(start_time_str, time_format) 
    except ValueError:
        print(f"Неверный формат временной метки в названии файла: {start_time_str}")
        return
    
    # Читаем файл
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Определяем количество антенн и их порядок
    antenna_blocks = defaultdict(list)
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
    
    # Определяем номера антенн и их порядок
    antenna_order = []
    for block in blocks:
        if len(block) >= 3:  # Как минимум ROU, H и S линии
            s_line = block[2]  # Строка с сигналом (S i)
            antenna_num = s_line.split()[1]  # Номер антенны
            if antenna_num not in antenna_order:
                antenna_order.append(antenna_num)
    
    num_antennas = len(antenna_order)
    print(f"Обнаружено антенн: {num_antennas}")
    print(f"Порядок антенн: {antenna_order}")
    
    # Обрабатываем блоки
    output_lines = []
    time_slot_count = 0
    
    for i, block in enumerate(blocks):
        # Определяем, к какому временному слоту относится этот блок
        time_slot = i // num_antennas
        antenna_index = i % num_antennas
        
        # Если это первый блок нового временного слота, увеличиваем время
        if antenna_index == 0 and time_slot > 0:
            current_time += timedelta(seconds=sampling_period)
            time_slot_count += 1
        
        # Заменяем '-' на текущее время
        time_str = current_time.strftime(time_format) 
        parts = block[0].split()
        parts[1] = time_str
        modified_line = ' '.join(parts)
        
        output_lines.append(modified_line)
        output_lines.extend(block[1:])
    
    # Записываем измененный файл
    base_name, ext = os.path.splitext(file_path)
    output_file = f"{base_name}_{output_suffix}{ext}"
    
    with open(output_file, 'w') as f:
        for line in output_lines:
            f.write(line + '\n')
    
    print(f"Обработано временных слотов: {time_slot_count + 1}")
    print(f"Обработано блоков: {len(blocks)}")
    print(f"Результат сохранен в: {output_file}")

# Пример использования
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add timestamps to ROU file')
    parser.add_argument('--fpath', default=FILE_PATH, help=f'Path to the ROU file; default: {FILE_PATH}')
    parser.add_argument('--tform', default=TFORM, 
                        choices= TFORM_CHOICES,
                        help=f'Time format; default: {TFORM.replace("%","%%")}')
    parser.add_argument('--sampling', type=int, default=3,
                        help=f'Sampling period, sec; default: {SAMPLING_PERIOD}')
    parser.add_argument('--suff', default=SUF,
                        help='Suffix for output file default: _fixed')
    
    args = parser.parse_args()
    
    # Определяем N на основе формата времени
    if args.time_format == "%y%m%d%H%M%S": 
        N = 12
    else:  # "%Y%m%d%H%M%S"
        N = 14
    
    process_multi_antenna_file(args.fpath, args.sampling, args.tformat, N, args.suff)
