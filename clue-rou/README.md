# Clue rou

Программа для склеивания файлов .rou в рамках одного дня
Программа ищет в заданной директории все файлы, содержащие заданный день в названии, записывает их в выходной файл по порядку, пробелы в измерениях заполняет нулями.

Если в файле есть некорректно записанный блок данных, программа выдаёт ошибку с указанием первой строки блока (ROU YYmmddHHMMSS ...)


## Установка

1. Скопируйте файл `clueRouFiles.py` на свой компьютер
2. ???
3. PROFIT!

## Использование

Если программе на вход не дан ни один аргумент, то она использует параметры по умолчанию (перечислены в начале файла программы) 
Все входные параметры опциональные

Пример использования

python3 clueRouFiles.py --pathname rou/ --day 250813 --tform %y%m%d%H%M%S --sampling 3 --pre zss

## Справка
Вызов справки 
clueRouFiles.py -h

usage: clueRouFiles.py [-h] [--pathname PATHNAME] [--day DAY] [--tform {%y%m%d%H%M%S,%Y%m%d%H%M%S}] [--sampling SAMPLING] [--pre PRE]

Clue ROU files

options:
  -h, --help            show this help message and exit
  
  --pathname PATHNAME   Path to directory files; default: rou/
  --day DAY             Day to process; default: 250813
  --tform {%y%m%d%H%M%S,%Y%m%d%H%M%S}
                        Time format; default: %Y%m%d%H%M%S
  --sampling SAMPLING   Sampling period, sec; default: 3
  --pre PRE             Prefix for output file; default: ZSS


