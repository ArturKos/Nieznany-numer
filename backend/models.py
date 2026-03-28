from pydantic import BaseModel, Field
import re

PHONE_RE = re.compile(r"^\+?\d{7,15}$")


def normalize_phone(number: str) -> str:
    return re.sub(r"[\s\-\(\)]", "", number)


def is_valid_phone(number: str) -> bool:
    return bool(PHONE_RE.match(number))


class RatingRequest(BaseModel):
    rating: str = Field(pattern=r"^(negative|neutral|positive)$")


class CommentRequest(BaseModel):
    text: str = Field(min_length=3, max_length=1000)
