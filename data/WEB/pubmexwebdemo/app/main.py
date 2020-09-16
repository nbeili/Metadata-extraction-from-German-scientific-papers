import os
from flask import Flask, flash, Response, request, send_file, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import time

from pubmex.pubmexinference import *

UPLOAD_FOLDER = '/home/appuser/detectron2_repo/app/uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = os.urandom(24)

pubmex = PubMexInference(
    model_dump='/home/appuser/detectron2_repo/app/models/final/model_final.pth', 
    config_file='/home/appuser/detectron2_repo/app/configs/final/train_config.yaml',
    use_cuda=False,
    )

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/uploadpdf', methods=["GET", "POST"])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.host_url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            v, metadata = pubmex.predict(app.config['UPLOAD_FOLDER'] + filename)
            img = Image.fromarray(v.get_image()[:, :, ::-1])
            img_path = "/home/appuser/detectron2_repo/app/static/" + filename[:-4] + ".jpg"
            img.save(img_path)
            output = {}
            output["output"] = metadata
            output["image_path"] = "/static/"+ filename[:-4] + ".jpg"
            return Response(json.dumps(output), mimetype='text/json')
    
    return render_template("index.html")

"""@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
"""
@app.route('/deletefile/<filename>')
def delete_file(filename):
    print("remove file")
    os.remove(app.config['UPLOAD_FOLDER'] + filename)
    os.remove("/home/appuser/detectron2_repo/app/static/" + filename[:-4] + ".jpg")

    return redirect(url_for('upload_file', filename=filename))


if __name__ == '__main__':
    app.run(host='0.0.0.0')


