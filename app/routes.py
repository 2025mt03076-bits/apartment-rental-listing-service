import re
from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query
from pymongo import ReturnDocument

from app import database
from app.models import (
    ListingCreate,
    ListingOut,
    ListingPage,
    ListingStatus,
    ListingUpdate,
    StatusUpdate,
)

router = APIRouter(prefix="/listings", tags=["listings"])


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _object_id(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise HTTPException(status_code=400, detail=f"Invalid listing id: {value}")
    return ObjectId(value)


def _serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


# Command: createListing
@router.post("", response_model=ListingOut, status_code=201)
async def create_listing(payload: ListingCreate):
    doc = payload.model_dump()
    doc.update(status=ListingStatus.AVAILABLE.value, created_at=_now(), updated_at=_now())
    result = await database.get_db().listings.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


# Query: searchListings
@router.get("", response_model=ListingPage)
async def search_listings(
    city: Optional[str] = None,
    min_rent: Optional[float] = Query(default=None, ge=0),
    max_rent: Optional[float] = Query(default=None, ge=0),
    bedrooms: Optional[int] = Query(default=None, ge=0),
    owner_id: Optional[str] = None,
    status: ListingStatus = ListingStatus.AVAILABLE,  # only rentable apartments by default
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    query: dict = {"status": status.value}
    if city:
        query["city"] = {"$regex": f"^{re.escape(city)}$", "$options": "i"}
    if bedrooms is not None:
        query["bedrooms"] = bedrooms
    if owner_id:
        query["owner_id"] = owner_id
    if min_rent is not None or max_rent is not None:
        query["rent"] = {}
        if min_rent is not None:
            query["rent"]["$gte"] = min_rent
        if max_rent is not None:
            query["rent"]["$lte"] = max_rent

    col = database.get_db().listings
    total = await col.count_documents(query)
    cursor = col.find(query).sort("created_at", -1).skip((page - 1) * limit).limit(limit)
    items = [_serialize(doc) async for doc in cursor]
    return {"page": page, "limit": limit, "total": total, "items": items}


# Query: getListingDetails
@router.get("/{listing_id}", response_model=ListingOut)
async def get_listing(listing_id: str):
    doc = await database.get_db().listings.find_one({"_id": _object_id(listing_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Listing not found")
    return _serialize(doc)


# Command: updateListing
@router.put("/{listing_id}", response_model=ListingOut)
async def update_listing(listing_id: str, payload: ListingUpdate):
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No fields to update")
    changes["updated_at"] = _now()
    doc = await database.get_db().listings.find_one_and_update(
        {"_id": _object_id(listing_id)},
        {"$set": changes},
        return_document=ReturnDocument.AFTER,
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Listing not found")
    return _serialize(doc)


# Command: change availability (used by owners and by the Booking Service)
@router.patch("/{listing_id}/status", response_model=ListingOut)
async def update_status(listing_id: str, payload: StatusUpdate):
    doc = await database.get_db().listings.find_one_and_update(
        {"_id": _object_id(listing_id)},
        {"$set": {"status": payload.status.value, "updated_at": _now()}},
        return_document=ReturnDocument.AFTER,
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Listing not found")
    return _serialize(doc)
