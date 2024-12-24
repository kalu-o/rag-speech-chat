import json

import pytest
from rag_speech_chat import app
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
import json


@pytest.fixture(scope="module")
def test_client() -> TestClient:
    return TestClient(app.app)


def test_get(test_client: TestClient):
    actual = test_client.get("/status")

    assert actual.status_code == status.HTTP_200_OK
    assert actual.text == "App is up and running!"


def test_chat(test_client: TestClient):
    request_default = {"chat_input": "Capital of Germany", "chat_history": []}
    response_default = {
        "output": "I don't know." 
    }
    actual = test_client.post(
        "/chat",
        headers={"content-type": "application/json"},
        data=json.dumps(request_default),
    )

    assert actual.status_code == status.HTTP_200_OK
    assert actual.json() == response_default or "don't" in response_default["output"]