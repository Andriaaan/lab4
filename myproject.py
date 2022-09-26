from flask import Flask
app = Flask(__name__)

@app.route("/api/v1/hello-world-1")
def hello():
    return "<h1 style='color:green'>Hello World-1</h1>"
    
@app.route("/api/v1/hello-world")
def hello1():
    return "<h1 style='color:red'>Hello World!</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0')


