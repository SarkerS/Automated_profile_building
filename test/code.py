import web
import config
import facebook_web
import json
from web import form

urls = (
    '/', 'Index',
    '/search', 'Search'
)

render = web.template.render('templates/', cache=config.cache)

class Index:
    def GET(self):
        return render.index()

class Search:
    def GET(self):
        user_data = web.input()
        query = user_data.query
        people = facebook_web.search(query)

        #print(json.dumps(people, sort_keys=True, indent=3))
        return json.dumps(people)
    
if __name__ == "__main__":
    app = web.application(urls, globals())
    app.internalerror = web.debugerror
    app.run()
