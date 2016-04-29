import datetime as dt
from io import BytesIO

from flask import Flask, jsonify, render_template, request, send_file

from cal.schema import db, Event, User, Tag, EventTag  # noqa
from cal.ics import to_icalendar

# Initialize the app
app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)

@app.before_request
def before_request():
    """ Do something before every request """
    if request.path != '/favicon.ico':
        app.logger.info(request.path)
    return

@app.after_request
def after_request(resp):
    """ Do something after every request """
    return resp


@app.errorhandler(404)
def page_not_found(e):
    return "Page not found"


@app.route('/')
def home():
    return render_template('index.html')
    
# select t.tag, et.ed_weight from tag t inner join event_tag et on t.id = et.tag_id where et.event_id = 100;
@app.route('/event_tags/<int:eventid>')
def get_one_event(eventid):
    results = db.session.query(Tag, EventTag).\
    filter(Tag.id==EventTag.tag_id).\
    filter(EventTag.event_id==eventid).\
    all()
    
    j_tags = {}
    for t, et in results:
        j_tags[t.tag] = et.ed_weight
        
    event = Event.query.filter(Event.id==eventid).first()
    j_result = {"description": event.description, "tags": j_tags}
    
    return jsonify(data=j_result)

@app.route("/events/<int:year>/<int:month>/<int:day>")
def events(year, month, day):
    search = request.args.get("search")
    if search is not None:
        events = Event.query.search(search)
    else:
        events = Event.query

    start = dt.date(year, month, day)
    start -= dt.timedelta(days=start.isoweekday() % 7)  # Sunday 7 -> 0
    end = start + dt.timedelta(weeks=1)

    events = events.filter((start <= Event.start) | (Event.end >= start)) \
                   .filter((Event.start < end) | (Event.end < end)) \
                   .order_by(Event.start, Event.end, Event.name)
    events = [event.to_json() for event in events]
    return jsonify(data=events)


@app.route("/users/<int:year>/<int:month>/<int:day>")
def users(year, month, day):
    start = dt.date(year, month, day)
    start -= dt.timedelta(days=start.isoweekday() % 7)  # Sunday 7 -> 0
    end = start + dt.timedelta(weeks=1)

    events = Event.query
    events = events.filter((start <= Event.start) | (Event.end >= start)) \
                   .filter((Event.start < end) | (Event.end < end))
    users = {event.user for event in events}    # use set to make users unique
    users = [user.to_json() for user in sorted(users, key=lambda u: u.name)]
    return jsonify(data=users)


@app.route("/ics/", methods=["GET"])
def to_ics():
    # get list of ids from GET request
    event_ids = request.args.getlist("event_ids[]", type=int)
    events = Event.query.filter(Event.id.in_(event_ids))

    return send_file(BytesIO(to_icalendar(events)), mimetype="text/calendar",
                     as_attachment=True, attachment_filename="calendar.ics")
