from fastapi import FastAPI


from api.auth_routes import router as auth_router 
from api.chat_routes import router as chat_router 
app = FastAPI(title =  "AI Knowledge Studio")

app.include_router(auth_router)
app.include_router(chat_router)


@app.get("/health")
def health_check():
    return {"message" : "health is ok "}