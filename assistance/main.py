import uvicorn
from apis.api_controller import app
from utils.logger import setup_logger

logger = setup_logger("main")

if __name__ == "__main__":
    logger.info("Starting Assistance API server...")
    uvicorn.run(app, host="localhost", port=8000)




