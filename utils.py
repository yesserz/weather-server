from werkzeug.security import generate_password_hash, check_password_hash


def check_hash(password, hashed_password):
    """
    Проверяет соответствие пароля хешу.
    """
    return check_password_hash(hashed_password, password)


def generate_hash(password):
    """
    Генерирует хеш для пароля.
    """
    return generate_password_hash(password, method='sha256')
