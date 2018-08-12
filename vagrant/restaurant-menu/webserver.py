from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurants = session.query(Restaurant).all()

                message = ""
                message += "<html><body>"
                message += "<h2><a href='/restaurants/new'>Add a new restaurant</a></h2>"
                message += "<h1>List of Restaurants</h1>"
                message += "<ul>"
                for r in restaurants:
                    message += "<li>{0}".format(r.name)
                    message += " <a href='restaurants/{0}/edit'>Edit</a>".format(
                        r.id)
                    message += " <a href='restaurants/{0}/delete'>Delete</a>".format(
                        r.id)
                    message += "</li>"
                message += "</ul>"
                message += "</body></html>"
                self.wfile.write(message)
                return
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                message = ""
                message += "<html><body>"
                message += "<h2>Add a new restaurant</h2>"
                message += "<form method='POST' enctype='multipart/form-data' action='restaurants/new'>"
                message += "<input name='newRestaurantName' type='text' placeholder='New restaurant name'>"
                message += "<input type='submit' value='Create'></form>"
                message += "</body></html>"
                self.wfile.write(message)
            if self.path.endswith("/edit"):
                restaurantId = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(
                    id=restaurantId).one_or_none()

                if restaurant != None:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    message = ""
                    message += "<html><body>"
                    message += "<h2>{0}</h2>".format(restaurant.name)
                    message += "<form method='POST' enctype='multipart/form-data' action='restaurants/{0}/edit'>".format(
                        restaurant.id)
                    message += "<input name='restaurantName' type='text' placeholder='{0}'>".format(
                        restaurant.name)
                    message += "<input type='submit' value='Rename'>"
                    message += "</form>"
                    message += "</body></html>"
                    self.wfile.write(message)

            if self.path.endswith("/delete"):
                restaurantId = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(
                    id=restaurantId).one_or_none()

                if restaurant != None:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    message = ""
                    message += "<html><body>"
                    message += "<h2>Are you sure you want to delete {0}?</h2>".format(
                        restaurant.name)
                    message += "<form method='POST' enctype='multipart/form-data' action='restaurants/{0}/delete'>".format(
                        restaurant.id)
                    message += "<input type='submit' value='Delete'>"
                    message += "</form>"
                    message += "</body></html>"
                    self.wfile.write(message)

        except IOError:
            self.send_error(404, "File Not Found " + self.path)

    def do_POST(self):
        if self.path.endswith("/restaurants/new"):
            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('newRestaurantName')

                newRestaurant = Restaurant(name=messagecontent[0])
                session.add(newRestaurant)
                session.commit()

                self.send_response(303)
                self.send_header('Location', '/restaurants')
                self.end_headers()

        if self.path.endswith("/edit"):
            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('restaurantName')

                restaurantId = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(
                    id=restaurantId).one_or_none()

                if restaurant != None:
                    restaurant.name = messagecontent[0]
                    session.add(restaurant)
                    session.commit()

                    self.send_response(303)
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
        if self.path.endswith("/delete"):
            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                #messagecontent = fields.get('restaurantName')

                restaurantId = self.path.split("/")[2]
                restaurant = session.query(Restaurant).filter_by(
                    id=restaurantId).one_or_none()

                if restaurant != None:
                    session.delete(restaurant)
                    session.commit()

                    self.send_response(303)
                    self.send_header('Location', '/restaurants')
                    self.end_headers()


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print("Web server running on port" + str(port))
        server.serve_forever()
    except KeyboardInterrupt:
        print("^C entered, stopping web server...")
        server.socket.close()


if __name__ == '__main__':
    main()
