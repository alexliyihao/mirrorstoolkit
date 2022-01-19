import pandas as pd
import os

class Validator():
    """
    a skeleton for a data validator
    """
    def __init__(self, verbose):
        self.verbose = verbose

    def _get_folders(self, csv_path, folder_ID):
        """
        get a dictionary of folders need for a specific csv output
        """
        df = pd.read_csv(csv_path, index_col = 0)
        ID_dict = dict(df[folder_ID])
        return ID_dict

    def validate(self, csv_file):
        bam_dict = self._get_folders(csv_file)
        bad_dict = self._list_invalid_input(bam_dict)
        if len(bad_dict) == 0:
            if self.verbose:
                print(f"Pass: All the related files to {os.path.basename(csv_file)} is validated")
            return []
        else:
            if self.verbose:
                print(f"Failed: the following {len(bad_dict)} items need a further check")
                for key, values in bad_dict.items():
                    print(f"row index {key}, file {values}")
            return bad_dict

    def _validate_input(self, path):
        pass

    def _list_invalid_input(self, bam_dict):
        """
        run _validate_input on all the returnings
        """
        return {key: value for key, value in bam_dict.items() if not self._validate_input(value)}
