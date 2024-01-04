class TagAlreadyExist(ValueError):
    ...


class IncorrectUsernameOrPassword(Exception):
    detail = "Incorrect username or password"
