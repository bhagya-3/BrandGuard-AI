from app.core.security import hash_password, verify_password


def test_password_hashing():
    password = "StrongTestPassword123!"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)


def test_wrong_password_is_rejected():
    hashed = hash_password("CorrectPassword123!")

    assert not verify_password("WrongPassword123!", hashed)


def test_password_hashes_are_not_plain_text():
    password = "StrongTestPassword123!"

    hashed = hash_password(password)

    assert password not in hashed