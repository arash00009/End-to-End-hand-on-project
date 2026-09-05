# HiveBox

Ett REST-API som hämtar sensordata (temperatur m.m.) från openSenseMap
och gör den användbar för biodlare.

## Status
- [x] Fas 1: Kickoff & förberedelse
- [x] Fas 2: Grundkod & Docker
- [x] Fas 3: API-endpoints & CI
- [x] Fas 4: Kubernetes & metrics
- [x] Fas 5: Cache, storage & Helm
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
docker build -t hivebox:v0.2.0 .
docker run --rm -p 5000:5000 hivebox:v0.2.0
```

Båda ska skriva ut den aktuella versionen, t.ex. `v0.2.0`.

## API-endpoints

### GET /version
Returnerar den aktuella versionen av applikationen.

**Exempel:**
```bash
curl http://localhost:5000/version
```
```json
{"version": "v0.2.0"}
```

### GET /temperature
Returnerar medeltemperaturen från 3 senseBoxar (openSenseMap), baserat på mätningar som är max 1 timme gamla.

**Exempel:**
```bash
curl http://localhost:5000/temperature
```
```json
{"temperature": 15.12, "unit": "celsius", "status": "Good", "sensors_used": 3}
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

## Cache och Storage

Appen använder Valkey (Redis-kompatibel) för cachning av temperaturdata i 5 minuter, och MinIO (S3-kompatibel) för att spara periodiska kopior av datan.

### Nya endpoints
- `GET /cache` — tvingar fram en cache-uppdatering direkt
- `GET /store` — sparar en kopia av senaste datan till MinIO
- `GET /readyz` — readiness-check, verifierar att senseBoxar är nåbara

## Installera med Helm

```bash
helm install hivebox hivebox-chart/
```

Konfigurerbara värden finns i `hivebox-chart/values.yaml` (image-tag, antal repliker, miljövariabler för Valkey/MinIO m.m.).

Avinstallera:
```bash
helm uninstall hivebox
```
