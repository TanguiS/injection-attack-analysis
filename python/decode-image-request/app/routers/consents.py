from datetime import datetime, timezone
from typing import List
import uuid
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, HTTPException, Request, Depends, status

from app import schemas
from app.crud import crud_consent
from app.core.config import settings

from aioredis import Redis
import aioredis

router = APIRouter(
    prefix="/tenants/{tenant_id}/branches/{branch_id}/consents",
    tags=["consents"],
)


async def get_redis():
    redis_server = aioredis.from_url(settings.get_redis_url(), decode_responses=True)
    try:
        yield await redis_server
    finally:
        await redis_server.close()


@router.post("/", response_model=schemas.Consent, status_code=201)
async def create_consent(
    consent: schemas.Consent,
    tenant_id: uuid.UUID,
    branch_id: uuid.UUID,
    redis: Redis = Depends(get_redis),
):
    print(consent)
    consent.id = uuid.uuid4()
    consent.time_stamp = datetime.now(timezone.utc)
    res = await crud_consent.create_consent(redis, tenant_id, branch_id, consent)

    if not res:
        raise HTTPException(status_code=400, detail="Could not create the new consent")

    return res


@router.get("/{consent_id}", response_model=schemas.Consent)
async def get_consent(
    tenant_id: uuid.UUID,
    branch_id: uuid.UUID,
    consent_id: uuid.UUID,
    redis: Redis = Depends(get_redis),
):
    res = await crud_consent.get_consent(redis, tenant_id, branch_id, consent_id)

    if not res:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return res


@router.delete("/{consent_id}", response_model=schemas.Consent)
async def delete_consent(
    tenant_id: uuid.UUID,
    branch_id: uuid.UUID,
    consent_id: uuid.UUID,
    redis: Redis = Depends(get_redis),
):
    """Basic implementation"""
    deleted = await crud_consent.delete_consent(redis, tenant_id, branch_id, consent_id)

    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return deleted


@router.get(
    "/", response_model=List[schemas.Consent], response_model_exclude_unset=True
)
async def get_consents(
    tenant_id: uuid.UUID, branch_id: uuid.UUID, redis: Redis = Depends(get_redis)
):
    print("Getting consents")
    res = await crud_consent.get_consents(redis, tenant_id, branch_id)
    print(res)
    if not res:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return res


@router.delete("/", response_model=List[schemas.Consent])
async def delete_consents(
    tenant_id: uuid.UUID, branch_id: uuid.UUID, redis: Redis = Depends(get_redis)
):
    """Basic implementation"""
    deleted = await crud_consent.delete_consents(redis, tenant_id, branch_id)

    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    return deleted
