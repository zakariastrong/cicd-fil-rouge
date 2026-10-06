from app import settings


def test_list_is_empty_at_start(client):
    assert client.get("/tasks").json() == []


def test_create_task(client):
    response = client.post("/tasks", json={"title": "Préparer le cours"})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "title": "Préparer le cours", "done": False}


def test_create_task_rejects_empty_title(client):
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422


def test_get_unknown_task_returns_404(client):
    assert client.get("/tasks/42").status_code == 404


def test_complete_task(client):
    client.post("/tasks", json={"title": "Corriger les labs"})
    response = client.patch("/tasks/1/done")
    assert response.status_code == 200
    assert response.json()["done"] is True


def test_search_tasks(client):
    client.post("/tasks", json={"title": "Acheter du café"})
    client.post("/tasks", json={"title": "Réviser Git"})
    titles = [t["title"] for t in client.get("/tasks/search", params={"q": "Git"}).json()]
    assert titles == ["Réviser Git"]


def test_delete_requires_token(client):
    client.post("/tasks", json={"title": "À supprimer"})
    assert client.delete("/tasks/1").status_code == 403


def test_delete_with_token(client, monkeypatch):
    monkeypatch.setattr(settings, "API_TOKEN", "jeton-de-test")
    client.post("/tasks", json={"title": "À supprimer"})
    response = client.delete("/tasks/1", headers={"X-API-Token": "jeton-de-test"})
    assert response.status_code == 204
    assert client.get("/tasks/1").status_code == 404
