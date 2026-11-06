from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ListingStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RENTED = "RENTED"
    INACTIVE = "INACTIVE"


class ListingCreate(BaseModel):
    title: str = Field(min_length=1)
    description: Optional[str] = None
    city: str = Field(min_length=1)
    rent: float = Field(ge=0)
    bedrooms: int = Field(ge=0)
    owner_id: str = Field(min_length=1)


class ListingUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    city: Optional[str] = Field(default=None, min_length=1)
    rent: Optional[float] = Field(default=None, ge=0)
    bedrooms: Optional[int] = Field(default=None, ge=0)


class StatusUpdate(BaseModel):
    status: ListingStatus


class ListingOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    city: str
    rent: float
    bedrooms: int
    owner_id: str
    status: ListingStatus
    created_at: datetime
    updated_at: datetime


class ListingPage(BaseModel):
    page: int
    limit: int
    total: int
    items: List[ListingOut]
