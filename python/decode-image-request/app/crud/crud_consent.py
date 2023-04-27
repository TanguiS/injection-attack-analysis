from typing import List, Optional
import uuid, json

from datetime import datetime, timezone
from aioredis import Redis
from sqlalchemy import false

from app.core.config import settings
from app import schemas
from app.schemas.consent import Consent


async def create_consent(
    redis: Redis, tenant_id: uuid.UUID, group_id: uuid.UUID, consent: schemas.Consent
) -> schemas.Consent:
    res: bool = False
    consent_info_str: str = json.dumps(consent.dict(), default=str)

    # nx=True makes sure the key is unique
    res = await redis.set(
        name=f"consent:{tenant_id}:{group_id}:{consent.id}",
        value=consent_info_str,
        nx=True,
        ex=settings.redis_consent_exp_sec,
    )

    if res:
        return consent
    else:
        return None


async def get_consent(
    redis: Redis, tenant_id: uuid.UUID, group_id: uuid.UUID, consent_id: uuid.UUID
) -> schemas.Consent:
    consent = await redis.get(name=f"consent:{tenant_id}:{group_id}:{consent_id}")
    if not consent:
        return None

    consent = json.loads(consent)

    return schemas.Consent.parse_obj(consent)


async def delete_consent(
    redis: Redis, tenant_id: uuid.UUID, group_id: uuid.UUID, consent_id: uuid.UUID
) -> schemas.Consent:
    key = f"consent:{tenant_id}:{group_id}:{consent_id}"
    value = await redis.get(name=f"consent:{tenant_id}:{group_id}:{consent_id}")
    res = await redis.delete(key)

    if res > 0:
        return schemas.Consent.parse_obj(json.loads(value))
    else:
        return None


async def get_consents(
    redis: Redis, tenant_id: uuid.UUID, group_id: uuid.UUID
) -> List[schemas.Consent]:
    key = f"consent:{tenant_id}:{group_id}"

    # Look for all consents in a group
    consents_keys = await redis.keys(pattern=f"{key}:*")
    if not consents_keys:
        return None

    # Get all the json values for each consent
    consents = await redis.mget(consents_keys)

    consentList = []

    # Format the data properly
    for consent in consents:
        consentList.append(schemas.Consent.parse_obj(json.loads(consent)))

    return consentList


async def delete_consents(
    redis: Redis, tenant_id: uuid.UUID, group_id: uuid.UUID
) -> List[schemas.Consent]:
    key = f"consent:{tenant_id}:{group_id}"

    # Look for all consents in a group
    consents_keys = await redis.keys(pattern=f"{key}:*")

    if len(consents_keys) > 0:
        consents = await redis.mget(consents_keys)

        consentList = []

        # Format the data properly
        for consent in consents:
            consentList.append(schemas.Consent.parse_obj(json.loads(consent)))

        # Returns number of deleted items
        res = await redis.delete(*consents_keys)
        if res > 0:
            return consentList
        else:
            return None
    else:
        return None
