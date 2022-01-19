from ..utils import utils
import os

class path_settings():
    """
    a path_settings class for DataManager
    """

    def __init__(self):
        self.ROOT = ""
        self.DATAMETA = {}

    def validate(self):
        if os.path.exists(self.ROOT)):
            print(f"Root folder {self.ROOT} verified")
        else:
            print(f"Root folder {self.ROOT} not verified: cannot find the root folder")


class DataManager():

    def __init__(self, path_settings):
        """
        init the DataManagement instance, with a specific version to be used
        """
        # get the root
        self.root = path_settings.ROOT

        # load the paths to be defined
        self.paths = utils.DotDict({
            datatype_name: datatype_meta["path"]
            for datatype_name, datatype_meta
            in path_settings.DATAMETA.items()
        })

        self.filename_formats = utils.DotDict({
            datatype_name: datatype_meta["name_format"]
            for datatype_name, datatype_meta
            in path_settings.DATAMETA.items()
        })

        # for each datatype, load all the folders under this datatype
        self.versions = utils.DotDict({
            data_type: self._get_subdirectory_list(sub_path = path)
            for data_type, path
            in self.paths.items()
        })

        # additional metadata
        self._generate_meta()

    def _get_subdirectory_list(self, sub_path):
        """
        helper functions for self._generate_meta, get all the folders under a sub path
        args:
            sub_path string, a sub path under self.root

        return:
            list[str], a list with all 1 level children under sub_path
        """
        return next(os.walk(os.path.join(self.root, sub_path)))[1]

    def _generate_meta(self):
        """
        get the metadata of DataManager, including the versions of all data
        """
        pass

    def deploy(self):
        """
        create all the folders for registered data type
        """
        for data_type, path in self.paths.items():
            try:
                os.makedirs(os.path.join(self.root, path), exist_ok = False)
            except FileExistsError:
                print(f"folder for data type {data_type} exists")

    def _create_version(self, data_type, version_name):
        """
        base method for all folder building
        """
        path = os.path.join(self.root, self.paths[data_type], version_name)
        try:
            os.makedirs(path, exist_ok = False)
            self.versions[data_type].append(version_name)
            print(f"{data_type[:-1].replace('_', ' ')} version {version_name} created")
        except FileExistsError:
            print(f"folder for data type {data_type} exists")
