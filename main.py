from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import qanswer, platypus, gAnswer, rubq, deeppavlov, tebaqa


app = FastAPI(
            title="QA Systems Wrapper",
            # version=linguaf.__version__,
            description=""
)

app.include_router(qanswer.router)
app.include_router(platypus.router)
app.include_router(gAnswer.router)
app.include_router(rubq.router)
app.include_router(deeppavlov.router)
app.include_router(tebaqa.router)

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
