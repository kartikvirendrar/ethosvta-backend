from flask import Flask, request
from deepspeech import Model
import numpy as np
from heapq import nlargest
from IPython.display import Audio
import requests
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
import text2emotion as te
import speech_recognition as sr
from playsound import playsound
import nltk
nltk.download('omw-1.4')

app = Flask(_name_)


# Srt file
import pvleopard
leopard = pvleopard.create(access_key="Cl5NXMtfMUcDUIrBlkNaJe8yPEq5BxQ1KRqAuZVNrAWZYL0FxYy09w==")

# Audio to text
model_file_path = 'deepspeech-0.9.3-models.pbmm'
lm_file_path = 'deepspeech-0.9.3-models.scorer'
beam_width = 100
lm_alpha = 0.93
lm_beta = 1.18

model = Model(model_file_path)
model.enableExternalScorer(lm_file_path)

model.setScorerAlphaBeta(lm_alpha, lm_beta)
model.setBeamWidth(beam_width)

@app.route('/')
def index():
  return 'Server Works!'  

def get_summary(text):
    nlp = spacy.load('en_core_web_sm')
    per=1
    doc= nlp(text)
    tokens=[token.text for token in doc]
    word_frequencies={}
    for word in doc:
        if word.text.lower() not in list(STOP_WORDS):
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
    max_frequency=max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word]=word_frequencies[word]/max_frequency
    sentence_tokens= [sent for sent in doc.sents]
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():                            
                    sentence_scores[sent]=word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent]+=word_frequencies[word.text.lower()]
    select_length=int(len(sentence_tokens)*per)
    summary=nlargest(select_length, sentence_scores,key=sentence_scores.get)
    final_summary=[word.text for word in summary]
    summary=''.join(final_summary)
    return summary

@app.route('/summary',methods=["POST"])
def summarize():
    data = request.get_json()
    text = data["text"]
    per=1
    # summary = te.get_emotion(text)
    summary = get_summary(text)
    
    # nlp = en_core_web_sm.load()
    
    return {"summary":summary}



@app.route('/finalAudioToText', methods=['POST'])
def finalAudioToText():
    """
    format intput data format should be as
    {
        "link" : "linkToWaveAudio.wav
    }
    output format will be as
    {
        "text": "converted text"
    }
    """
    data = request.get_json()
    link = data["link"]
    r = sr.Recognizer()
    doc = requests.get(link)
    sig = np.frombuffer(doc.content, dtype=np.int16)
    return {"text" : model.stt(sig) }    

@app.route('/finalSentimentCompleteAudio', methods=['POST'])
def finalSentimentCompleteAudio():  
    """
    format intput data format should be as
    {
        "link" : "linkToWaveAudio.wav
    }

    output format will be as
    {
        "text": "text"
        "sentiment" : "text sentiment"
    }
    """
    data = request.get_json()
    link = data["link"]
    doc = requests.get(link)
    data16 = np.frombuffer(doc.content, dtype=np.int16)
    text = model.stt(data16)
    sentimentDict = te.get_emotion(text)
    sentiment = ''
    sentimentScore = 0
    for key, value in sentimentDict.items():
        if sentimentScore>=value:
            sentiment=key
            sentimentScore=value
    return ({'text': text, 'sentiment':sentiment})
    

# Cl5NXMtfMUcDUIrBlkNaJe8yPEq5BxQ1KRqAuZVNrAWZYL0FxYy09w==
# Cl5NXMtfMUcDUIrBlkNaJe8yPEq5BxQ1KRqAuZVNrAWZYL0FxYy09w==

@app.route('/generateSrtFile', methods=['POST'])
def generateSrtFile():
    """
    format intput data format should be as
    {
        "link" : "linkToWaveAudio.wav"
    }

    output format will be as
    {
        "subtitlesInString" :"raw data can be converted to .srt file easily"
    }
    """
    # link = "https://res.cloudinary.com/dyr4hl32b/video/upload/v1673098748/longLengthTestAudio_qg8b4t.wav"
    data = request.get_json()
    link = data["link"]
    doc = requests.get(link)
    data = np.frombuffer(doc.content, dtype=np.int16)
    transcript, words = leopard.process(data) 
    summary = get_summary(transcript)
    listOfSubs = to_srt(words)
    listOfSentiments = []
    for sub in listOfSubs:
        sentimentDict = te.get_emotion(transcript)
        sentiment = ''
        sentimentScore = 0
        for key, value in sentimentDict.items():
            if sentimentScore>=value:
                sentiment=key
                sentimentScore=value
        listOfSentiments.append({"sentiment":sentiment,"index" : sub["index"], "from":sub["from"],"to":sub["to"]})
    res = {
        "success": True,
        "message": "Data Processed successfully",
        "data": {"subs":to_srt(words),"text" : transcript, "summary" : summary, "sentiments":listOfSentiments}
    }
    return res

def second_to_timecode(x: float) -> str:
    hour, x = divmod(x, 3600)
    minute, x = divmod(x, 60)
    second, x = divmod(x, 1)
    millisecond = int(x * 1000.)

    return '%.2d:%.2d:%.2d,%.3d' % (hour, minute, second, millisecond)

def to_srt(
        words: pvleopard.Leopard.Word,
        endpoint_sec: float = 1.,
        length_limit: int = 16) -> str:

    def _helper(end: int) -> None:
        single = {
            "index" : "%d" % section,
            "from" :"%s" % second_to_timecode(words[start].start_sec),
            "to":"%s" % second_to_timecode(words[end].end_sec),
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