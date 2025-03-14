from flask import Flask, request, redirect

app = Flask(__name__)

@app.route("/test", methods=['GET'])
def home():
    return "Server is working fine"

@app.route("/", methods=['GET'])
def redirect_url():
    original_url = request.args.get('watch')
    return redirect(f"http://127.0.0.1:5000/redirecting?url=https://www.youtube.com/watch?v={original_url}")

if __name__ == "__main__":
    app.run(debug=True)
