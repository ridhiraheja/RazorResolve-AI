from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.api.routes import dashboard, incidents, payments, products, carts, audit
from app.api.routes import checkout, payments_extended, financial

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="RazorResolve AI",
    description="AI Commerce Recovery Agent — Razorpay AI Builder Hackathon 2026",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(incidents.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(carts.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(checkout.router, prefix="/api/v1")
app.include_router(payments_extended.router, prefix="/api/v1")
app.include_router(financial.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": "RazorResolve AI",
        "version": "1.0.0",
        "tagline": "An autonomous AI commerce agent that turns failed checkouts into recovered revenue.",
        "status": "operational",
        "disclaimer": "This is a hackathon prototype using synthetic/demo data. Not a real Razorpay production integration.",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
