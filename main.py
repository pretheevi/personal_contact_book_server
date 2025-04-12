from flask import Flask
from flask_cors import CORS
from router import routes 

app = Flask(__name__)
CORS(app, origins=[
  "http://localhost:5173",
  "https://personal-contact-book.onrender.com"
])

app.register_blueprint(routes)

if __name__=="__main__":
  app.run(host="0.0.0.0", port=8080, debug=True)
