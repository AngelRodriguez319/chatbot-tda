from os import environ
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from Chabot.chatbot import ChatBot
import json

app = Flask(__name__, static_folder="static", template_folder="templates")
cors = CORS(app, resources={r"*": {"origins": "*"}}, supports_credentials=True)
bot = ChatBot()


@app.route('/getResponse', methods=['POST'])
def messageBot():
    data = request.json["message"]
    response = bot.getResponse(data)
    return jsonify({
        'status': 200,
        'mimetype': 'application/json',
        'response': response
    })

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")

if(__name__) == '__main__':
    app.run(debug=False, port=environ.get("PORT", 5000), host='0.0.0.0')

# set "FLASK_ENV=development"
# set "FLASK_APP=app.py"