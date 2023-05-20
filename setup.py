import os

CURR_DIR = os.getcwd()
WEB_DIR = os.path.join(CURR_DIR, "web")
CMD_DIR = os.path.join(CURR_DIR, "cmd")
TMP_DIR = os.path.join(WEB_DIR, "tmp")

print("Setting up env variables...")
with open('.env', 'w') as f:
    f.write(
        f"GRANALYS_PATH = '{CURR_DIR}'\nWEB_CONFIG = '{WEB_DIR}'\nCMD_CONFIG = '{CMD_DIR}'\n "
        )
    
print(f"Creating '{TMP_DIR}' directory...")
try:
    os.mkdir(TMP_DIR)
except:
    print(f"'{TMP_DIR}' already exists")