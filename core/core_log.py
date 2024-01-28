#
# логирование сообщений 
#
##########################
import os
from datetime import datetime
import time

#
# Формат записей в логе
#
# DataTime  Severity    Facility    text
# где
#   Datatime  - текущее время Функция логирования возьмёт сама на момент поступления сообщения
#   Severity  - серьёзность события. Чем выше, тем серьёзней.  Основной момент. До Error - продолжать работать можно, выше приложение продолжить работу не может.
#               emergency/critical
#               error
#               warning     - возможно, что-то не указано, но система взяла значения по умолчанию и продолжает работать
#               notice      - 
#               info        - по умолчанию
#               debug
#
#   facility  - система/модуль/функция, которая отправляет сообщение
#


async def log(text, severity='info', facility="none"):
    #
    # лог файл
    #
    log_file = "./server.log"

    #
    # Файл блокировки (lock)
    # в одно время только один кто-то может писать в файл, иначе он испортится.
    # для этого процесс выставляет Флаг (Lock), пишет в файл, удаляет Флаг (unlock)
    # Остальные ждут пока предыдущий снимет блокировку
    #
    lock_file = "./server.lock"

    #
    # Чтобы не зависнуть в ожидании блокировки навечно сделаем счётчик максимального количества попыток
    # если он пройдёт - просто выйдем из функции без записи в лог
    #
    max_try = 3

    #
    # ждём удаления предыдущей блокировки
    #
    while os.path.exists(lock_file) and max_try > 0:
        time.sleep(1)
        max_try -= 1

    #
    # Если блокировка снята, но не максимальное кол-во попыток исчерпано - то можно записывать
    # ставим свою блокировку и пишем
    #
    if max_try > 0:

        try:

            #
            # Мы выставляем Lock
            #
            with open(lock_file, 'x') as lock_fhndl:
                # формируем запись
                lock_fhndl.write('BLOCK')

            #
            # берём текущую дату
            #
            dt = datetime.now()
            today = dt.strftime("%Y-%m-%d %H:%M:%S")

            #
            # PID
            #
            pid = os.getpid()

            #
            # открываем log файл для дозаписи
            #
            with open(log_file, 'a') as log_fhndl:
                #
                # формируем запись
                s = f'{today}\t{str(severity):10} '
                if len(str(facility)) < 15:
                    s += f'{str(facility):15} '
                else:
                    s += f'{str(facility)[0:15]} '
                s += f'[{str(pid)}]\t{str(text)}\n'
                log_fhndl.write(s)

            #
            # unlock
            #
            os.remove(lock_file)

        except Exception as err:
            # даже если ошибка, ни чего не делаем
            pass


#
# remove Lock from last start
#
async def init():
    lock_file = "./server.lock"

    #
    # unlock
    #
    if os.path.exists(lock_file):
        os.remove(lock_file)


# if __name__ == '__main__':
#     init()
#     log('test')
