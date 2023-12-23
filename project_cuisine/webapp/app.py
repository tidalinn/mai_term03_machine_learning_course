import flask
import pandas as pd

from funcs.utils import check_hour, get_predictions, create_rating

# load data
data_count_rating = pd.read_csv('data/data_count_rating.csv', index_col=0)

# flask app
app = flask.Flask(__name__, template_folder='templates')
@app.route('/', methods=['GET', 'POST'])

def main():
    if flask.request.method == 'GET':
        return(flask.render_template('main.html')
    )

    if flask.request.method == 'POST':
        # get fields
        name = flask.request.form['name']
        hour = flask.request.form['hour']
        address = flask.request.form['address']

        # get predictions
        prediction = get_predictions(name)

        
        cuisine_rating, location_rating = create_rating(
            data_count_rating, address, hour, prediction, top=5
        )

        hour = f' at {hour} AM' if 0 < int(hour) < 12 else f' at {hour} PM'
        
        # return fields
        return(
            flask.render_template(
                'main.html', 
                dish=name,
                hour=hour,
                result=prediction,
                cuisine_rating=cuisine_rating,
                location_rating=location_rating
            )
        )


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=8000)