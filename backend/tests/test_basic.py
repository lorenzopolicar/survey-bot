import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0].parent))

from httpx import AsyncClient, ASGITransport
from app.main import app
import app.scoring as scoring

transport = ASGITransport(app=app)
client = AsyncClient(transport=transport, base_url="http://test")


import pytest


@pytest.mark.asyncio
async def test_create_question(monkeypatch):
    monkeypatch.setattr(scoring, 'score_answer', lambda *args, **kwargs: 5)
    resp = await client.post('/questions', json={'text': 'What is your name?'} )
    assert resp.status_code == 200
    data = resp.json()
    assert data['text'] == 'What is your name?'
