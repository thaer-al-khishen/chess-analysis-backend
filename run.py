from gunicorn.app.wsgiapp import run

# Import your Flask application instance
from main import app

if __name__ == '__main__':
    run()
