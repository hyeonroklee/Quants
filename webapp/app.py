from flask import Flask, render_template
from quantom import *
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    data = generate_stock_prices(n=30)
    return render_template('index.html', data=data)

if __name__ == "__main__":
    app.run(debug = True,port=8080, passthrough_errors=True)