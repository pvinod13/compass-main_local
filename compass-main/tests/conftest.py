# import pytest
# from selenium import webdriver
# import chromedriver_autoinstaller
# import threading
# import subprocess
# from os import path


# def start_dash_app_frozen():
#     path_dir = path.abspath(r'.\src\app.py')
#     subprocess.Popen(r'C:\VirtualEnvironment\webapppoc\Scripts\python ' + path_dir, shell=True)


# def check_server_was_killed():
#     proc = subprocess.Popen(r"""netstat -ano | findStr "PID :8050" | findStr "State LISTENING\"""", shell=True, stdout=subprocess.PIPE)
#     if len(proc.stdout.readlines()) > 1:
#         pytest.fail("server not killed")

# @pytest.fixture()
# def url():
#     return "http://127.0.0.1:8050/"

# @pytest.fixture()
# def chrome_driver():
#     chrome_options = webdriver.ChromeOptions()
#     # chrome_options.add_argument('--headless')
#     # chrome_options.add_argument('--no-sandbox')
#     # chrome_options.add_argument('--disable-dev-shm-usage')
#     chrome_driver = webdriver.Chrome(chromedriver_autoinstaller.install(), chrome_options=chrome_options)
#     server_thread = threading.Thread(target=start_dash_app_frozen())
#     server_thread.start()

#     yield chrome_driver
#     server_thread.join()
#     check_server_was_killed()
