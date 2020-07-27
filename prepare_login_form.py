from typing import Set, Dict, Union

from signum import captcha, util
import pkgutil

from signum.state import StateEncryptor

site_packages_path: str = next(filter(lambda m: m.name == 'signum', pkgutil.iter_modules())).module_finder.path


def prepare_login_form(state_encryptor: StateEncryptor) -> object:
    # TODO: if captch is not needed from config, skip it

    captcha_url: str
    captcha_solution: Set[str]

    captcha_url, captcha_solutions = captcha.generate_captcha_challenge(site_packages_path + "/captcha-images")
    # TODO: get all numbers from from config
    csrf_token = util.generate_random_base_64(20)
    hashcash_server_string = util.generate_random_base_64(20)

    state = {
        "captcha_solutions": captcha_solutions,
        "csrf_token": csrf_token,
        "hashcash": {
            "server_string": hashcash_server_string,
            "zero_count": 30
        }
    }
    # TODO: add timestamp, ip

    login_details: Dict[str, Union[str, Set[str]]] = {
        "captcha": captcha_url,
        "server-instructions": f"""{{
            "captcha": {{
                "require": true
            }},
            "hashcash": {{
                "require": true,
                "zeroCount": 15,
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
