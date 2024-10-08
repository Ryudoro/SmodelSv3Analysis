from PyFileParser import PyFileParser
from SLHAParser import SLHAParser
from FileFinder import FileFinder

import pandas as pd
from typing import List
from tqdm import tqdm

class DataAssembler:
    def __init__(self, py_parser: PyFileParser, slha_parser: SLHAParser):
        self.py_parser = py_parser
        self.slha_parser = slha_parser

    def assemble_data(self, py_files: List[str], slha_files: List[str]) -> pd.DataFrame:
        """
        avengers, assemble !
        """
        all_data = []

        for py_file in tqdm(py_files, desc="Traitement des fichiers .py", unit="fichier"):
            py_data = self.py_parser.extract_data_from_py(py_file)
            for entry in py_data:
                slha_file = entry.get("input file")
                slha_data = self.slha_parser.extract_from_slha(slha_file)
                entry.update(slha_data)
                all_data.append(entry)

        df = pd.DataFrame(all_data)
        return df

if __name__ == "__main__": 
    config_py = {
        "OutputStatus": ["input file", "sigmacut"],
        "ExptRes": ["r", "r_expected"]
    }
    config_slha = {
        "SMINPUTS": [1],
        "MASS": [25, 6]
    }

    py_parser = PyFileParser(config_py)
    slha_parser = SLHAParser(config_slha)

    finder = FileFinder("output_EWino")
    finder2 = FileFinder("data_EWino")
    py_files = finder.find_files([".py"])
    slha_files = finder2.find_files([".slha"])
    assembler = DataAssembler(py_parser, slha_parser)
    df = assembler.assemble_data(py_files, slha_files)

    print(df)
    print(df.columns)