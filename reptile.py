from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import flask

import os.path
import subprocess

shell_cmd = '''
/bin/mkdir \
    -p static/{filename}/{z}/{x} && \
/usr/local/kakadu-7.2/bin/Mac-x86-64-gcc/kdu_buffered_expand \
    -i {filename} \
    -o static/{filename}/{z}/{x}/{y}.pgm \
    -reduce {level} \
    -num_threads 2 \
    -int_region \"{{{tile_y},{tile_x}}},{{{tilesize},{tilesize}}}\" && \
/usr/local/bin/convert \
    -background black \
    -extent {tilesize}x{tilesize} \
    static/{filename}/{z}/{x}/{y}.pgm \
    static/{filename}/{z}/{x}/{y}.png && \
/bin/rm \
    -f static/{filename}/{z}/{x}/{y}.pgm
'''

DEBUG = True
SECRET_KEY = '29298cfabc017f006fcd5a4f9ea42afbba50b9a6'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<filename>/<int:z>/<int:x>/<int:y>.png')
def tile(filename, z, x, y):
    tilesize = 256
    filename = secure_filename(filename)
    fullpath = './static/%s/%d/%d/%d.png' % (filename, z, x, y)
    if not os.path.exists(fullpath):
        cmd = shell_cmd.format(
                filename=filename,
                z=z, x=x, y=y, level=10-z,
                tile_x=x*tilesize, tile_y=y*tilesize, tilesize=tilesize)
        subprocess.call(cmd, shell=True)
    return flask.send_file(fullpath, mimetype='image/png')

if __name__ == '__main__':
    app.run()
