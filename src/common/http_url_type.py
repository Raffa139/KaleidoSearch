from pydantic import HttpUrl
from sqlalchemy.types import TypeDecorator, String


class HttpUrlType(TypeDecorator):
    impl = String(2000)
    cache_ok = True
    python_type = HttpUrl

    def process_bind_param(self, value: HttpUrl, dialect) -> str | None:
        return str(value) if value is not None else None

    def process_result_value(self, value: str | None, dialect) -> HttpUrl | None:
        try:
            return HttpUrl(url=value) if value is not None else None
        except ValueError:
            return None

    def process_literal_param(self, value: HttpUrl, dialect) -> str:
        return str(value) if value is not None else None
