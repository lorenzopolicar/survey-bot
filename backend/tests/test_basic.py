import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0].parent))

from fastapi.testclient import TestClient
from app.main import app
import app.scoring as scoring

client = TestClient(app)


def test_create_question(monkeypatch):
    monkeypatch.setattr(scoring, 'score_answer', lambda *args, **kwargs: 5)
    resp = client.post('/questions', json={'text': 'What is your name?'} )
    assert resp.status_code == 200
    data = resp.json()
    assert data['text'] == 'What is your name?'
