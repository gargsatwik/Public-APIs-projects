import flask
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os


API_KEY = os.environ.get('API_KEY')
API_READ_ACCESS_TOKEN = os.environ.get('API_READ_ACCESS_TOKEN')


app = Flask(__name__)
# app.config['SECRET KEY'] = os.environ.get('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DB_URI', 'sqlite:///project.db')
app.secret_key = "some-random-text"
bootstrap = Bootstrap5(app)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Movie(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    description: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    rating: Mapped[float] = mapped_column(Float, unique=False, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, unique=True, nullable=True)
    review: Mapped[str] = mapped_column(String(250), unique=False, nullable=True)
    image_url: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)


class FormToEdit(FlaskForm):
    new_rating = StringField("new_rating", validators=[DataRequired()])
    new_review = StringField("new_review", validators=[DataRequired()])
    submit = SubmitField("Submit")


class FormToAdd(FlaskForm):
    movie_name = StringField("movie name", validators=[DataRequired()])
    submit = SubmitField("Submit")


# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's"
#                 "sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to"
#                 " a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     image_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )

with app.app_context():
    db.create_all()
    # db.session.add(new_movie)                       TO INITIALIZE THE DATABASE
    db.session.commit()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating.desc()).all()
    movie_list = []
    i = 1
    for movie in all_movies:
        movie_data = {
            'id': movie.id,
            'description': movie.description,
            'review': movie.review,
            'rating': movie.rating,
            'ranking': i,
            'image_url': movie.image_url,
            'title': movie.title,
            'year': movie.year,
        }
        i += 1
        movie_list.append(movie_data)
    flask.jsonify(movie_list)
    return render_template("index.html", movies=movie_list)


@app.route("/update/<num>", methods=["GET", "POST"])
def update(num):
    form = FormToEdit()
    movie = Movie.query.get(num)
    if request.method == "GET":
        return render_template("edit.html", form=form)
    elif request.method == "POST" and form.validate_on_submit():
        if movie:
            movie.rating = form.new_rating.data
            movie.review = form.new_review.data
            db.session.commit()
            return redirect(url_for("home"))


@app.route("/delete/<num>", methods=["GET", "POST"])
def delete(num):
    movie = Movie.query.filter_by(id=int(num)).first()
    if movie:
        db.session.delete(movie)
        db.session.commit()
    return redirect(url_for("home"))


@app.route("/add-movie", methods=["GET", "POST"])
def add_movie():
    form = FormToAdd()
    if request.method == "GET":
        return render_template("add.html", form=form)
    elif request.method == "POST":
        title = form.movie_name.data
        response = requests.get(url="https://api.themoviedb.org/3/search/movie",
                                params={"api_key": API_KEY, "query": title, "adult": True}).json()["results"]
        return render_template("select.html", data=response)


@app.route("/add-to-database/<num>", methods=["GET", "PUTS"])
def add_to_database(num):
    response = requests.get(url=f"https://api.themoviedb.org/3/movie/{num}?api_key={API_KEY}").json()
    title = response['title']
    description = response['overview']
    year = response['release_date']
    image_url = "https://image.tmdb.org/t/p/w300" + response['poster_path']
    with app.app_context():
        db.session.add(Movie(title=title, description=description, year=year, image_url=image_url))
        db.session.commit()
    all_movies = Movie.query.all()
    num_ = 0
    for movie in all_movies:
        if movie.title == title:
            num_ = movie.id
    return redirect(url_for("update", num=num_))


if __name__ == '__main__':
    app.run(debug=True)
