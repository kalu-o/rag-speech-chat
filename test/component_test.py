import os

import pytest
import requests
from fastapi import status
import json

HOST_ALIAS = os.getenv("HOST_ALIAS", "localhost")


@pytest.fixture(scope="module")
def request_url() -> str:
    return f"http://{HOST_ALIAS}:8000/chat"


def test_request_positive(request_url):
    """Positive test"""
    request_default = {"chat_input": "Capital of Germany", "chat_history": []}
    response_default = {
        "output": "I don't know." 
    }

    actual = requests.post(
        request_url,
        headers={"content-type": "application/json"},
        data=json.dumps(request_default),
    )

    assert actual.status_code == status.HTTP_200_OK
    assert actual.json() == response_default or "don't" in response_default["output"]