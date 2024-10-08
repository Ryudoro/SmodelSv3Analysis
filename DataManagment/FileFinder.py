import os
from typing import List
class FileFinder:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir

    def find_files(self, extensions: List[str]) -> List[str]:
        """
        search the 0,1,2... files in the output_EWino directory
        """
        file_paths = []
        for dirpath, _, filenames in os.walk(self.root_dir):
            for file in filenames:
                if file.endswith(tuple(extensions)):
                    file_paths.append(os.path.join(dirpath, file))
        return file_paths
    
    
    