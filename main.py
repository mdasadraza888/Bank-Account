import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Database.db_models import engine, Base
from API.account_api import app as bank_router

app = FastAPI(
    title="Nexus Corporate Bank",
    description="A multi-tier polymorphic ledger architecture engine driving secure banking transactions.",
    version="1.0.0"
)

# origins = [
#     "http://localhost",
#     "http://127.0.0.1",
#     "http://localhost:8501",   # 💡 Standard default execution port for Streamlit
#     "http://127.0.0.1:8501",   # Ensures match regardless of terminal navigation
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Permits local front-end engine streams
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, PATCH, DELETE operations
    allow_headers=["*"],
)

Base.metadata.create_all(engine)

app.include_router(bank_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)