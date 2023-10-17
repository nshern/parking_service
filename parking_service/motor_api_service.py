import os
import requests


def get_info(registration_number):
    url = "https://v1.motorapi.dk/vehicles"

    headers = {
        "X-AUTH-TOKEN": os.environ["MOTOR_API_SERVICE"],
    }
    params = {"registration_number": registration_number}

    response = requests.get(url, headers=headers, params=params)
    return response


if __name__ == "__main__":
    r = get_info("DM24392")
    print(r.status_code)
    print(r.text)
