import datetime
import json
from typing import Tuple, Dict, List

from flask import request
from signum import util
from signum.password_repository import PasswordRepository
from signum.state import StateEncryptor


def extract_request_details(req: request) -> Tuple[Dict[str, str], Dict[str, str]]:
    return {
        "referrer": req.referrer,
        "host": req.host,
        "remote_addr": req.remote_addr,
        "body": req.data.decode("utf-8")
    }, req.headers


# TODO: move, of course, to python library
# TODO: need to know policy! not all should be validated
def validate_signup(request_details: Dict[str, str], headers: Dict[str, str], state_encryptor: StateEncryptor,
                    password_database: PasswordRepository, self_ip_addresses: List[str]) -> \
        Tuple[bool, object]:
    try:
        auth_validation, details = validate_auth(request_details=request_details, headers=headers,
                                                 state_encryptor=state_encryptor, password_database=password_database,
                                                 self_ip_addresses=self_ip_addresses)

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
                   password_database: PasswordRepository, self_ip_addresses: List[str]) -> \
        Tuple[bool, object]:
    try:
        auth_validation, details = validate_auth(request_details=request_details, headers=headers,
                                                 state_encryptor=state_encryptor, password_database=password_database,
                                                 self_ip_addresses=self_ip_addresses)

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


def validate_auth(request_details: Dict[str, str], headers: Dict[str, str], state_encryptor: StateEncryptor,
                  password_database: PasswordRepository, self_ip_addresses: List[str]) -> \
        Tuple[bool, object]:

    # Concept: fail as fast as possible

    if not request_details["referrer"]:
        return failure("referrer", "not provided")

    acceptable_referrer = 'http://%s/' % request_details["host"]

    if not request_details["referrer"].startswith(acceptable_referrer):
        return failure("referrer", "doesn't match")

    username = headers.get("X-Username")

    if not username:
        return failure("username", "not provided")

    password = headers.get("X-hashed-Passtext")

    if not password:
        return failure("password", "not provided")

    csrf = headers.get("X-Csrf-Token")

    if not csrf:
        return failure("csrf", "not provided")

    captcha = headers.get("X-Captcha")

    if not captcha:
        return failure("captcha", "not provided")

    hashcash = headers.get("X-Hashcash")

    if not hashcash:
        return failure("hashcash", "not provided")

    zeros, timestamp, ip, server_string, _, _ = hashcash.split(":")

    timestamp_object = datetime.datetime.strptime(timestamp, "%Y%m%d-%H%M%S")

    diff_in_seconds = (datetime.datetime.utcnow() - timestamp_object).total_seconds()

    # TODO: use configuration. Same value as the tolerance
    if not 0 < diff_in_seconds <= 120:
        return failure("hashcash", "timestamp doesn't match")

    if request_details["remote_addr"] not in [ip] + self_ip_addresses:
        return failure("hashcash", "ip address doesn't match: "+request_details["remote_addr"])

    if not util.validate_hashcash_zeros(bytes(hashcash, "utf-8"), int(zeros)):
        return failure("hashcash", "zeros not validated")

    data = json.loads(request_details["body"])
    encrypted_state = data["state"]

    try:
        state = state_encryptor.decrypt_state(encrypted_state.encode())
    except ValueError as e:
        return failure("state", str(e))

    if int(zeros) != int(state["hashcash"]["zero_count"]):
        return failure("hashcash", "zeros don't match")

    if server_string != state["hashcash"]["server_string"]:
        return failure("hashcash", "server string doesn't match")

    if csrf != state["csrf_token"]:
        return failure("csrf", "csrf token doesn't match")

    captcha_solutions = set(state["captcha_solutions"])

    if captcha not in captcha_solutions:
        return failure("captcha", f"captcha solution isn't in {captcha_solutions}")

    return True, {
        "visible_response": {
              "passed": True,
              "session_key": util.generate_random_base_64(40)
        }
    }


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
