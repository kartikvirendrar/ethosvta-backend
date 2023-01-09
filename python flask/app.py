from flask import Flask, request
from flask_cors import CORS
from flask_restful import Api
import numpy as np
import requests
import pvleopard
leopard = pvleopard.create(access_key="Cl5NXMtfMUcDUIrBlkNaJe8yPEq5BxQ1KRqAuZVNrAWZYL0FxYy09w==")

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
  return 'Server Works!'  

@app.route('/generateSrtFile/<path:l>', methods=['GET'])
def generateSrtFile(l):
    print(l)
    doc = requests.get(l)
    data = np.frombuffer(doc.content, dtype=np.int16)
    transcript, words = leopard.process(data) 
    return ({'subs':to_srt(words),'text' : transcript})

def second_to_timecode(x: float) -> str:
    hour, x = divmod(x, 3600)
    minute, x = divmod(x, 60)
    second, x = divmod(x, 1)
    millisecond = int(x * 1000.)
    return '%.2d:%.2d:%.2d:%.3d' % (hour, minute, second, millisecond)

def to_srt(
        words: pvleopard.Leopard.Word,
        endpoint_sec: float = 1.,
        length_limit: int = 16) -> str:

    def _helper(end: int) -> None:
        single = {
            "index" : "%d" % section,
            "from" :"%s" % (words[start].start_sec),
            "to":"%s" % (words[end].end_sec),
            "text" :' '.join(x.word for x in words[start:(end + 1)])
        }
        lines.append(single)

    lines = []
    section = 0
    start = 0
    for k in range(1, len(words)):
        if ((words[k].start_sec - words[k - 1].end_sec) >= endpoint_sec) or \
                (length_limit is not None and (k - start) >= length_limit):
            _helper(k - 1)
            start = k
            section += 1
    _helper(len(words) - 1)
    return lines

if __name__ == '__main__':
    app.run(debug=True)   