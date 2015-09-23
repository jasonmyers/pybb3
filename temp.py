from pony.orm import *
from pony.orm.core import sql_debug
sql_debug(True)

db = Database('sqlite', ':memory:')

class Topic(db.Entity):
    pass

db.generate_mapping(create_tables=True)

with db_session:
    topic = Topic()

with db_session:
    t = Topic[1]

