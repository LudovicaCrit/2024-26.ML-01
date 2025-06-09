from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/infer', methods=['POST'])
def hello():
    data = request.get_json()
    name = data.get('name', 'Stranger')
    return jsonify({"message": "Hello {}!".format(name)})

if __name__ == '__main__':
    app.run(debug=True)