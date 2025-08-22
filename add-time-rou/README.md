# add time in ROU
Программа читает .rou файл. Из его имени извлекает метку времени первого измерения, заменяет прочерки на метки времени и записывает в новый файл.

## Установка

1. Скопируйте файл `addTimeRouFile.py` на свой компьютер
2. ???
3. PROFIT!

## Использование

Если программе на вход не дан ни один аргумент, то она использует параметры по умолчанию (перечислены в начале файла программы) 

Пример использования
python3 addTimeRouFiles.py --fpath rou/tss250813000000.rou --tform %y%m%d%H%M%S --sampling 3 --suf -fixed

## Справка
Вызов справки 
addTimeRouFile.py -h

Справка
usage: addTimeRouFiles.py [-h] [--fpath FPATH] [--tform {%y%m%d%H%M%S,%Y%m%d%H%M%S}] [--sampling SAMPLING] [--suff SUFF]

Add timestamps to ROU file

options:
  -h, --help            show this help message and exit
  --fpath FPATH         Path to the ROU file; default: rou/klmeast-250725092106_MSK.rou
  --tform {%y%m%d%H%M%S,%Y%m%d%H%M%S}
                        Time format; default: %y%m%d%H%M%S
  --sampling SAMPLING   Sampling period, sec; default: 3
  --suff SUFF           Suffix for output file default: _fixed




