from datetime import datetime
from typing import Set, Dict, Union, List

from signum import captcha, util
import pkgutil

from signum.state import StateEncryptor

site_packages_path: str = next(filter(lambda m: m.name == 'signum', pkgutil.iter_modules())).module_finder.path


def prepare_login_form(state_encryptor: StateEncryptor, configuration: Dict[str, Union[str, List[str]]]) -> object:
    captcha_url: str
    captcha_solution: Set[str]

    captcha_url, captcha_solutions = captcha.generate_captcha_challenge(site_packages_path + "/captcha-images")

    csrf_token = util.generate_random_base_64(configuration["csrf_token_length"])
    hashcash_server_string = util.generate_random_base_64(configuration["hashcash_server_string_length"])

    state = {
        "server_time": datetime.utcnow().strftime("%Y%m%d-%H%M%S"),
        "captcha_solutions": captcha_solutions,
        "csrf_token": csrf_token,
        "hashcash": {
            "server_string": hashcash_server_string,
            "zero_count": configuration["hashcash_zero_count"]
        }
    }

    login_details: Dict[str, Union[str, Set[str]]] = {
        "captcha": captcha_url,
        "server-instructions": f"""{{
            "captcha": {{
                "require": true
            }},
            "hashcash": {{
                "require": true,
                "zeroCount": "{configuration["hashcash_zero_count"]}",
                "serverString": "{hashcash_server_string}"
            }},
            "csrfToken": {{
                "require": true
            }},
            "tolerance": {{
                "minimumAlphabetPassphrase": 20
            }},
            "hashing": {{
                saltHashByUsername: true,
                hashCycles: 3,
                resultLength: 20
            }}
        }}""",
        "state": state_encryptor.encrypt_state(state),
        "csrfToken": csrf_token,
        "passtextStrength": f"""{{
            "minimumCharactersPassword": 8
        }}""",
        "tolerance": f"""{{
            "minimumAlphabetPassphrase": 20
        }}"""
    }

    return login_details
