from fastapi import FastAPI
import os
from chains.feautres_chain import run_chain
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
loaded = load_dotenv()




from api.auth_routes import router as auth_router 
from api.chat_routes import router as chat_router 
app = FastAPI(title =  "AI Knowledge Studio")

app.include_router(auth_router)
app.include_router(chat_router)



origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://your-service-name.up.railway.app/",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins  = origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/health")
def health_check():
    return {"message" : "health is ok "}


