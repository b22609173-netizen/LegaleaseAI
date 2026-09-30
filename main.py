from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from.import routes

app = FastAPI(title="LegalEase AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)

@app.get("/")
def home():
    return {"message": "LegalEase AI Backend is running"}