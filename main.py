from fastapi import FastAPI
from database import engine  # Adjust the import statement here

app = FastAPI()

# Just a placeholder route
@app.get("/")
def read_root():
    return {"Hello": "World"}
