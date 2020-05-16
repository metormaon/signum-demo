import json
from typing import Tuple

from flask import request, jsonify
from signum import util
from signum.state import StateEncryptor


def validate_login(req: request, state_encryptor: StateEncryptor) -> Tuple[bool, object]:
    try:
        hashcash = req.headers.get("X-Hashcash")

        if not hashcash:
            return failure("hashcash", "not_provided")

        zeros, timestamp, ip, server_string, _, _ = hashcash.split(":")

        if not util.validate_hashcash_zeros(hashcash, int(zeros)):
            return failure("hashcash", "zeros not validated")

        data = json.loads(request.data.decode("utf-8"))
        state = data["state"]

        state = state_encryptor.decrypt_state(state.encode())

    # Host: 127.0.0.1:5000
        # Connection: keep-alive
        # Content-Length: 15
        # X-Hashcash: 15:20200516-184239:82.81.223.44:G5V-uz1mchswi07fqx0QumL8LO0:MS4zMzczODkzNzkyNzY0MDM0ZSszMDc=:MjIwMQ==
        # X-Csrf-Token: _jiAGTtAie0HU3xksfKt9xkwPSk
        # X-Username: a
        # User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36
        # X-Hashed-Passtext: 414370292207eb05cd88
        # Content-Type: application/json;charset=UTF-8
        # Accept: */*
        # Origin: http://127.0.0.1:5000
        # Sec-Fetch-Site: same-origin
        # Sec-Fetch-Mode: cors
        # Sec-Fetch-Dest: empty
        # Referer: http://127.0.0.1:5000/
        # Accept-Encoding: gzip, deflate, br
        # Accept-Language: en-US,en;q=0.9,he;q=0.8,ar;q=0.7,fr;q=0.6
        #
        #  b'[object Object]'



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
