import os
import threading
import time

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def start_auto_update(interval, update_function):
    def run():
        while True:
            update_function()
            time.sleep(interval)
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()