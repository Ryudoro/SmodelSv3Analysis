from PyFileParser import PyFileParser
from SLHAParser import SLHAParser
from FileFinder import FileFinder

import pandas as pd
from typing import List
from tqdm import tqdm
import os, sys
import pickle

class DataAssembler:
    def __init__(self, py_parser: PyFileParser, slha_parser: SLHAParser):
        self.py_parser = py_parser
        self.slha_parser = slha_parser

    def load_from_cache(self, cache_type: str, cache_file: str) -> pd.DataFrame:
        """
        Load data from cache file (either CSV or pickle).
        """
        if cache_type == "csv" and os.path.exists(cache_file):
            print(f"Loading data from {cache_file}")
            return pd.read_csv(cache_file, index_col = False)
        elif cache_type == "pickle" and os.path.exists(cache_file):
            print(f"Loading data from {cache_file}")
            with open(cache_file, "rb") as f:
                return pickle.load(f)
        else:
            print(f"No cache file found at {cache_file}")
            return pd.DataFrame()

    def save_to_cache(self, df: pd.DataFrame, csv_file: str, pickle_file: str):
        """
        Save the dataframe to CSV and pickle files.
        """
        print(f"Saving data to {csv_file} and {pickle_file}")
        print(df.columns)
        df.to_csv(csv_file, index=False)
        with open(pickle_file, "wb") as f:
            pickle.dump(df, f)

    def _check_missing_fields(self, df: pd.DataFrame, required_fields: List[str]) -> pd.DataFrame:
        """
        Check for missing fields in the DataFrame. If a required field is not present in the DataFrame,
        it's considered as missing.
        """
        missing_columns = [field for field in required_fields if field not in df.columns]

        if missing_columns:
            print(f"Missing columns in cache: {missing_columns}")
        else:
            return pd.DataFrame()
        existing_fields = [field for field in required_fields if field in df.columns]
        if existing_fields:
            missing_df = df[df[existing_fields].isnull().any(axis=1)]
        else:
            missing_df = df

        return missing_df

    def assemble_data(self, py_files: List[str], slha_files: List[str], use_cache: str = "csv", csv_file: str = "cache_output.csv", pickle_file: str = "cache_output.pkl") -> pd.DataFrame:
        """
        Load data from cache or process the files and save to cache.
        """
        df = self.load_from_cache(use_cache, csv_file if use_cache == "csv" else pickle_file)

        required_py_fields = ["filename"] + self.py_parser.config["OutputStatus"] + self.py_parser.config["ExptRes"]
        required_slha_fields = [f"{block}_{id_}" for block, ids in self.slha_parser.config.items() for id_ in ids]
        required_fields = required_py_fields + required_slha_fields

        if not df.empty:
            print("Data loaded from cache.")
            
            missing_df = self._check_missing_fields(df, required_fields)

            if missing_df.empty:
                print("All required fields are present in the cache.")
                return df
            else:
                print("Some required fields are missing, completing missing data.")
        else:
            print("Cache not found or empty, processing all files.")
            df = pd.DataFrame()

        all_data = []
        for py_file in tqdm(py_files, desc="Traitement des fichiers .py", unit="fichier"):
            py_data = self.py_parser.extract_data_from_py(py_file)
            for entry in py_data:
                slha_file = entry.get("input file")
                
                if slha_file not in slha_files:
                    print(f"SLHA file {slha_file} missing from provided files.")
                    continue
                
                existing_entry = df[df["filename"] == entry["filename"]]
                
                if not existing_entry.empty:
                    missing_fields = existing_entry.isnull().any(axis=1)

                    if missing_fields.any():
                        slha_data = self.slha_parser.extract_from_slha(slha_file)
                        entry.update(slha_data)
                        all_data.append(entry)
                else:
                    slha_data = self.slha_parser.extract_from_slha(slha_file)
                    entry.update(slha_data)
                    all_data.append(entry)

        new_df = pd.DataFrame(all_data)

        self.save_to_cache(new_df, csv_file, pickle_file)
        return new_df


if __name__ == "__main__": 
    config_py = {
        "OutputStatus": ["input file", "sigmacut"],
        "ExptRes": ["r", "r_expected"]
    }
    config_slha = {
        "SMINPUTS": [1],
        "MASS": [25, 6, 24],
        "NMIX" : [11]
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