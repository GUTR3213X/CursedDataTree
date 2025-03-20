from os import system
from typing import List
from threading import Thread
import curses
from time import (
    perf_counter,
    sleep
)
from .std import Print

def beep(tom: float, freq: float, pad: float, repeat: int):
    # Verifica se o comando 'play' está disponível
    if system("command -v play > /dev/null 2>&1") != 0:
        raise RuntimeError("O comando 'play' não foi encontrado. Instale o SoX.")
    
    # O comando abaixo gera o tom e o silêncio (pad) e repete o ciclo
    system(f'play -nq -t alsa synth {tom} sine {freq} pad 0 {pad} repeat {repeat}')

def AddLinesWhileBeep(
        window: curses.window, 
        string: str, 
        beep_freq: float = 6525,
        base_delay: float = 0.06,
        beep_tom: float = 0.01):
    """
    base_delay: tempo total desejado para cada iteração (incluindo tempo de operações do curses e o delay)
    beep_tom: duração do tom audível em cada ciclo
    """
    # Número de linhas a serem exibidas
    lines = string.count('\n') + 1
    # Para sincronizar, cada ciclo do beep deverá durar exatamente base_delay
    # Então, o tempo de silêncio (pad) será:
    pad_delay = base_delay - beep_tom
    if pad_delay < 0:
        raise ValueError("base_delay deve ser maior que beep_tom para garantir um intervalo não negativo.")
    
    def AddLines():
        curses.curs_set(0)
        _print = Print(window)

        for line in string.split('\n'):
            start_time = perf_counter()
            
            _print(line, end='')
            window.refresh()
            
            # Calcula o tempo gasto nas operações de curses
            exec_time = perf_counter() - start_time
            # Ajusta o sleep para que cada iteração dure aproximadamente base_delay
            adjusted_sleep = max(0, base_delay - exec_time)
            sleep(adjusted_sleep)
    
    def Beep():
        # Para N linhas, temos N ciclos de beep. Como o primeiro ciclo já é executado, usa-se repeat = lines - 1
        beep(tom=beep_tom, freq=beep_freq, pad=pad_delay, repeat=lines - 1)
    
    threads: List[Thread] = [
        Thread(target=AddLines),
        Thread(target=Beep)
    ]
    
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
