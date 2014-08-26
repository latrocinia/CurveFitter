from __future__ import print_function
import os
from flask import Flask, render_template, request, url_for, redirect
from curvefitter import CurveFitter, parse, string_to_func

app = Flask(__name__)
cf = CurveFitter()

@app.route('/', methods=['GET'])
def fit_app():

    popt = {}
    try:
        expression = request.args['expression']
        xvariable = request.args['xvariable']

        xvalues = [float(x) for x in request.args['xvalues'].split()]
        yvalues = [float(y) for y in request.args['yvalues'].split()]

        parameters = parse(expression)
        parameters.remove(xvariable)
        my_func = string_to_func(expression, parameters, xvariable)
        cf.set_data(xvalues, yvalues)
        cf.set_func(my_func)
        popt = cf.fit()

    except:
        pass

    return render_template('form.html', popt=popt)

if __name__=='__main__':
    app.run()
