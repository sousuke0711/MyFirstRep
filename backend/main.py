from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import stocks, analysis

app = FastAPI(
    title="東証プライム株価予測API",
    description="ファンダメンタルズスクリーニング + Claude AIによる銘柄分析",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router, prefix="/api", tags=["銘柄"])
app.include_router(analysis.router, prefix="/api", tags=["AI分析"])


@app.get("/")
def root():
    return {"message": "東証プライム株価予測API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
