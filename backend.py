# backend.py
# openeventdatabase

import falcon
import psycopg2
import uuid
import json

class StatsResource(object):
    def on_get(self, req, resp):
        db = psycopg2.connect("dbname=oedb")
        cur = db.cursor()
        cur.execute("SELECT count(*) from events;")
        stat = cur.fetchone()
        count_events = stat[0]
        cur.close()
        db.close()

        resp.body = """{"events_count":%s}""" % (count_events)
        resp.set_header('X-Powered-By', 'OpenEventDatabase')
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Headers', 'X-Requested-With')
        resp.status = falcon.HTTP_200

class EventResource(object):
    def on_post(self, req, resp):
        # get request body payload (json)
        body = req.stream.read().decode('utf-8')
        j=json.loads(body)
        
        # connect to db and insert
        db = psycopg2.connect("dbname=oedb")
        cur = db.cursor()
        cur.execute("""INSERT INTO events ( events_type, events_what, events_when, events_tags) VALUES (%s, %s, %s, %s) RETURNING events_id;""",(j['type'],j['what'],j['when'], body))
        # get newly created event id
        e = cur.fetchone()
        db.commit()
        cur.close()
        db.close()
        # send back to client
        resp.body = """{"id":"%s"}""" % (e[0])
        resp.set_header('X-Powered-By', 'OpenEventDatabase')
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Headers', 'X-Requested-With')
        resp.status = falcon.HTTP_200


# falcon.API instances are callable WSGI apps
app = falcon.API()

# Resources are represented by long-lived class instances
event = EventResource()
stats = StatsResource()

# things will handle all requests to the matching URL path
app.add_route('/event', event)  # handle single event requests
app.add_route('/stats', stats)

