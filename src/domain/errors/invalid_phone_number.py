from src.domain.errors.core_error import CoreError


class InvalidPhoneNumberError(CoreError):
    def __init__(self, phone_number: str):
        super().__init__(
            f"Invalid phone number: {phone_number} must have 12 digits",
            400,
            f"Invalid phone number: {phone_number} must have 12 digits",
        )
