import pyslha
from typing import List, Dict, Any

class SLHAParser:
    def __init__(self, config: Dict[str, List[int]]):
        self.config = config

    def extract_from_slha(self, slha_file: str) -> Dict[str, Any]:
        """
        extract from slha.
        """
        try:
            slha_data = pyslha.read(slha_file)
        except Exception as e:
            print(f"Error with .slha file {slha_file}: {e}")
            return {}

        extracted_data = {}
        for block, ids in self.config.items():
            for id_ in ids:
                try:
                    extracted_data[f"{block}_{id_}"] = slha_data.blocks[block].get(id_, None)
                except:
                    print(f"Error with block {block} and id {id}")
        return extracted_data
