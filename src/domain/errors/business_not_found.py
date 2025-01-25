from src.domain.errors.core_error import CoreError


class BusinessNotFoundError(CoreError):
    def __init__(self, business_id: str):
        super().__init__(
            f"Business with id {business_id} was not found",
            404,
            f"Business with id {business_id} was not found",
        )
