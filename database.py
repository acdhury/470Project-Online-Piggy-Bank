from sqlalchemy import create_engine

# MySQL Connection URL
DATABASE_URL = "mysql+mysqlconnector://username:password@localhost/db_name"

# SQLAlchemy engine
engine = create_engine(DATABASE_URL)
