## Setup

pip install -r requirements.txt

## Run

uvicorn app.main:app --reload

## API Endpoints

POST /trees
GET /trees
PUT /trees/{id}
GET /trees/stats