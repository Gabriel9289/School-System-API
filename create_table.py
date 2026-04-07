from database import Base,engine


Base.metadata.create_all(bind=engine)
print("tables created")





"""
postgres=# \c school_system
psql (18.3, server 16.13)
You are now connected to database "school_system" as user "postgres".
school_system=# \dt
                List of tables
 Schema |       Name       | Type  |  Owner
--------+------------------+-------+----------
 public | attendance       | table | postgres
 public | attendance_codes | table | postgres
 public | classes          | table | postgres
 public | enrollments      | table | postgres
 public | marks            | table | postgres
 public | students         | table | postgres
 public | teachers         | table | postgres
 public | users            | table | postgres
(8 rows)


school_system=#
"""
