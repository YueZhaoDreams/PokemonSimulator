from app.main import app
import uvicorn
from app.config import HOST, PORT

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
