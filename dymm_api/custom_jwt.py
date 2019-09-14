from .patterns import ErrorPattern
from .errors import forbidden

_e = ErrorPattern()


def customize_jwt(jwt):
    @jwt.invalid_token_loader
    def custom_invalid_token_loader():
        return forbidden(_e.TOKEN_INVALID)

    @jwt.expired_token_loader
    def custom_expired_token_callback():
        return forbidden(_e.TOKEN_EXPR)

    @jwt.needs_fresh_token_loader
    def custom_needs_fresh_token_loader():
        return forbidden(_e.TOKEN_NEED_FRESH)
