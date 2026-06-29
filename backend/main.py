from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, products, cart

app = FastAPI(title="Palette API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)


@app.get("/health")
def health():
    return {"status": "ok"}
