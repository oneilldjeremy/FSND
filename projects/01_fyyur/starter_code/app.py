#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import db, Venue, Artist, Show
migrate = Migrate(app,db)

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
  upcoming_shows = {}
  venues_upcoming_shows_count =  0
  
  venue = Venue.query.get(venue_id)

  # The __dict__ command creates a dictionary with the instance variable name as the key and it's value as the associated key value.
  venue_info = venue.__dict__
  venue_info["upcoming_shows"] = []
  venue_info["past_shows"] = []

  # Query the database to find associated upcoming shows.
  venues_upcoming_shows_count = Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()

  venue_info["upcoming_shows_count"] = venues_upcoming_shows_count

  # Append information about each upcoming show 
  if (venues_upcoming_shows_count > 0):
    venues_upcoming_shows = Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).all()
  
    for show in venues_upcoming_shows:

      venue_info["upcoming_shows"].append({"artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
      })

  # Query the database to find associated past shows.
  venues_past_shows_count = Show.query.filter(Show.venue_id == venue.id, Show.start_time <= datetime.now()).count()

  venue_info["past_shows_count"] = venues_past_shows_count
  
  # Append information about each past show 
  if (venues_past_shows_count > 0):
    venues_past_shows = Show.query.filter(Show.venue_id == venue.id, Show.start_time <= datetime.now()).all()
  
    for show in venues_past_shows:

      venue_info["past_shows"].append({"artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
      })

  return render_template('pages/show_venue.html', venue=venue_info)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    # Get form results from from and create variables to use to create a new Venue instance.
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    
    seeking_description = request.form['seeking_description']
    genres = request.form.getlist('genres'), 

    # Convert the 'y'/'n' response for the "Seeking Talent" field to a Python boolean.
    if ('seeking_talent' in request.form):
      if (request.form['seeking_talent'] == 'y'):
        seeking_talent = True
      else:
        seeking_talent = False
    else:
      seeking_talent = False

    # Create new Venue
    venue = Venue(name=name, city=city,state=state,address=address,phone=phone,image_link=image_link,facebook_link=facebook_link,website=website_link,seeking_talent=seeking_talent,seeking_description=seeking_description,genres=genres)
    db.session.add(venue)
    db.session.commit()
    #body['id'] = venue.id
    
  except():
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
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
  upcoming_shows = {}
  artists_upcoming_shows_count =  0
  
  artist = Artist.query.get(artist_id)

  artist_info = artist.__dict__
  artist_info["upcoming_shows"] = []
  artist_info["past_shows"] = []

  artists_upcoming_shows_count = Show.query.filter(Show.artist_id == artist.id, Show.start_time > datetime.now()).count()

  artist_info["upcoming_shows_count"] = artists_upcoming_shows_count

  # Get information about artist's upcoming shows and append to list of upcoming shows
  if (artists_upcoming_shows_count > 0):
    artists_upcoming_shows = Show.query.filter(Show.venue_id == artist.id, Show.start_time > datetime.now()).all()
  
    for show in artists_upcoming_shows:

      artist_info["upcoming_shows"].append({"venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
      })

  artists_past_shows_count = Show.query.filter(Show.artist_id == artist.id, Show.start_time <= datetime.now()).count()

  artist_info["past_shows_count"] = artists_past_shows_count
  
  # Get information about artist's past shows and append to list of upcoming shows
  if (artists_past_shows_count > 0):
    artists_past_shows = Show.query.filter(Show.artist_id == artist.id, Show.start_time <= datetime.now()).all()
  
    for show in artists_past_shows:

      artist_info["past_shows"].append({"venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
      })
  
  return render_template('pages/show_artist.html', artist=artist_info)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  
  # Get artist's information from database and autopopulate to form for editing.
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website
  form.seeking_description.data = artist.seeking_description
  form.genres.data = artist.genres[0]
  form.seeking_venue.data = artist.seeking_venue

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  error = False
  try:
    # Get form results and update artist information
    artist = Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website_link = request.form['website_link']
    
    artist.seeking_description = request.form['seeking_description']
    artist.genres = request.form.getlist('genres'), 

    if ('seeking_venue' in request.form):
      if (request.form['seeking_venue'] == 'y'):
        artist.seeking_venue = True
      else:
        artist.seeking_venue = False
    else:
      artist.seeking_venue = False

    db.session.commit()
    
    
  except():
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))
  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  
  # Get venue's information from database and autopopulate to form for editing.
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website
  form.seeking_description.data = venue.seeking_description
  form.genres.data = venue.genres[0]
  form.seeking_talent.data = venue.seeking_talent
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    
    # Get form results and update artist information
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    
    venue.seeking_description = request.form['seeking_description']
    venue.genres = request.form.getlist('genres'), 

    if ('seeking_talent' in request.form):
      if (request.form['seeking_talent'] == 'y'):
        venue.seeking_talent = True
      else:
        venue.seeking_talent = False
    else:
      venue.seeking_talent = False

    db.session.commit()
    
  except():
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return redirect(url_for('show_venue', venue_id=venue_id))
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  
  error = False
  try:
    # Get form results and capture values to create new venue.
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    seeking_description = request.form['seeking_description']
    genres = request.form.getlist('genres'), 

    if ('seeking_venue' in request.form):
      if (request.form['seeking_venue'] == 'y'):
        seeking_venue = True
      else:
        seeking_venue = False
    else:
      seeking_venue = False

    # Create new Artist
    artist = Artist(name=name, city=city,state=state,phone=phone,image_link=image_link,facebook_link=facebook_link,website=website_link,seeking_venue=seeking_venue,seeking_description=seeking_description,genres=genres)
    db.session.add(artist)
    db.session.commit()
    #body['id'] = venue.id
    
  except():
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

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
  error = False
  try:
    # Capture form results to create a new show instance.
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    # Create new Show
    show = Show(start_time=start_time,artist_id=artist_id,venue_id=venue_id)
    db.session.add(show)
    db.session.commit()

  except():
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    flash('Show was successfully listed!')
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
