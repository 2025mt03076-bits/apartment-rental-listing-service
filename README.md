# Listing Service

Part of the Apartment Rental Platform (SEZG583 assignment). Owns apartment listings and their availability.

- Stack: Python 3.12, FastAPI, Motor (async MongoDB driver) - database `listingdb`
- Port: 3001 (interactive API docs at `/docs`)

## API
| Method | Path | Description |
|---|---|---|
| POST | /listings | Create a listing |
| GET | /listings?city=&min_rent=&max_rent=&bedrooms=&status=&page=&limit= | Search (defaults to AVAILABLE) |
| GET | /listings/{id} | Listing details |
| PUT | /listings/{id} | Update title, description, city, rent, bedrooms |
| PATCH | /listings/{id}/status | Body `{"status": "AVAILABLE" / "RENTED" / "INACTIVE"}` |
| GET | /health | Health check |

## Run locally
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
MONGO_URI=mongodb://localhost:27017/listingdb uvicorn app.main:app --port 3001 --reload
```

## Docker
```
docker build -t listing-service:1.0 .
```

## Kubernetes (minikube)
```
eval $(minikube docker-env)
docker build -t listing-service:1.0 .
kubectl apply -f k8s/mongo.yaml -f k8s/deployment.yaml
```
