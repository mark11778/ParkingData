from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/python-function', methods=['GET'])
def my_python_function():
    data = request.args.get('data', default='default value', type=str)
    # Example function processing
    print("here")
    processed_data = data.upper()  # Example operation
    return jsonify({'result': processed_data})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
