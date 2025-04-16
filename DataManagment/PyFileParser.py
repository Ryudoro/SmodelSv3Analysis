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
        
        # Explicitly retrieve 'input file' and 'OutputStatus' from data
        input_file = data.get("input file", None)
        output_status = data.get("OutputStatus", {})
        
        base_entry = {
            "filename": file_path,
            "input file": input_file,
            "AnalysisID": None  # Default if ExptRes is absent
        }
        for key in self.config.get("OutputStatus", []):
            base_entry[key] = output_status.get(key, None)
        
        if "ExptRes" in data:
            for experiment in data["ExptRes"]:
                entry = base_entry.copy()  # Copy base entry for each experiment
                entry["AnalysisID"] = experiment.get("AnalysisID")
                
                # Add experiment-specific fields
                for key in self.config.get("ExptRes", []):
                    if key == "TxNames":
                        entry[key] = tuple(experiment.get(key, None))
                        continue
                    entry[key] = experiment.get(key, None)
                
                extracted_data.append(entry)
        else:
            # If ExptRes is not present, add the base entry
            extracted_data.append(base_entry)

        return extracted_data

    def _extract_from_experiment(self, experiment: Dict[str, Any], output_status: Any, input_file: str, file_path: str) -> Dict[str, Any]:
        """
        Extract all the specific fields
        """
        entry = {
            "filename": file_path,  
            "AnalysisID": experiment.get("AnalysisID"),
            "input file": input_file,
            "OutputStatus": output_status
        }

        for key in self.config.get("OutputStatus", []):
            entry[key] = output_status.get(key, None) if isinstance(output_status, dict) else output_status

        for key in self.config.get("ExptRes", []):
            entry[key] = experiment.get(key, None)

        return entry
