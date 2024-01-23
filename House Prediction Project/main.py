from flask import Flask, request, render_template
import pickle
import numpy as np

app = Flask(__name__, template_folder="templates")

model = pickle.load(open('RidgeModel.pkl', 'rb'))


@app.route('/')
def hello_world():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)