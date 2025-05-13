import json
import os
from json import JSONDecodeError


def read_config(path: str= "config.json") -> dict:
    try:
        with open(path, "r") as f:
            data = json.loads(f.read())
    except FileNotFoundError as e:
        print(f"Config file not found: {e}")
        return {}
    except JSONDecodeError as e:
        print(f"Json wrongly formatted: {e}")
        return {}
    else:
        return data


config = read_config()
config['database']['database_config']['password'] = os.environ['dbeaver_pass']