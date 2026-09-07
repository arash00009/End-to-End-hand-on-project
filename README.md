# 🐝 HiveBox

Ett end-to-end DevOps-projekt: ett REST-API som hämtar sensordata (temperatur m.m.) från [openSenseMap](https://opensensemap.org) och gör den användbar för biodlare, byggt genom hela kedjan från kod till produktionsliknande drift i Kubernetes.

Projektet är baserat på [DevOps Hive's Dynamic DevOps Roadmap](https://devopsroadmap.io/projects/hivebox/) och har genomförts i sju gradvisa faser: från grundläggande Python-kod till full GitOps-driven Kubernetes-deployment.

## Arkitektur

## Status

- [x] Fas 1: Kickoff & förberedelse
- [x] Fas 2: Grundkod & Docker
- [x] Fas 3: API-endpoints & CI
- [x] Fas 4: Kubernetes & metrics
- [x] Fas 5: Cache, storage & Helm
- [x] Fas 6: GitOps med Argo CD
- [x] Fas 7: Capstone → se relaterat projekt [greenops-cost-estimator](https://github.com/arash00009/greenops-cost-estimator)

## Tech stack

Python (Flask), Docker, Kubernetes, Helm, Argo CD, Valkey, MinIO, Prometheus, GitHub Actions

## Köra applikationen

### Lokalt

```bash
python3 app.py
```

### Med Docker

```bash
docker build -t hivebox:v0.3.0 .
docker run --rm -p 5000:5000 hivebox:v0.3.0
```

Båda ska skriva ut den aktuella versionen, t.ex. `v0.3.0`.

## API-endpoints

### GET /version

Returnerar den aktuella versionen av applikationen.

```bash
curl http://localhost:5000/version
```
```json
{"version": "v0.3.0"}
```

### GET /temperature

Returnerar medeltemperaturen från 3 senseBoxar (openSenseMap), läst från cache om tillgänglig, annars hämtad live. Baserat på mätningar som är max 1 timme gamla.

```bash
curl http://localhost:5000/temperature
```
```json
{"temperature": 15.12, "unit": "celsius", "status": "Good", "sensors_used": 3}
```

Om ingen färsk data finns tillgänglig returneras statuskod 503 med ett felmeddelande.

### GET /cache

Tvingar fram en cache-uppdatering direkt (utanför den ordinarie 5-minuterscykeln).

```bash
curl http://localhost:5000/cache
```
```json
{"message": "Cache updated", "data": {"temperature": 15.12, "unit": "celsius", "status": "Good", "sensors_used": 3}}
```

### GET /store

Sparar en tidsstämplad kopia av senaste temperaturdatan till MinIO.

```bash
curl http://localhost:5000/store
```
```json
{"message": "Data stored", "object": "temperature-20260905T192936.json"}
```

### GET /readyz

Readiness-check. Returnerar 503 om mer än hälften av senseBoxarna är onåbara.

```bash
curl http://localhost:5000/readyz
```
```json
{"status": "ready"}
```

### GET /metrics

Exponerar Prometheus-metrics: standardmått för HTTP-requests, svarstider och Python-processinfo.

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
# Skapa klustret
kind create cluster --name hivebox --config k8s/kind-config.yaml

# Installera Ingress-Nginx
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Bygg och ladda in imagen
docker build -t hivebox:v0.3.0 .
kind load docker-image hivebox:v0.3.0 --name hivebox

# Deploya via Helm
helm install hivebox hivebox-chart/
```

Appen nås sedan på `http://localhost:8080` (port 80 mappas till 8080 i Kind-konfigurationen för att undvika lokala portkonflikter).

Konfigurerbara värden (image-tag, antal repliker, miljövariabler för Valkey/MinIO m.m.) finns i `hivebox-chart/values.yaml`.

Avinstallera:
```bash
helm uninstall hivebox
```

## Cache och Storage

Appen använder **Valkey** (Redis-kompatibel) för cachning av temperaturdata i 5 minuter, och **MinIO** (S3-kompatibel) för periodisk lagring av data som JSON-objekt.

## GitOps med Argo CD

Applikationen deployas deklarativt via Argo CD, som automatiskt synkar klustret mot Helm-chartet i detta repo (`hivebox-chart/`) varje gång `main`-branchen uppdateras — inga manuella `kubectl apply` eller `helm upgrade` behövs efter första installationen.

### Installera Argo CD

```bash
kubectl create namespace argocd
kubectl apply -n argocd --server-side -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### Skapa Application

```bash
kubectl apply -f k8s/argocd/hivebox-application.yaml
```

Auto-sync och self-heal är aktiverat.

### Öppna Argo CD UI

```bash
kubectl port-forward svc/argocd-server -n argocd 8081:443
```

Öppna `https://localhost:8081`, logga in med `admin` och lösenordet från:
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

## Relaterat projekt

[**greenops-cost-estimator**](https://github.com/arash00009/greenops-cost-estimator) — Capstone-projektet (Fas 7): ett fristående API som uppskattar molnkostnad och CO2-avtryck för olika cloud-regioner, byggt med samma metodik.

## Om projektet

Byggt av [Arash Rahimi](https://github.com/arash00009) som ett portfolio-projekt för att demonstrera end-to-end DevOps/Platform Engineering-kompetens: från applikationskod till containerisering, CI/CD, Kubernetes, observability och GitOps.
