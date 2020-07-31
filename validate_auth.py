from typing import Tuple, Dict, List, Union

from flask import request
from signum import util
from signum.authentication_validator import AuthenticationValidator
from signum.password_repository import PasswordRepository
from signum.state import StateEncryptor


def extract_request_details(req: request) -> Tuple[Dict[str, str], Dict[str, str]]:
    return {
               "referrer": req.referrer,
               "host": req.host,
               "remote_addr": req.remote_addr,
               "body": req.data.decode("utf-8")
           }, req.headers


def validate_signup(request_details: Dict[str, str], headers: Dict[str, str], state_encryptor: StateEncryptor,
                    password_database: PasswordRepository, configuration: Dict[str, Union[str, List[str]]]) -> \
        Tuple[bool, object]:
    try:
        auth_validation, details = AuthenticationValidator.validate(request_details=request_details, headers=headers,
                                                                    state_encryptor=state_encryptor,
                                                                    configuration=configuration)

        if not auth_validation:
            return auth_validation, details

        username = headers.get("X-Username")
        password = headers.get("X-hashed-Passtext")

        try:
            password_database.save_password(username=username, password=password)
        except ValueError as e:
            return failure("username-password", str(e))

        return True, {
            "visible_response": {
                "passed": True,
                "session_key": util.generate_random_base_64(40)
            }
        }

    except Exception as e:
        print(e)
        return failure("General", str(e))


def validate_login(request_details: Dict[str, str], headers: Dict[str, str], state_encryptor: StateEncryptor,
                   password_database: PasswordRepository, configuration: Dict[str, Union[str, List[str]]]) -> \
        Tuple[bool, object]:
    try:
        auth_validation, details = AuthenticationValidator.validate(request_details=request_details, headers=headers,
                                                                    state_encryptor=state_encryptor,
                                                                    configuration=configuration)

        if not auth_validation:
            return auth_validation, details

        username = headers.get("X-Username")
        password = headers.get("X-hashed-Passtext")

        passed, reason = password_database.validate_password(username=username, password=password)

        if not passed:
            return failure("username-password", reason)

        return True, {
            "visible_response": {
                "passed": True,
                "session_key": util.generate_random_base_64(40)
            }
        }

    except Exception as e:
        print(e)
        return failure("General", str(e))


def failure(failure_stage: str, failure_reason: str):
    return False, {
        "visible_response": {
            "passed": False,
        },
        "security_details": {
            "failure_stage": failure_stage,
            "failure_reason": failure_reason
        }
    }
