from __future__ import annotations

import os
from functools import lru_cache

from pymongo import ASCENDING, MongoClient
from pymongo.collection import ReturnDocument
from pymongo.errors import ConfigurationError

_PLACEHOLDERS = frozenset({"", "CHANGE_ME", "replace-me"})
_indexed = False


def using_mongo() -> bool:
    return bool(_uri())


def _uri() -> str:
    value = os.getenv("MONGO_URI", "").strip()
    return "" if value in _PLACEHOLDERS else value


@lru_cache(maxsize=1)
def client() -> MongoClient:
    return MongoClient(
        _uri(),
        maxPoolSize=8,
        serverSelectionTimeoutMS=8000,
        retryWrites=True,
    )


def database():
    try:
        return client().get_default_database()
    except ConfigurationError:
        return client()["manusmriti"]


def next_id(name: str) -> int:
    doc = database()["counters"].find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(doc["seq"])


def files():
    collection = database()["upload_files"]
    _ensure_indexes(collection)
    return collection


def _ensure_indexes(collection) -> None:
    global _indexed
    if _indexed:
        return
    collection.create_index([("id", ASCENDING)], unique=True)
    collection.create_index([("stored_name", ASCENDING)], unique=True)
    _indexed = True
