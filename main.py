import json
import os
import sys

import stepic as stepic
from PIL import Image
from flask import Flask, request, redirect, url_for, render_template, jsonify
from werkzeug.utils import secure_filename
import face_recognition
import cv2
import cv2
from face_recognition import face_encodings, compare_faces
import uuid
import face_compare as fc
import numpy as np

UPLOAD_FOLDER = '/Users/badri.sannidhi/hackathon-face-reg/Face_rec/upload'
EXISTING_USERS_FOLDER = '/Users/badri.sannidhi/hackathon-face-reg/Face_rec/existing_users'
ALLOWED_EXTENSIONS = set(['png'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EXISTING_USERS_FOLDER'] = EXISTING_USERS_FOLDER


def recognise(im1, im2):
    img_enc1 = read_image(im1)
    img_enc2 = read_image(im2)
    return compare_faces([img_enc1], img_enc2)


def read_image(im):
    img = cv2.imread(im)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return face_encodings(rgb_img)[0]


# def main():
#     res = recognise("srk10.png", "lk2.png")
#     print(res)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/getcreds", methods=['POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        filename = str(uuid.uuid4()) + secure_filename(file.filename)
        cuurent_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(cuurent_file_path)

    existing_users_folder = os.listdir('./existing_users')
    for check_file in existing_users_folder:
        if allowed_file(check_file):
            file_with_relative_path = './existing_users/' + check_file
            is_match = recognise(cuurent_file_path, file_with_relative_path)[0]
            if is_match:
                cv2.destroyAllWindows()
                im = Image.open(file_with_relative_path)
                dec_response = stepic.decode(im)
                delete_file(cuurent_file_path)
                return dec_response
    return jsonify({"IsMatched": False, "UserName": "", "Password": ""})


def delete_file(file_path):
    os.remove(file_path)


@app.route("/register", methods=['POST'])
def register():
    if request.method == 'POST':
        file = request.files['file']
        user_name = request.form['UserName']
        password = request.form['Password']
        filename = str(uuid.uuid4()) + secure_filename(file.filename)
        filename= str(filename.split(".")[0]) + ".png"
        cuurent_file_path = os.path.join(app.config['EXISTING_USERS_FOLDER'], filename)

        file.save(cuurent_file_path)

        im = Image.open(cuurent_file_path)
        msg = bytes(json.dumps({"UserName": user_name, "Password": password}), 'utf-8')
        new_img = stepic.encode(im, msg)
        delete_file(cuurent_file_path)
        new_img.save(cuurent_file_path, "PNG")
    return jsonify({"FileName": cuurent_file_path})


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001, debug=False)
