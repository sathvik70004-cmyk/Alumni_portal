# run.py

from app import app

if __name__ == '__main__':
    # Use host='0.0.0.0' to be accessible on local network if needed
    # Port can be specified e.g., app.run(debug=True, port=5001)
    app.run(debug=app.config['DEBUG'])