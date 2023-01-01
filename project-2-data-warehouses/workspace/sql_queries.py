import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

ARN = config.get('IAM_ROLE', 'ARN')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplay"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= ("""
    CREATE TABLE IF NOT EXISTS staging_events(
        artist VARCHAR,
        auth VARCHAR,
        first_name VARCHAR,
        gender VARCHAR(1),
        item_in_session INTEGER,
        last_name VARCHAR,
        length FLOAT,
        level VARCHAR,
        location VARCHAR,
        method VARCHAR,
        page VARCHAR,
        registration FLOAT,
        session_id INTEGER sortkey distkey,
        song VARCHAR(255),
        status INTEGER,
        ts BIGINT,
        user_agent VARCHAR,
        user_id INTEGER
    )
""")

staging_songs_table_create = ("""
    CREATE TABLE IF NOT EXISTS staging_songs(
        num_songs INTEGER,
        artist_id VARCHAR sortkey distkey,
        artist_latitude FLOAT,
        artist_longitude FLOAT,
        artist_location VARCHAR(50),
        artist_name VARCHAR,
        song_id VARCHAR,
        title VARCHAR(255),
        duration FLOAT,
        year INTEGER
    )
""")

songplay_table_create = ("""
    CREATE TABLE IF NOT EXISTS songplays(
        songplay_id INTEGER IDENTITY(1,1) sortkey,
        start_time TIMESTAMP NOT NULL,
        user_id INTEGER NOT NULL distkey,
        level VARCHAR(10) NOT NULL,
        song_id VARCHAR,
        artist_id VARCHAR,
        session_id INTEGER NOT NULL,
        location VARCHAR NOT NULL,
        user_agent VARCHAR NOT NULL);
""")

user_table_create = ("""
    CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER sortkey,
        first_name VARCHAR(25),
        last_name VARCHAR(25),
        gender VARCHAR(1),
        level VARCHAR(25) NOT NULL);
""")

song_table_create = ("""
    CREATE TABLE IF NOT EXISTS songs(
        song_id VARCHAR(25) sortkey,
        title VARCHAR(255) NOT NULL,
        artist_id VARCHAR NOT NULL,
        year INTEGER NOT NULL,
        duration FLOAT NOT NULL);
""")

artist_table_create = ("""
    CREATE TABLE IF NOT EXISTS artists(
        artist_id VARCHAR sortkey,
        artist_name VARCHAR NOT NULL,
        artist_location VARCHAR,
        artist_latitude FLOAT,
        artist_longitude FLOAT);
""")

time_table_create = ("""
    CREATE TABLE IF NOT EXISTS time(
        start_time TIMESTAMP sortkey,
        hour INTEGER NOT NULL,
        day INTEGER NOT NULL,
        week INTEGER NOT NULL,
        month INTEGER NOT NULL,
        year INTEGER NOT NULL,
        weekday INTEGER NOT NULL);
""")

# STAGING TABLES

staging_events_copy = ("""
    COPY staging_events FROM 's3://udacity-dend/log_data/2018/11/'
    credentials 'aws_iam_role={}'
    format as json 's3://udacity-dend/log_json_path.json'
    STATUPDATE ON
    region 'us-west-2'
""").format(ARN)

staging_songs_copy = ("""
    COPY staging_songs FROM 's3://udacity-dend/song_data/A/A/'
    credentials 'aws_iam_role={}'
    format as json 'auto'
    STATUPDATE ON
    region 'us-west-2'
""").format(ARN)

# FINAL TABLES

songplay_table_insert = ("""
    INSERT INTO songplays(start_time, user_id,
                          level, song_id,
                          artist_id, session_id,
                          location, user_agent)
    SELECT  DISTINCT TIMESTAMP 'epoch' + s_events.ts/1000 * INTERVAL'1 second' as start_time,
            s_events.user_id as user_id,
            s_events.level as level,
            s_songs.song_id as song_id,
            s_songs.artist_id as artist_id, 
            s_events.session_id as session_id,
            s_events.location as location,
            s_events.user_agent as user_agent
    FROM staging_events as s_events
    JOIN staging_songs as s_songs ON (s_events.artist=s_songs.artist_name)
""")

user_table_insert = ("""
    INSERT INTO users(user_id, first_name,
                      last_name, gender,
                      level)
    SELECT DISTINCT s_events.user_id as user_id,
           s_events.first_name as first_name,
           s_events.last_name as last_name,
           s_events.gender as gender,
           s_events.level as level
    FROM staging_events as s_events
""")

song_table_insert = ("""
    INSERT INTO songs(song_id, title,
                      artist_id, year, duration)
    SELECT DISTINCT s_songs.song_id as song_id,
           s_songs.title as title,
           s_songs.artist_id as artist_id,
           s_songs.year as year,
           s_songs.duration as duration
    FROM staging_songs as s_songs
""")

artist_table_insert = ("""
    INSERT INTO artists(artist_id, artist_name,
                        artist_location,
                        artist_latitude,
                        artist_longitude)
    SELECT DISTINCT s_songs.artist_id as artist_id,
           s_songs.artist_name as artist_name,
           s_songs.artist_location as artist_location,
           s_songs.artist_latitude as artist_latitude,
           s_songs.artist_longitude as artist_longitude
    FROM staging_songs as s_songs
""")

time_table_insert = ("""
    INSERT INTO time(start_time, hour, 
                     day, week, month,
                     year, weekday)
    SELECT DISTINCT TIMESTAMP 'epoch' + s_events.ts/1000 * INTERVAL'1 second' as start_time,
           EXTRACT(hour FROM start_time) as hour,
           EXTRACT(day FROM start_time) as day,
           EXTRACT(week FROM start_time) as week,
           EXTRACT(month FROM start_time) as month,
           EXTRACT(year FROM start_time) as year, 
           EXTRACT(weekday FROM start_time) as weekday
    FROM staging_events as s_events
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
