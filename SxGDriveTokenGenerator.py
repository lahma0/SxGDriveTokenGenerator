#! /usr/bin/python3

# Requirements:
#   Python 3.7+
#   Python Packages:
#       oauth2client
#       google-api-python-client

import json
import os
import shutil
import sys
from pathlib import Path
from httplib2 import Http
from oauth2client import client, service_account, tools, file
from googleapiclient.discovery import build
from googleapiclient import errors

DEFAULT_CONFIG_PATH = "config.json"
DEFAULT_CLIENT_SECRET_PATHS = ["credentials.json", "client_secret*.json"]
DEFAULT_OUTPUT_FOLDER_PATH = "switch/sx/"
DEFAULT_SCOPES = "https://www.googleapis.com/auth/drive.readonly"
DEFAULT_OUTPUT_TOKEN_NAME = "gdrive.token"
DEFAULT_OUTPUT_CLIENT_SECRET_NAME = "credentials.json"


class Config:
    """Class responsible for reading the config file or creating a config file with default 
    values. Once loaded, the following properties are accessible: 
        client_secret_paths,
        output_folder_path,
        scopes,
        output_token_json_name,
        output_client_secret_json_name"""

    CLIENT_SECRET_JSON_PATHS_KEY = 'client_secret_json_paths'
    OUTPUT_FOLDER_PATH_KEY = 'output_folder_path'
    SCOPES_KEY = 'scopes'
    OUTPUT_TOKEN_JSON_NAME_KEY = 'output_token_json_name'
    OUTPUT_CLIENT_SECRET_JSON_NAME_KEY = 'output_client_secret_json_name'

    def __init__(self, config_dict=None):
        self.config_dict = config_dict

    @staticmethod
    def create_load_default_config(config_path='config.json'):
        """Creates a config file with default values and returns 
        a new Config instance using those default values"""
        config = Config()
        config_dict = config.create_config_dict()
        with open(config_path, "w") as config_file:
            json.dump(config_dict, config_file, indent=4)

        return config

    @staticmethod
    def load_config(config_path='config.json'):
        """Creates a new Config instance with data loaded from a config file"""
        return Config(Config.__read_config(config_path))

    @staticmethod
    def __read_config(config_path='config.json'):
        '''Reads config data from a file and returns JSON data as a dict'''
        with open(config_path) as config_file:
            return json.load(config_file, object_hook=Config.remove_json_comments)

    @staticmethod
    def remove_json_comments(d):
        return {k: v for k, v in d.items() if "__comments__" not in k}

    @property
    def client_secret_json_paths(self):
        if not getattr(self, '__client_secret_json_paths', None):
            self.__client_secret_json_paths = DEFAULT_CLIENT_SECRET_PATHS
            if dkv_valid(self.config_dict, Config.CLIENT_SECRET_JSON_PATHS_KEY):
                self.__client_secret_paths = self.config_dict[Config.CLIENT_SECRET_JSON_PATHS_KEY]

        return self.__client_secret_json_paths

    @property
    def output_folder_path(self):
        if not getattr(self, '__output_folder_path', None):
            self.__output_folder_path = DEFAULT_OUTPUT_FOLDER_PATH
            if dkv_valid(self.config_dict, Config.OUTPUT_FOLDER_PATH_KEY):
                self.__output_folder_path = self.config_dict[Config.OUTPUT_FOLDER_PATH_KEY]

        return self.__output_folder_path

    @property
    def scopes(self):
        if not getattr(self, '__scopes', None):
            self.__scopes = DEFAULT_SCOPES
            if dkv_valid(self.config_dict, Config.SCOPES_KEY):
                self.__scopes = self.config_dict[Config.SCOPES_KEY]

        return self.__scopes

    @property
    def output_token_json_name(self):
        if not getattr(self, '__output_token_json_name', None):
            self.__output_token_json_name = DEFAULT_OUTPUT_TOKEN_NAME
            if dkv_valid(self.config_dict, Config.OUTPUT_TOKEN_JSON_NAME_KEY):
                self.__output_token_json_name = self.config_dict[Config.OUTPUT_TOKEN_JSON_NAME_KEY]

        return self.__output_token_json_name

    @property
    def output_client_secret_json_name(self):
        if not getattr(self, '__output_client_secret_json_name', None):
            self.__output_client_secret_json_name = DEFAULT_OUTPUT_CLIENT_SECRET_NAME
            if dkv_valid(self.config_dict, Config.OUTPUT_CLIENT_SECRET_JSON_NAME_KEY):
                self.__output_client_secret_json_name = self.config_dict[
                    Config.OUTPUT_CLIENT_SECRET_JSON_NAME_KEY]

        return self.__output_client_secret_json_name

    def create_config_dict(self):
        """Creates a dictionary using the Config instance's property values"""
        return {
            Config.CLIENT_SECRET_JSON_PATHS_KEY: self.client_secret_json_paths,
            Config.OUTPUT_FOLDER_PATH_KEY: self.output_folder_path,
            Config.SCOPES_KEY: self.scopes,
            Config.OUTPUT_TOKEN_JSON_NAME_KEY: self.output_token_json_name,
            Config.OUTPUT_CLIENT_SECRET_JSON_NAME_KEY: self.output_client_secret_json_name
        }

    def create_output_folder_path(self):
        """Creates 'output_folder_path' directories if they do not already exist"""
        path = Path(self.output_folder_path)
        if not path.exists():
            os.makedirs(self.output_folder_path, exist_ok=True)

    def find_client_secret_path(self):
        """Finds the 1st matching file in 'client_secret_json_paths'"""
        search_paths = []
        if isinstance(self.client_secret_json_paths, list):
            search_paths.extend(self.client_secret_json_paths)
        elif isinstance(self.client_secret_json_paths, str):
            search_paths.append(self.client_secret_json_paths)

        for p in search_paths:
            path = Path(p)
            path_list = list(path.parent.glob(path.name))
            if path_list:
                return str(path_list[0])

        raise RuntimeError("No valid 'client_secret' ('credentials') JSON found!")

    def get_output_token_json_path(self):
        """Appends 'output_token_json_name' to 'output_folder_path'"""
        return str(Path(self.output_folder_path) / self.output_token_json_name)

    def get_output_client_secret_json_path(self):
        """Appends 'output_client_secret_json_name' to 'output_folder_path'"""
        return str(Path(self.output_folder_path) / self.output_client_secret_json_name)


def dkv_valid(d, keyname):
    """Checks if the dict, key, and value exist and are valid. Returns True if 'd' exists, it 
    has a key named 'keyname', and that key's value does not evaluate to False or None"""
    return (d and (keyname in d) and d[keyname])


def get_file_directory(append_to_path=""):
    """Return an absolute path to the current file directory"""
    return str(Path(__file__).absolute().parent / append_to_path)


def create_empty_file(path):
    """Creates an empty file at the provided path"""
    Path(path).touch()


def do_auth(token_path=None, client_secret_path=None, scopes=None):
    """Generates a Google OAuth token file using the provided credentials"""
    store = file.Storage(token_path)
    creds = store.get()

    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(client_secret_path, scopes)
        creds = tools.run_flow(flow, store)

    return build('drive', 'v3', http=creds.authorize(Http()))


def main():
    config_path = DEFAULT_CONFIG_PATH
    if sys.argv and len(sys.argv) > 1 and sys.argv[1]:
        config_path = sys.argv[1]
        print(f"Loading config file from user-supplied path: '{config_path}'")
    else:
        print(f"Loading config file from default path: '{config_path}'")

    try:
        config = Config.load_config(config_path)
    except FileNotFoundError:
        print(f"No config file found. Creating default config file at '{config_path}'")
        config = Config.create_load_default_config(config_path)

    input("""\nYour web browser will now open to a Google OAuth verification webpage. Ensure you 
are logged into the Google Account you used to create your OAuth credentials file and complete 
the verification process. If you see the warning, 'This app isn't verified', click 'Advanced' 
> 'Go to {Project Name} (unsafe)'. Once you complete the verification procedure you will be 
returned to the app. Press [Enter] to continue to the verification page.\n""")

    try:
        print("Creating output folder")
        config.create_output_folder_path()

        print("Locating client secret file")
        client_secret_path = config.find_client_secret_path()

        # Create an empty token file so oath2client doesn't print a warning on console
        create_empty_file(config.get_output_token_json_path())

        print("Performing authentication")
        do_auth(config.get_output_token_json_path(), client_secret_path, config.scopes)

        print("Copying client secret JSON to output directory")
        shutil.copyfile(client_secret_path, config.get_output_client_secret_json_path())

        input(f"\nProcess complete! Copy (2) files from " +
              f"'{str(Path(config.output_folder_path).absolute())}' to your Switch SD card " +
              f"folder '/switch/sx/'. Press [Enter] to close this window.")

    except shutil.Error as shutil_ex:
        print(f"An error occurred while copying the client secret file to the output " +
              f"directory: {shutil_ex}")
    except Exception as ex:
        print(f"An error occurred while generating your token: {ex}")

    # If token file is still empty, something went wrong. Delete it so we don't confuse
    # user into thinking a valid token file was generated.
    token_path = Path(config.get_output_token_json_path())
    if token_path.exists() and token_path.stat().st_size <= 0:
        token_path.unlink()


if __name__ == '__main__':
    main()
