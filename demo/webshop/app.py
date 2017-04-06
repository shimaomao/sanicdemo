import os
from cubes.server.base import create_server, run_server
from cubes.server.utils import str_to_bool

# Set the configuration file
try:
    CONFIG_PATH = os.environ["SLICER_CONFIG"]
except KeyError:
    CONFIG_PATH = os.path.join(os.getcwd(), "slicer.ini")



run_server("slicer.ini")