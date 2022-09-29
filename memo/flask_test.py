from flask import Flask, request
import json

app = Flask(__name__)


@app.route('/')
def get_request():
    contents = request.args.get('data', '')
    data = json.loads(contents)
    print(type(data))
    print(data["car_id"])

    return contents


if __name__ == "__main__":
    app.run(debug=True)
