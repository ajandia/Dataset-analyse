from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    request,
    redirect,
    url_for,
    send_file
)
import os
from utils.explore_database import explore_regex, liste_mots_cles, ngrammes, plot_schema, get_regex_data
from utils.helpers import load_config, download, load_data, validte_form

IMAGES = os.path.join('static', 'uploads')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = IMAGES
config = load_config()
keywords_class, text_class, liste_regex, nbr_mot_chunk = load_data(config)
plot_image = os.path.join(app.config['UPLOAD_FOLDER'], 'no_image.jpg')
file_json, file_txt = None, None

@app.route("/test")
def api_root():
    resp = jsonify(
        {u"statusCode": 200, u"status": "Up",
            u"message": u"Welcome to apply regex api"}
    )
    resp.status_code = 200
    return resp


@app.route('/')
def home():
    values = {}
    return render_template('index.html',
                           keywords_class=keywords_class,
                           text_class=text_class,
                           liste_regex=liste_regex,
                           nbr_mot_chunk=nbr_mot_chunk,
                           plot_image=plot_image, values=values)


@app.route('/', methods=['POST'])
def apply_regex():
    if request.method == "POST":
        valid = validte_form(request.form)
        plot_image = os.path.join(app.config['UPLOAD_FOLDER'], 'no_image.jpg')
        if not valid:
            return render_template('index.html',
                                   values=request.form,
                                   keywords_class=keywords_class,
                                   text_class=text_class,
                                   liste_regex=liste_regex,
                                   nbr_mot_chunk=nbr_mot_chunk,
                                   plot_image=plot_image)

        values = {}
        # get input values
        keywords_class_value = request.form.get('input_class')
        text_class_value = request.form.get('input_text_class')
        liste_regex_value = request.form.getlist('input_liste_regex')
        nbr_mot_chunk_value = int(request.form.get('input_nbr_mot_chunk'))

        # apply regex
        keywords_racisme_religion = liste_mots_cles(keywords_class_value)
        data = explore_regex(keywords_racisme_religion, liste_regex_value)
        value_ngrammes = ngrammes(text_class_value, nbr_mot_chunk_value)
        plot_image_name = plot_schema(value_ngrammes)
        plot_image = os.path.join(app.config['UPLOAD_FOLDER'], plot_image_name)
        file_json, file_txt = download(data)
        return render_template('index.html',
                               keywords_class=keywords_class,
                               text_class=text_class,
                               liste_regex=liste_regex,
                               nbr_mot_chunk=nbr_mot_chunk,
                               file_json=file_json,
                               file_txt=file_txt,
                               plot_image=plot_image, values=values)


@app.route('/download/<filename>/<type>')
def export(filename, type):
    file_path = f'./static/{type}/{filename}'
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
  app.run(debug=True)
