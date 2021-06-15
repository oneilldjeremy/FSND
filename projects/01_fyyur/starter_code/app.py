#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask, 
  render_template, 
  request, Response, 
  flash, 
  redirect, 
  url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm as Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

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

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  
  # I originally wanted to do this by getting a list of cities and states with query.distinct, but the current documentation online claimed this was deprecated. 
  # It seems like this would be much easier to implement with a method equivalent to SELECT distinct(city, state) FROM Venue.
  venues = Venue.query.all()
  cities_and_venues = []

  for venue in venues:
    city_already_included = False

    venue_info = {"id": venue.id, "name": venue.name, "num_upcoming_shows": 0}
    current_city = {"city": venue.city, "state": venue.state}

    upcoming_shows = Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()

    venue_info["num_upcoming_shows"] = upcoming_shows
    
    # This will go through each venue and check if the venue's city and state already exists. 
    # If it does, it will add the venue to that city and state.
    # If it doesn't, a new city and state will be created and the venue will be added as the first venue for that city/state.
    for i, city_with_venues in enumerate(cities_and_venues):
      if (venue.city == city_with_venues["city"] and venue.state == city_with_venues["state"]):
        city_already_included = True
        cities_and_venues[i]["venues"].append(venue_info)

    if (not city_already_included):
      current_city["venues"] = [venue_info]
      cities_and_venues.append(current_city)
    # Add calculation for num_upcoming_shows 

  return render_template('pages/venues.html', areas=cities_and_venues);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')

  # This will search the database for the search term in a case-insensitive manner.
  search_results = Venue.query.filter(Venue.name.ilike('%' + search_term + '%'))
  number_of_results = 0
  
  response = {"count": 0, "data": []}

  # This will gather the number of shows for each venue by checking the associated shows for the venue in the Show table.
  for venue in search_results:
    number_of_results += 1

    upcoming_shows = Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()

    response["data"].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": upcoming_shows
    })
  
  response["count"] = number_of_results

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  past_shows = []
  upcoming_shows = []
  
  venue = Venue.query.get(venue_id)

  # The __dict__ command creates a dictionary with the instance variable name as the key and it's value as the associated key value.
  venue_info = venue.__dict__

  # Use the joined table Show to get information about shows associated with this venue.
  for show in venue.show:
    temp_show = {"artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
      }

    # Add show to upcoming shows if the show is in the future, otherwise, add to past shows
    if show.start_time > datetime.now():
      upcoming_shows.append(temp_show)
    else:
      past_shows.append(temp_show)

  venue_info["upcoming_shows_count"] = len(upcoming_shows)
  venue_info["upcoming_shows"] = upcoming_shows
  venue_info["past_shows_count"] = len(past_shows)
  venue_info["past_shows"] = past_shows

  return render_template('pages/show_venue.html', venue=venue_info)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      # Create a new Venue instance with form results.
      venue = Venue()
      form.populate_obj(venue)

      db.session.add(venue)
      db.session.commit()
    except():
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
  
    
  return render_template('pages/home.html')
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
 
  error = False
  try:
      venue = Venue.query.get(venue_id)
      
      db.session.delete(venue)
      db.session.commit()
  except():
      db.session.rollback()
      error = True
  finally:
      db.session.close()
  if error:
      abort(500)
  else:
      return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term')

  search_results = Artist.query.filter(Artist.name.ilike('%' + search_term + '%'))
  number_of_results = 0
  
  response = {"count": 0, "data": []}

  for artist in search_results:
    number_of_results += 1

    upcoming_shows = Show.query.filter(Show.artist_id == artist.id, Show.start_time > datetime.now()).count()

    response["data"].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": upcoming_shows
    })
  
  response["count"] = number_of_results
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  past_shows = []
  upcoming_shows = []
  
  artist = Artist.query.get(artist_id)

  # The __dict__ command creates a dictionary with the instance variable name as the key and it's value as the associated key value.
  artist_info = artist.__dict__

  # Use the joined table Show to get information about shows associated with this venue.
  for show in artist.show:
    temp_show = {"venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
      }

    # Add show to upcoming shows if the show is in the future, otherwise, add to past shows
    if show.start_time > datetime.now():
      upcoming_shows.append(temp_show)
    else:
      past_shows.append(temp_show)

  artist_info["upcoming_shows_count"] = len(upcoming_shows)
  artist_info["upcoming_shows"] = upcoming_shows
  artist_info["past_shows_count"] = len(past_shows)
  artist_info["past_shows"] = past_shows
  
  return render_template('pages/show_artist.html', artist=artist_info)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  
  # Get artist's information from database and autopopulate to form for editing.
  form = ArtistForm(obj=artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      artist = Artist.query.get(artist_id)
      form.populate_obj(artist)

      db.session.commit()
    except():
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
      redirect_url = 'show_artist'
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    redirect_url = 'edit_artist_submission'
  return redirect(url_for(redirect_url, artist_id=artist_id))
 
  
  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  
  # Get venue's information from database and autopopulate to form for editing.
  form = VenueForm(obj=venue)
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      venue = Venue.query.get(venue_id)
      form.populate_obj(venue)

      db.session.commit()
    except():
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
      redirect_url = 'show_venue'
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    redirect_url = 'edit_venue_submission'
  return redirect(url_for(redirect_url, venue_id=venue_id))
  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form, meta={'csrf': False})
  if form.validate():
    try:
      # Create a new Venue instance with values entered in form.
      artist = Artist()
      form.populate_obj(artist)

      db.session.add(artist)
      db.session.commit()
    except():
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
      

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows_info=[]

  shows = Show.query.all()

  for show in shows:
    shows_info.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    })

  return render_template('pages/shows.html', shows=shows_info)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form, meta={'csfr': False})
  if form.validate():
    try:
      # Get form results from form and create a new Venue instance.
      show = Show()
      form.populate_obj(show)

      db.session.add(show)
      db.session.commit()

    except():
      flash('An error occurred. Show could not be listed.')
      db.session.rollback()
      error = True
      print(sys.exc_info())
    finally:
      db.session.close()
      flash('Show was successfully listed!')
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    
  return render_template('pages/home.html')

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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
