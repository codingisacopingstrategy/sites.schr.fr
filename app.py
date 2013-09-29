#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
import json

from flask import Flask, jsonify, render_template, request, g, send_file, Markup

import Image

app = Flask(__name__)

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
LOCATION = os.path.join(PROJECT_DIR, 'static/')
FINAL_LOCATION = os.path.join(PROJECT_DIR, 'static/img/scaled/') 
RATIO = 0.24

@app.before_request
def before_request():
    """Read the json each time the page is displayed"""
    f = codecs.open('sites.json', 'r', 'utf-8')
    g.sites = json.loads(f.read())
    f.close()

def dimensions(filename):
    original = os.path.join(LOCATION, filename)
    if os.path.exists(original):
        im = Image.open(original)
        width = int((float(im.size[0])*float(RATIO)))
        height = int((float(im.size[1])*float(RATIO)))
        return (width, height)
    return (None, None)

@app.template_filter('image')
def generate_image_tag(filename):
    width, height = dimensions(filename)
    if width:
        return Markup('<img src="/%s/%s" width="%s" height="%s" />' % (width, filename, width, height))
    return ""

@app.template_filter()
def width(filename):
    return dimensions(filename)[0]

@app.route('/')
def index():
    return render_template('index.html', sites=g.sites)

@app.route("/<int:size>/<filename>")
def image(size, filename):
    original = os.path.join(LOCATION, filename)
    FINALPATH = os.path.join(FINAL_LOCATION, str(size))
    final = os.path.join(FINALPATH, filename)
    if os.path.exists(final):
        return send_file(final)
    elif os.path.exists(original):
        if not os.path.exists(FINALPATH):
            os.makedirs(FINALPATH)
        bounding = (size, size)
        im = Image.open(original)
        
        width = size
        ratio = (width/float(im.size[0]))
        height = int((float(im.size[1])*float(ratio)))

        im = im.resize((width,height), Image.ANTIALIAS)
        im.save(final)
        return send_file(final)
    else:
        abort(404)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
