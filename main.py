import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import qanswer, platypus, gAnswer, rubq, deeppavlov, tebaqa, qanary, deeppavlov2023

__version__ = "0.0.6"

app = FastAPI(
            title="QA Systems Wrapper",
            version=__version__,
            description=""
)

app.include_router(qanswer.router)
app.include_router(platypus.router)
app.include_router(gAnswer.router)
# app.include_router(rubq.router)
app.include_router(deeppavlov.router)
app.include_router(tebaqa.router)
app.include_router(qanary.router)
app.include_router(deeppavlov2023.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", include_in_schema=False)
async def root():
    return {"message": "Hello Bigger Applications!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
