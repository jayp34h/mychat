from flask import Flask, request, redirect
import jwt
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)
SECRET_KEY = 'dc707ccf4dcd014384e0a0de7bdf2e437960164779561d86f9f24af245e6be0b'

def decode_token(token):
    """Decode and validate JWT token"""
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired. Please log in again."}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token. Please log in again."}

@app.route("/chatbot")
def chatbot():
    """Handle chatbot requests with token authentication"""
    # Get token from query parameters
    token = request.args.get("token")
    if not token:
        return {"error": "Missing authentication token"}, 401

    # Decode and validate token
    user_info = decode_token(token)

    if "error" in user_info:
        return user_info, 401

    # Extract user information from token
    try:
        name = user_info["name"]
        email = user_info["email"]
        return {
            "status": "success",
            "message": f"Welcome, {name}!",
            "user": {
                "name": name,
                "email": email
            }
        }, 200
    except KeyError:
        return {"error": "Invalid token format"}, 400

@app.route("/redirect-to-report")
def redirect_to_report():
    token = request.args.get("token")
    symptoms = request.args.get("symptoms", "")  # Get symptoms from query param
    
    if not token:
        return {"error": "Missing authentication token"}, 401
    
    # Verify token is valid before redirecting
    user_info = decode_token(token)
    if "error" in user_info:
        return user_info, 401
        
    return redirect(f"https://reportsemail.onrender.com?token={token}&symptoms={symptoms}")

if __name__ == "__main__":
    app.run(debug=True)