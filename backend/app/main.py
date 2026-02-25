from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.routes import save_routes, search_routes, insights_routes, auth_routes
import sqlalchemy

app = FastAPI(title=settings.APP_NAME, version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(save_routes.router)
app.include_router(search_routes.router)
app.include_router(insights_routes.router)


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.execute(sqlalchemy.text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    print(f"✅ {settings.APP_NAME} v0.2.0 started — multi-user + auth enabled")


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": "0.2.0"}

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.core.config import settings
# from app.core.database import engine, Base
# from app.api.routes import save_routes, search_routes, insights_routes
# import sqlalchemy

# app = FastAPI(
#     title=settings.APP_NAME,
#     version="0.1.0",
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Register all routes
# app.include_router(save_routes.router)
# app.include_router(search_routes.router)
# app.include_router(insights_routes.router)


# @app.on_event("startup")
# async def on_startup():
#     async with engine.begin() as conn:
#         await conn.execute(sqlalchemy.text("CREATE EXTENSION IF NOT EXISTS vector"))
#         await conn.run_sync(Base.metadata.create_all)
#     print(f"✅ {settings.APP_NAME} backend started")


# @app.get("/health")
# async def health():
#     return {"status": "ok", "app": settings.APP_NAME}