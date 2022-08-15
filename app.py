#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import re
import json
import dateutil.parser
import babel
from datetime import datetime
from flask import Flask, copy_current_request_context, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from model import *
# TODO: connect to a local postgresql database
# setup_db(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

def format_string(string):
  return re.sub(r'[{}]', '', string)

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  recent_venues = Venue.query.order_by(desc(Venue.id)).limit(10)
  recent_artists = Artist.query.order_by(desc(Artist.id)).limit(10)
  db.session.close()
  return render_template('pages/home.html', venues=recent_venues, artists=recent_artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  venues = Venue.query.all()
  # List to hold all shows displayed in groups based on city and state
  data = []
  city_state = []
  # Put distinct city, state in the city_state list and add venues to those city-state groups
  for i in venues:
    obj = {}
    obj['city'] = i.city
    obj['state'] = i.state
    obj['venues'] = Venue.query.filter_by(city=i.city, state=i.state).all()
    if f"{obj['city']}, {obj['state']}" not in city_state:
      city_state.append(f"{obj['city']}, {obj['state']}")
      data.append(obj)
    else:
      continue
  db.session.close()
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  response={
    "count": len(venues),
    "data": [{
      "id": i.id,
      "name": i.name,
      "num_upcoming_shows": len(Show.query.filter(Show.venue_id == i.id, Show.start_time > datetime.now()).all()),
    } for i in venues]
  }
  db.session.close()
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  # Ouery the show table to get all shows for the venue id both past and upcoming
  upcoming_shows = Show.query.filter(Show.venue_id==venue_id, Show.start_time > datetime.now()).all()
  past_shows = Show.query.filter(Show.venue_id==venue_id, Show.start_time < datetime.now()).all()
  # Create a list of dictionaries containing details of the show showing the artist details using the artist relationship on the Show table for both past and upcoming shows
  past = [{
      "artist_id": pa.artist_id,
      "artist_name": pa.artist.name,
      "artist_image_link": pa.artist.image_link,
      "start_time": str(pa.start_time)
    } for pa in past_shows]

  upcoming = [{
      "artist_id": up.artist_id,
      "artist_name": up.artist.name,
      "artist_image_link": up.artist.image_link,
      "start_time": str(up.start_time)
    } for up in upcoming_shows]

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": format_string(venue.genres).split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_desc,
    "image_link": venue.image_link,
    "past_shows": past,
    "upcoming_shows": upcoming,
    "past_shows_count": len(past),
    "upcoming_shows_count": len(upcoming),
  }
  db.session.close()
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  # Retrieve the form data
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form['genres']
  facebook = request.form['facebook_link']
  image = request.form['image_link']
  website = request.form['website_link']
  seek_talent = True if request.form['seeking_talent'] == 'y' else False
  seek_desc = request.form['seeking_description']
  # name = form.name.data
  # city = form.city.data
  # address = form.address.data
  # state = form.state.data
  # phone = form.phone.data
  # image = form.image_link.data
  # genres = form.genres.data
  # facebook = form.facebook_link.data
  # website = form.website_link.data
  # seek_talent = form.seeking_talent.data
  # seek_desc = form.seeking_description.data
  try:
    new_venue = Venue(name=name, city=city, address=address, state=state, phone=phone, image_link=image, genres=genres, facebook_link=facebook, website_link=website, seeking_talent=seek_talent, seeking_desc=seek_desc)
    db.session.add(new_venue)
    db.session.commit()
    db.session.close()
    flash('Venue ' + name + ' was successfully listed!')
    return redirect(url_for('index'))
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + name + ' could not be listed.')
    return redirect(url_for('index'))
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return jsonify({ 'success': True })
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  db.session.close()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  response={
    "count": len(artists),
    "data": [{
      "id": i.id,
      "name": i.name,
      "num_upcoming_shows": len(Show.query.filter(Show.artist_id == i.id, Show.start_time > datetime.now()).all()),
    } for i in artists]
  }
  db.session.close()
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  db.session.close()
  # Query the Show table for all shows involving the artist
  upcoming_shows = Show.query.filter(Show.artist_id==artist_id, Show.start_time > datetime.now()).all()
  past_shows = Show.query.filter(Show.artist_id==artist_id, Show.start_time < datetime.now()).all()
  # Create a list of dictionaries containing details of the show showing the venue details using the venue relationship on the Show table for both past and upcoming shows
  past = [{
      "venue_id": pa.venue_id,
      "venue_name": pa.venue.name,
      "venue_image_link": pa.venue.image_link,
      "start_time": str(pa.start_time)
    } for pa in past_shows]

  upcoming = [{
      "venue_id": up.venue_id,
      "venue_name": up.venue.name,
      "venue_image_link": up.venue.image_link,
      "start_time": str(up.start_time)
    } for up in upcoming_shows]

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": format_string(artist.genres).split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_desc,
    "image_link": artist.image_link,
    "past_shows": past,
    "upcoming_shows": upcoming,
    "past_shows_count": len(past),
    "upcoming_shows_count": len(upcoming),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.default = artist.name
  form.city.default = artist.city
  form.state.default = artist.state
  form.phone.default = artist.phone
  form.genres.default = artist.genres
  form.image_link.default = artist.image_link
  form.website_link.default = artist.website_link
  form.facebook_link.default = artist.facebook_link
  form.seeking_venue.default = artist.seeking_venue
  form.seeking_description.default = artist.seeking_desc
  form.process()
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  artist.name = form.name.data
  artist.city = form.city.data
  artist.state = form.state.data
  artist.phone = form.phone.data
  artist.image_link = form.image_link.data
  artist.genres = form.genres.data
  artist.facebook_link = form.facebook_link.data
  artist.website_link = form.website_link.data
  artist.seeking_venue = form.seeking_venue.data
  artist.seeking_desc = form.seeking_description.data
  db.session.commit()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.default = venue.name
  form.city.default = venue.city
  form.state.default = venue.state
  form.address.default = venue.address
  form.phone.default = venue.phone
  form.genres.default = venue.genres
  form.image_link.default = venue.image_link
  form.website_link.default = venue.website_link
  form.facebook_link.default = venue.facebook_link
  form.seeking_talent.default = venue.seeking_talent
  form.seeking_description.default = venue.seeking_desc
  form.process()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue.name = form.name.data
  venue.city = form.city.data
  venue.state = form.state.data
  venue.address = form.address.data
  venue.phone = form.phone.data
  venue.image_link = form.image_link.data
  venue.genres = form.genres.data
  venue.facebook_link = form.facebook_link.data
  venue.website_link = form.website_link.data
  venue.seeking_talent = form.seeking_talent.data
  venue.seeking_desc = form.seeking_description.data
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))
 
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  name = form.name.data
  city = form.city.data
  state = form.state.data
  phone = form.phone.data
  image = form.image_link.data
  genres = form.genres.data
  facebook = form.facebook_link.data
  website = form.website_link.data
  seek_venue = form.seeking_venue.data
  seek_desc = form.seeking_description.data
  try:
    new_artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image, genres=genres, facebook_link=facebook, website_link=website, seeking_venue=seek_venue, seeking_desc=seek_desc)
    db.session.add(new_artist)
    db.session.commit()
    db.session.close()
    flash('Artist ' + name + ' was successfully listed!')
    return redirect(url_for('index'))
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + name + ' could not be listed.')
    return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.filter(Show.start_time > datetime.now()).all()
  data = [{"venue_id": s.venue_id, "venue_name": s.venue.name, "artist_id": s.artist_id, "artist_name": s.artist.name, "artist_image_link": s.artist.image_link, "start_time": str(s.start_time)} for s in shows]
  db.session.close()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  artist_id = form.artist_id.data
  venue_id = form.venue_id.data
  start_time = form.start_time.data 
  try:
    new_show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
    return redirect(url_for('index'))
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    return redirect(url_for('index'))
  finally:
    db.session.close()
  
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
