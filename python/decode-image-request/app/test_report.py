import uuid
import pytest
import json
import aioredis
import requests

from fastapi import status
from httpx import AsyncClient
from datetime import datetime, timezone

import app.schemas as consents
import app.crud.crud_consent as crud
from app.main import app
from app.core.config import settings
from app.routers.consents import get_redis


base_url = "http://localhost:9090"

class TestStatus:
    def test_get_status(self):
        api_path = "/"
        res = requests.get(url=base_url+api_path)
        status_code = res.status_code
        assert status_code == 200


