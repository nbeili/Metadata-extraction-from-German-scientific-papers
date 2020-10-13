import os
from flask import Flask, flash, Response, request, send_file, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image
import time
import json

from pubmex.pubmexinference import PubMexInference

UPLOAD_FOLDER = '/home/appuser/detectron2_repo/app/uploads/'
ALLOWED_EXTENSIONS = {'pdf'}

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
    output = {}

    if request.method == 'POST':
        if 'file' not in request.files:
            output["flash"] = "Please upload a PDF document above!"
            return Response(json.dumps(output), mimetype='text/json')
        
        file = request.files['file']
        print(file.filename)
        if file.filename == '':
            output["flash"] = "Please upload a PDF document above!"
            return Response(json.dumps(output), mimetype='text/json')
        if not allowed_file(file.filename):
            output["flash"] = 'Wrong file format. Please upload a PDF document!'
            return Response(json.dumps(output), mimetype='text/json')
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            file_saved = False
            waited = 0
            while not file_saved:
                if not os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                    time.sleep(1)
                    waited += 1
                    print("waiting")
                else:
                    file_saved = True
                if waited > 20:
                    return redirect(request.host_url)
            for i in range(3):
                while True:
                    try:
                        v, metadata = pubmex.predict(app.config['UPLOAD_FOLDER'] + filename)
                        img = Image.fromarray(v.get_image()[:, :, ::-1])
                        img_path = app.config['UPLOAD_FOLDER'] + filename[:-4] + ".jpg"
                        img.save(img_path)
                        output["output"] = metadata
                        output["image_path"] = app.config['UPLOAD_FOLDER'] + filename[:-4] + ".jpg"
                        return Response(json.dumps(output), mimetype='text/json')
                    except:
                        output["flash"] = "Something went wrong uploading the file - please try again."
                        if i == 2:
                            return Response(json.dumps(output), mimetype='text/json')
                        continue
                    break
    return render_template("index.html")

@app.route('/deletefile/<filename>')
def delete_file(filename):
    print("remove file")
    flash("Deleted file {}".format(filename))
    try:
        os.remove(app.config['UPLOAD_FOLDER'] + filename)
        os.remove(app.config['UPLOAD_FOLDER'] + filename[:-4] + ".jpg")

        return redirect(url_for('upload_file', filename=filename))  
    except:
        pass


if __name__ == '__main__':
    app.run(host='0.0.0.0')


