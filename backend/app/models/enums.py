from enum import StrEnum


class UserRole(StrEnum):
    CUSTOMER = "CUSTOMER"
    SELLER = "SELLER"
    ADMIN = "ADMIN"


class LotStatus(StrEnum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    TAKEN = "TAKEN"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class LotCategory(StrEnum):
    OUTERWEAR = "OUTERWEAR"
    TOPS = "TOPS"
    BOTTOMS = "BOTTOMS"
    FOOTWEAR = "FOOTWEAR"
    ACCESSORIES = "ACCESSORIES"


class OrderStatus(StrEnum):
    PAID = "PAID"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"
