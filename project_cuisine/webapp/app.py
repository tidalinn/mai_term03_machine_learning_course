import flask
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import TextVectorization
import pickle

from funcs.utils import transform_label, transform_probs_to_labels


# import models
multilabel = pickle.load(open('model/multilabel.pkl', 'rb'))
model = load_model('model/model.h5')
vectorizer_file = pickle.load(open('model/vectorizer.pkl', 'rb'))


# flask app
app = flask.Flask(__name__, template_folder='templates')
@app.route('/', methods=['GET', 'POST'])


def main():
    if flask.request.method == 'GET':
        return(flask.render_template('main.html'))

    if flask.request.method == 'POST':
        # get dish name
        name = flask.request.form['name']

        # convert vectorizer
        vectorizer = TextVectorization.from_config(vectorizer_file['config'])
        vectorizer.adapt([name])
        vectorizer.set_weights(vectorizer_file['weights'])

        # make predictions
        prediction = model.predict(vectorizer([name]))

        # convert predictions
        prediction = transform_probs_to_labels(prediction)[0]

        if sum(prediction) == 0:
            prediction = 'No results'
        else:
            prediction = transform_label(prediction, multilabel)
            prediction = ', '.join(*prediction)
        
        # return predictions
        return(flask.render_template('main.html', result=prediction))


if __name__ == '__main__':
    app.run(debug=True)