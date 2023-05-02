import numpy as np
import torch
from collections import Counter
from sklearn.preprocessing import LabelEncoder
import boto3
import librosa
from model.model import genreNet
from model.config import MODELPATH, acs_key, acs_sec
from model.config import GENRES
import flask
import json
#from pydub import AudioSegment

s3_client = boto3.client('s3', aws_access_key_id=acs_key,aws_secret_access_key= acs_sec,region_name="us-east-1")
import warnings
warnings.filterwarnings("ignore")
import logging


def main(audio_path):

    le = LabelEncoder().fit(GENRES)
    net         = genreNet()
    net.load_state_dict(torch.load(MODELPATH, map_location='cpu'))

    y, sr       = librosa.load(audio_path, mono=True, sr=22050)
    S           = librosa.feature.melspectrogram(y=y, sr=sr).T
    S           = S[:-1 * (S.shape[0] % 128)]
    num_chunk   = S.shape[0] / 128
    data_chunks = np.split(S, num_chunk)
    genres = list()
    for i, data in enumerate(data_chunks):
        data    = torch.FloatTensor(data).view(1, 1, 128, 128)
        preds   = net(data)
        pred_val, pred_index    = preds.max(1)
        pred_index              = pred_index.data.numpy()
        pred_val                = np.exp(pred_val.data.numpy()[0])
        pred_genre              = le.inverse_transform(pred_index).item()
        if pred_val >= 0.5:
            genres.append(pred_genre)
    # ------------------------------- #
    s           = float(sum([v for k,v in dict(Counter(genres)).items()]))
    pos_genre   = sorted([(k, v/s*100) for k,v in dict(Counter(genres)).items()], key=lambda x:x[1], reverse=True)
    pos_genre_dict = {}
    for i in pos_genre:
        pos_genre_dict[i[0]] = i[1]
    return pos_genre_dict




app = flask.Flask(__name__)
@app.route('/', methods=['GET'])
def ping():
    # Check if the classifier was loaded correctly
    try:
        #regressor
        status = 200
        logging.info("Status : 200")
    except:
        status = 400
    return flask.Response(response= json.dumps(' '), status=status, mimetype='application/json' )


@app.route('/audiofilename')
def hello_world():
    filename = flask.request.args.get('audiopath')
    s3_client.download_file("spotflix-video-dataset",filename,"temp.mp4")
    #filename = librosa.ex('trumpet')
    filename = "temp.mp4"
    pos_genre = main(filename)

    result = {
        'output': pos_genre
        }

    resultjson = json.dumps(result)
    return flask.Response(response=resultjson, status=200, mimetype='application/json')
 
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
    

    