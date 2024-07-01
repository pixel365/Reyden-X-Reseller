from django.contrib.auth.hashers import PBKDF2PasswordHasher


class ExtendedPBKDF2PasswordHasher(PBKDF2PasswordHasher):
    algorithm = "pbkdf2_sha256"
    salt_entropy = 128
    iterations = 260000
