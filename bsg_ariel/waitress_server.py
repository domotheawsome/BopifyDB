from waitress import serve
from webapp import webapp
import app1
serve(app1.webapp, host='0.0.0.0', port=8080)