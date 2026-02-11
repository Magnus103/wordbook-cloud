from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/guess', methods=['POST'])
def guess():
    prompt = request.json.get("text")

    result = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return jsonify({
        "answer": result.choices[0].message.content
    })


if __name__ == '__main__':
    app.run(debug=True)
