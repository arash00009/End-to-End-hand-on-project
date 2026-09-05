# HiveBox

Ett REST-API som hämtar sensordata (temperatur m.m.) från openSenseMap
och gör den användbar för biodlare.

## Status
- [x] Fas 1: Kickoff & förberedelse
- [x] Fas 2: Grundkod & Docker
- [ ] Fas 3: API-endpoints & CI
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
