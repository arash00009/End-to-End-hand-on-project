# HiveBox

Ett REST-API som hämtar sensordata (temperatur m.m.) från openSenseMap
och gör den användbar för biodlare.

## Status
- [x] Fas 1: Kickoff & förberedelse
- [x] Fas 2: Grundkod & Docker
- [ ] Fas 3: API-endpoints & CI
- [x] Fas 4: Kubernetes & metrics
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

## Köra i Kubernetes (lokalt via Kind)

```bash
kind create cluster --name hivebox --config k8s/kind-config.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
docker build -t hivebox:v0.2.0 .
kind load docker-image hivebox:v0.2.0 --name hivebox
kubectl apply -f k8s/deployment.yaml
```

Appen nås sedan på `http://localhost:8080` (port 80 mappas till 8080 i Kind-konfigurationen för att undvika portkonflikter lokalt).

## Metrics

Appen exponerar Prometheus-metrics på `/metrics`, inklusive standardmått för HTTP-requests, svarstider och Python-processinfo.
