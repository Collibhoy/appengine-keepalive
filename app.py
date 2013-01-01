"""
appengine-keepalive
Copyright (C) 2012 Patrick Carey appengine-keepalive@wackwack.co.uk

A simple appengine app that pings a specified list of URLs on a regular
schedule (useful for tasks like keeping a single dyno heroku app from
spinning down).

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
"""

# stdlib imports
import datetime
import json
import logging
import webapp2

# third-party imports
from google.appengine.api import urlfetch


class KeepAliveHandler(webapp2.RequestHandler):

    """
    Request handler to send GET requests to a specified list of URLs
    """

    # list of URLs to ping on each cron run (this is most useful for
    # heroku apps with only one dyno as they get spun down when no
    # requests have been made)
    keepalive_urls = [
        'http://example-1.com',
        'http://example-2.com',
    ]

    def get(self):

        # new json object for response
        json_response = {}

        # loop over all keepalive urls
        for url in self.keepalive_urls:
            # ping the url and add results to response
            result = self.ping(url)
            json_response[url] = result
            # log result of urlfetch call
            logging.info('%s: %s' % (url, json.dumps(result)))

        # dump dict to JSON
        json_response = json.dumps(json_response)

        # construct and send response to user
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json_response)

    def ping(self, url):

        # timestamp at start of ping
        start_time = datetime.datetime.utcnow()

        # ping specified URL
        response = urlfetch.fetch(url, deadline=60)

        # timestamp at end of ping
        end_time = datetime.datetime.utcnow()
        # get timedelta for befora and after ping
        delta = end_time - start_time

        # build dict for response
        response_object = {}
        response_object['status'] = response.status_code
        response_object['duration'] = delta.seconds

        # return dict with ping results
        return response_object

# our main WSGI app
app = webapp2.WSGIApplication([('/', KeepAliveHandler)], debug=False)
