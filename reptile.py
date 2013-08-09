from __future__ import print_function

import os.path
import random
import subprocess
import sys
from contextlib import contextmanager

import flask
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename

import config


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass

tile_shell_cmd = '''
mkdir -p {tile_filename}/{z}/{x} ; \

LD_LIBRARY_PATH=/opt/Kakadu/lib /opt/Kakadu/bin/kdu_buffered_expand \
    -i {jp2_filename} \
    -o {tile_filename}/{z}/{x}/{y}.pgm \
    -reduce {level} \
    -int_region \"{{{tile_y},{tile_x}}},{{{tilesize},{tilesize}}}\" \
    2>/dev/null && \

convert \
    -background black \
    -extent {tilesize}x{tilesize} \
    {tile_filename}/{z}/{x}/{y}.pgm \
    {tile_filename}/{z}/{x}/{y}.png
'''

dimensions_shell_cmd = '''
LD_LIBRARY_PATH=/opt/Kakadu/lib/7.2 /opt/Kakadu/bin/7.2/kdu_jp2info \
    -i {jp2_filename} \
    | xmllint --xpath '//width/text() | //height/text()' -
'''

app = Flask(__name__)
app.config.from_object(__name__)

app.config.tile_root = config.tile_root
if not app.config.tile_root:
    msg = '''
    You must set a tile root path in config.py before running reptile.
    This location is where reptile will save the generated tiles and
    should be readable and writable by the process owner of reptile.
    '''
    print(msg, file=sys.stderr)
    sys.exit(1)

app.config.jp2_root = config.jp2_root
if not app.config.jp2_root:
    msg = '''
    You must set a JP2 root path in config.py before running reptile.
    '''
    print(msg, file=sys.stderr)
    sys.exit(1)


@app.route('/')
def index():
    sources = [
        ('Fading Rover Tracks Near Victoria Crater', '/PDS/EXTRAS/RDR/ESP/ORB_013900_013999/ESP_013954_1780/ESP_013954_1780_RED.QLOOK.JP2'),
        ('Continued Monitoring of Slope Streaks in Olympus Mons Aureole', '/PDS/EXTRAS/RDR/ESP/ORB_012200_012299/ESP_012258_2080/ESP_012258_2080_RED.QLOOK.JP2'),
        ('Meander and Tributary of Scamander Vallis', '/PDS/EXTRAS/RDR/ESP/ORB_011200_011299/ESP_011289_1950/ESP_011289_1950_RED.QLOOK.JP2'),
        ('Crater in Meridiani Planum with Layering', '/PDS/EXTRAS/RDR/ESP/ORB_011200_011299/ESP_011277_1825/ESP_011277_1825_RED.QLOOK.JP2'),
    ]
    with ignored(IOError):
        with open('../jp2_index') as f:
            for n, line in enumerate(f):
                if random.randrange(n + 2):
                    continue
                sources.append(line.split('='))
    return render_template('index.html', sources=sources)


@app.route('/<path:filename>.JP2')
def jp2_source(filename):
    filename = '/' + filename + '.JP2'
    jp2_filename = app.config.jp2_root + filename
    cmd = dimensions_shell_cmd.format(jp2_filename=jp2_filename)
    child = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    width, height = child.stdout.readline().split()
    return render_template('single-source-view.html',
                           filename=filename, width=width, height=height)


@app.route('/<path:filename>/<int:z>/<int:x>/<int:y>.png')
def tile(filename, z, x, y):
    tilesize = 256
    tile = '%s/%s/%d/%d/%d.png' % (app.config.tile_root, filename, z, x, y)
    if not os.path.exists(tile):
        cmd = tile_shell_cmd.format(
            tile_filename=app.config.tile_root + filename,
            jp2_filename=app.config.jp2_root + filename,
            z=z, x=x, y=y, level=10-z,
            tile_x=x*tilesize, tile_y=y*tilesize, tilesize=tilesize)
        if subprocess.call(cmd, shell=True) != 0:
            tile = app.config.tile_root + '/black.png'
    return flask.send_file(tile, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
