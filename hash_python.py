from hashlib import md5
from datetime import datetime

SALT: str = "gXpM4ur0D3V!"
DEFAULT_ENCODE: str = "utf-8"


def gerarkey() -> str:
    return md5(
        f"""{datetime.now().strftime("%y%m%d%H%M%S%f")}{SALT}""".encode(DEFAULT_ENCODE)
    ).hexdigest()


if __name__ == "__main__":
    print(gerarkey())
