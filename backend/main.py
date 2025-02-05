from fastapi import FastAPI
from auth import ao3_login

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AO3 Scheduler API is running!"}

@app.post("/login")
def login():
    result = ao3_login()
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
