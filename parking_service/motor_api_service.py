import os
import requests


def get_response(registration_number):
    url = "https://v1.motorapi.dk/vehicles"

    headers = {
        "X-AUTH-TOKEN": os.environ["MOTOR_API_SERVICE"],
    }
    params = {"registration_number": registration_number}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"An error occured: {e}")
        return None

    return response


def get_info(registration_number):
    r = get_response(registration_number)
    if r is not None:
        return {
            "make": r.json()[0]["make"],
            "model": r.json()[0]["model"],
            "variant": r.json()[0]["variant"],
        }


if __name__ == "__main__":
    registration_numbers = [
        "DM24392",
        "CZ48785",
        "BR92382",
        "AZ39331",
        "CK82292",
        "CP43099",
        "DA35743",
    ]
    for i in registration_numbers:
        info = get_info(i)
        if info is not None:
            print(
                f"make: {info['make']}, model: {info['model']}, \
variant: {info['variant']}"
            )
