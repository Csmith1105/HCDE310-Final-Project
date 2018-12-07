import webapp2, urllib, urllib2, webbrowser, json
import jinja2

import os
import logging

EVENTFUL_KEY = 'v6BJKNJCtjRkbz6d'

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template_values={}
        template_values['page_title']="Event Search"
        template = JINJA_ENVIRONMENT.get_template('searchform.html')
        self.response.write(template.render(template_values))

def safeGet(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        print 'The server couln\'t fulfill the request.'
        print 'Error code: ', e.code
    except urllib2.URLError, e:
        print 'We failed to reach a server'
        print 'Reason: ', e.reason
    return None


def eventfulREST(baseurl = 'http://api.eventful.com/json/events/search',
                 api_key = EVENTFUL_KEY,
                 params = {}):
    params['app_key'] = api_key
    url = baseurl + "?" + urllib.urlencode(params)
    print("Print in url in eventfulREST")
    print(url)
    safeurl = safeGet(url)
    return safeurl

# calls to the eventfulREST, recieves the JSON data and returns a list of events
def get_eds(keywords="books", location="Seattle", date="Next Week", n=20):
    params = {'keywords': keywords, 'location': location, 'date': date, 'page_size': n}

    data_retrieved = eventfulREST(params=params)
    if (data_retrieved != None):
        data_read = data_retrieved.read()
        data_load = json.loads(data_read)
        event_list = data_load['events']['event']
        return event_list
    else:
        return None

# creates Event object
# string method
class Event:
    def __init__(self, eventdict):

        self.title = eventdict['title']
        self.venue = eventdict['venue_name']
        self.address = eventdict['venue_address']
        self.city = eventdict['city_name']
        self.zip = eventdict['postal_code']


        # TODO - figure out how to convert ascii to string
        if 'description' in eventdict:
            self.description = eventdict['description']
        else:
            self.description = None

        if eventdict['performers'] != None:
            self.performer = eventdict['performers']['performer']['name']
        else:
            self.performer = None

        if eventdict['image'] != None:
            if 'medium' in eventdict['image']:
                self.imageURL = eventdict['image']['medium']
        else:
            self.imageURL = None


    def __str__(self):

        return self.title + "\n" + self.venue + "\n" + self.address + "\n" + self.city + "\n"


class ResultsHandler(webapp2.RequestHandler):
    def post(self):
        vals = {}
        date = self.request.get('date')

        vals['page_title'] = "Events happening " + date

        if date:
            vals['date'] = date
            events = [Event(ed) for ed in get_eds(date)]
            events_print = [event.__str__() for event in events]
            vals['events_print'] = events_print

            template = JINJA_ENVIRONMENT.get_template('searchresults.html')
            self.response.write(template.render(vals))
        else:
            template = JINJA_ENVIRONMENT.get_template('searchform.html')
            self.response.write(template.render(vals))


application = webapp2.WSGIApplication([ \
    ('/results', ResultsHandler),
    ('/.*', MainHandler)
],
    debug=True)

print("NO parameters:")
edl_no_params = get_eds()
print(len(edl_no_params))
eventlist_noparams = [Event(ed) for ed in edl_no_params]
for event in eventlist_noparams[:3]:
    print(event)

print("WITH parameters:")
edl_params = get_eds(keywords="movies", location="San Francisco", date="Future", n=10)
print(len(edl_params))
eventlist_params = [Event(ed) for ed in edl_params]
for event in eventlist_params[:3]:
    print(event)


