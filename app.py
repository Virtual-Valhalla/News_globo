from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

NEWS_API_KEY = 'NEWS_API_KEY'

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/country-news")
def country_news():
    code = request.args.get("code", "world").lower()

    try:
        # 🌍 GLOBAL
        if code == "world":
            url = f'https://newsapi.org/v2/everything?q=world&sortBy=publishedAt&apiKey={NEWS_API_KEY}'
            return jsonify(requests.get(url).json())

        # 🔹 1. Intento con top-headlines
        url = f'https://newsapi.org/v2/top-headlines?country={code}&apiKey={NEWS_API_KEY}'
        response = requests.get(url).json()

        # 🔻 2. Si no hay noticias → fallback
        if not response.get("articles"):
            url = f'https://newsapi.org/v2/everything?q={code}&sortBy=publishedAt&apiKey={NEWS_API_KEY}'
            response = requests.get(url).json()

        return jsonify(response)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)