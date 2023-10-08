import platform
from configparser import ConfigParser

config = r"configs/config.ini"


configFile = ConfigParser()

configFile.read(config)


filesData = configFile["FILES"]

path = "Builds/"

if platform.system() == "Windows":
    path += "Windows/"
    path += filesData["path"]

else:
    path += "Linux/"
    path += filesData["path"]
    path += "/linux.x86_64"

print(path)