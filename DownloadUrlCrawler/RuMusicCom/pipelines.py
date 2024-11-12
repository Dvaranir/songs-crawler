# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import sqlite3
from itemadapter import ItemAdapter


class TrackPipeline:

    def __init__(self):
        self.con = sqlite3.connect('../tracks.db')
        self.cur = self.con.cursor()

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS tracks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            init_name TEXT,
            init_artist TEXT,
            init_duration_ms INTEGER,
            init_url TEXT,
            name TEXT,
            artist TEXT,
            download_url TEXT,
            duration_ms INTEGER,
            crawled TEXT,
            similarity_name INTEGER,
            similarity_artist INTEGER,
            similarity_duration INTEGER,
            similarity_score INTEGER,
            similarity_sign TEXT
        )
        """)

    def process_item(self, item, spider):

        self.cur.execute(
            """
            SELECT * 
            FROM tracks
            WHERE init_name = ?
                AND init_artist = ? 
                AND init_duration_ms = ? 
                AND similarity_score = ? 
                AND similarity_name = ? 
                AND similarity_artist = ?""",
            (item['init_name'],
             item['init_artist'], 
             item['init_duration_ms'], 
             item['similarity_score'], 
             item['similarity_name'], 
             item['similarity_artist'],
            ))
        result = self.cur.fetchone()

        if result:
            self.cur.execute("""
                UPDATE tracks SET
                    init_name = ?,
                    init_artist = ?,
                    init_duration_ms = ?,
                    init_url = ?,
                    name = ?,
                    artist = ?,
                    download_url = ?,
                    duration_ms = ?,
                    crawled = ?,
                    similarity_name = ?,
                    similarity_artist = ?,
                    similarity_duration = ?,
                    similarity_score = ?,
                    similarity_sign = ?
                WHERE init_name = ?""", (
                item['init_name'],
                item['init_artist'],
                item['init_duration_ms'],
                item['init_url'],
                item['name'],
                item['artist'],
                item['download_url'],
                item['duration_ms'],
                item['crawled'],
                item['similarity_name'],
                item['similarity_artist'],
                item['similarity_duration'],
                item['similarity_score'],
                item['similarity_sign'],
                item['init_name']
            ))
        else:
            self.cur.execute("""
                INSERT INTO tracks (
                    init_name,
                    init_artist,
                    init_duration_ms,
                    init_url,
                    name,
                    artist,
                    download_url,
                    duration_ms,
                    crawled,
                    similarity_name,
                    similarity_artist,
                    similarity_duration,
                    similarity_score,
                    similarity_sign)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                item['init_name'],
                item['init_artist'],
                item['init_duration_ms'],
                item['init_url'],
                item['name'],
                item['artist'],
                item['download_url'],
                item['duration_ms'],
                item['crawled'],
                item['similarity_name'],
                item['similarity_artist'],
                item['similarity_duration'],
                item['similarity_score'],
                item['similarity_sign']
            ))

            result = self.con.commit()

        return item
