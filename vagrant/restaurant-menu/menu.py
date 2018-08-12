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

restaurants = session.query(Restaurant).all()

print('###Restaurants###')
#for r in restaurants:
    #print(r.name)

print('###Menu###')
items = session.query(MenuItem).all()
#for item in items:
    #print(item.name)

veggieBurgers = session.query(MenuItem).filter_by(name = 'Veggie Burger')
for burger in veggieBurgers:
    print(str(burger.id))
    print(str(burger.price))
    print(burger.restaurant.name)
    print('\n')

urbanBurger = session.query(MenuItem).filter_by(id = 1).one()
urbanBurger.price = '$2.99'
session.add(urbanBurger)
session.commit()

veggieBurgers = session.query(MenuItem).filter_by(name = 'Veggie Burger')
for burger in veggieBurgers:
    print(str(burger.id))
    print(str(burger.price))
    print(burger.restaurant.name)
    print('\n')