import ast
from typing import List, Dict, Any

class PyFileParser:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def extract_data_from_py(self, file_path: str) -> List[Dict[str, Any]]:
        """
        extract info from config
        """
        with open(file_path, 'r') as file:
            content = file.read()
        
        try:
            data = ast.literal_eval(content.split('=')[1].strip())
        except Exception as e:
            print(f"Error with .py file {file_path}: {e}")
            return []

        extracted_data = []
        if "ExptRes" in data:
            for experiment in data["ExptRes"]:
                extracted_entry = self._extract_from_experiment(experiment, data["OutputStatus"], file_path)
                extracted_data.append(extracted_entry)

        return extracted_data

    def _extract_from_experiment(self, experiment: Dict[str, Any], output_status: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """
        Extract all the specific fields
        """
        entry = {
            "filename": file_path,  
            "AnalysisID": experiment.get("AnalysisID")
        }

        for key in self.config.get("OutputStatus", []):
            entry[key] = output_status.get(key, None)

        for key in self.config.get("ExptRes", []):
            entry[key] = experiment.get(key, None)

        return entry
