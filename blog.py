import os

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class BaseHandler(webapp2.RequestHandler):
   
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class Post(db.Model):
	subject = db.StringProperty( required = True)
	content = db.TextProperty( required = True)
	created = db.DateTimeProperty( auto_now_add = True)

class NewPost(BaseHandler):

	def render_page(self, error="", subject="", content=""):
		self.render('newpost.html', error=error, subject=subject, content=content)

	def get(self):
		self.render_page()

	def post(self):
		subject = self.request.get('subject')
		content = self.request.get('content')
		if subject and content:
			p = Post(subject=subject, content=content)
			p.put()
			self.redirect('/'+str(p.key().id()) ) #do something
		else:
			error = "Please complete all fields"
			self.render_page(error=error, subject=subject, content=content)

class MainPage(BaseHandler):

	def render_front(self):
		posts = db.GqlQuery('SELECT * FROM Post ORDER BY created DESC')
		self.render('main.html',posts=posts)

	def get(self):
		self.render_front()

class PermaLink(BaseHandler):

	def get(self, post_id):
		post = Post.get_by_id(long(post_id))
		if post:
			self.render('permalink.html',post=post)
		else:
			self.response.out.write("Post does not exit")

class TestPage(BaseHandler):

	def get(self):
		#p = Post(subject = 'First Post', content = 'It works!')
		#p.put()
		posts = db.GqlQuery('SELECT * FROM Post')
		#query = datamodel.Post().all()
		for result in posts:
		    self.response.out.write(result.key().id())
		    self.response.out.write('\n')
		#self.render('permalink.html', subject=subject, content=content)

application = webapp2.WSGIApplication([
		('/', MainPage),('/newpost', NewPost),(r'/(\d+)', PermaLink),
		 ('/test', TestPage)
	],	debug=True)
