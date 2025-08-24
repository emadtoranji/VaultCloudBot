import random
import string


def generate_random_string(
        length=8,
        include_digits=True,
        include_lower=True,
        include_upper=True,
        include_special=False,
        prefix=""
):
    """
    Create random string, numbers, password, IDs
    'prefix' will add a custom string at the beginning of the final string
    """

    chars = ""
    if include_digits:
        chars += string.digits
    if include_lower:
        chars += string.ascii_lowercase
    if include_upper:
        chars += string.ascii_uppercase
    if include_special:
        chars += string.punctuation

    if not chars:
        chars += string.ascii_lowercase

    final_length = max(0, length - len(prefix))
    random_part = ''.join(random.choice(chars) for _ in range(final_length))
    return prefix + random_part
