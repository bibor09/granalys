import os

with open('.env', 'w') as f:
    f.write(
        f"GRANALYS_PATH = '{os.getcwd()}'\nWEB_CONFIG = '{os.getcwd()}/web'\nCMD_CONFIG = '{os.getcwd()}/cmd'\n "
        )