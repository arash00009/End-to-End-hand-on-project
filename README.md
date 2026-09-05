# HiveBox

Ett REST-API som hämtar sensordata (temperatur m.m.) från openSenseMap
och gör den användbar för biodlare.

## Status
- [x] Fas 1: Kickoff & förberedelse
- [x] Fas 2: Grundkod & Docker
- [x] Fas 3: API-endpoints & CI
- [ ] Fas 4: Kubernetes & metrics
- [ ] Fas 5: Cache, storage & Helm
- [ ] Fas 6: GitOps & optimering
- [ ] Fas 7: Capstone

## Tech stack
Python (Flask), Docker, Kubernetes, GitHub Actions

## Köra applikationen

### Lokalt
```bash
python3 app.py
```

### Med Docker
```bash
docker build -t hivebox:v0.0.1 .
docker run --rm hivebox:v0.0.1
```

Båda ska skriva ut den aktuella versionen, t.ex. `v0.0.1`.

## API-endpoints

### GET /version
Returnerar den aktuella versionen av applikationen.

**Exempel:**
```bash
curl http://localhost:5000/version
```
```json
{"version": "v0.1.0"}
```

### GET /temperature
Returnerar medeltemperaturen från 3 senseBoxar (openSenseMap), baserat på mätningar som är max 1 timme gamla.

**Exempel:**
```bash
curl http://localhost:5000/temperature
```
```json
{"temperature": 15.12, "unit": "celsius", "sensors_used": 3}
```

Om ingen färsk data finns tillgänglig returneras statuskod 503 med ett felmeddelande.

## Tester

```bash
pip install -r requirements.txt
pytest -v
```

## Linting

```bash
flake8 app.py test_app.py --max-line-length=100
```
