import web

search_name = 'Wayne'

DB = web.database(dbn='sqlite', db='sql/database.db')
DB.printing = False
cache = False

NUM_TOP_TWEETS = 3
CRAWL_TIMEOUT = 1 # seconds
MAX_RESULTS_PAGES = 6
