import sys
from pathlib import Path

# DIRTY TRICK SO THAT sdb module can be found by manipulating PYTHONPATH
file_path = Path(__file__)
project_directory = file_path.parent.parent
sys.path.append(str(project_directory))
