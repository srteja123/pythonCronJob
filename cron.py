import schedule
import time
import subprocess
import traceback


def task():
    print("start")
    try:
        subprocess.run(['d:/Anaconda/python.exe', 'd:/PythonDevWebScraping/webScrapper.py'])
    except Exception as e:
            print('Exception error for below player:',e)
            traceback.print_exc()

schedule.every().minute.do(task) # Run every minute

while True:
    schedule.run_pending()
    time.sleep(1)