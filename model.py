#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
import os
from app import db

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
database_name = 'trivia'

database_path = "postgresql://{}:{}@{}/{}".format(
    DB_USER, DB_PASSWORD, DB_HOST, DB_NAME
)

def setup_db(app, database_path=database_path):
  # app.config["SQLALCHEMY_DATABASE_URI"] = database_path
  app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://nnwsixatdsfgfv:df154d2383570e2d8eab0ef8a3f1edb7f34290e6bdbd8f72d97d759ebf0e875a@ec2-44-209-186-51.compute-1.amazonaws.com:5432/d2h2dl7orvp1o0'
  app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
  db.app = app
  db.init_app(app)
  db.create_all()

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_desc = db.Column(db.String(240))
    shows = db.relationship('Show', back_populates ='venue', cascade="delete, delete-orphan")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_desc = db.Column(db.String(240))
    shows = db.relationship('Show', back_populates ='artist', cascade="delete, delete-orphan")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer(), db.ForeignKey("Venue.id"))
  artist_id = db.Column(db.Integer(), db.ForeignKey("Artist.id"))
  start_time = db.Column(db.DateTime())
  venue = db.relationship('Venue', back_populates ='shows')
  artist = db.relationship('Artist', back_populates ='shows')
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
