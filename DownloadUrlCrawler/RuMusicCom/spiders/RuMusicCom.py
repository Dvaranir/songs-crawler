import csv
import scrapy
import difflib

from pathlib import Path
from datetime import datetime


class RuMusicCom(scrapy.Spider):

    name = "RuMusicCom"
    domain = 'ru-music.com'
    site = f"https://{domain}"
    allowed_domains = [domain]
    project_root = Path().parent.absolute().parent.absolute()

    crawled_dict = {}

    def start_requests(self):
        print(self.project_root)
        urls = []
        songs_csv_path = f'{self.project_root}{Path("/songs.csv")}'

        with open(songs_csv_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)

            i = 0
            for row in reader:
                if i == 0:
                    i += 1
                    continue

                search_str = f"{row[0]} {row[1]}"
                search_url = f"https://ru-music.com/public/api.search_result.php?i=0&q={search_str}"

                self.crawled_dict[search_url] = {
                    'init_name': row[0],
                    'init_artist': row[1],
                    'init_duration_ms': row[2],
                    'init_url': search_url,
                }

                urls += [search_url]
                break

        for url in urls:
            yield scrapy.Request(url=url, callback=self.search, meta={'url': url}, dont_filter=True)

    def search(self, response):
        tracks_data = []
        meta_url = response.meta['url']

        blank_track = {
            'name': "",
            'artist': "",
            'download_url': "",
            'duration_ms': 0,
            'crawled': "❌",
            'similarity_name': '',
            'similarity_artist': '',
            'similarity_duration': '',
            'similarity_score': '',
            'similarity_sign': '',
        }

        try:
            tracks = response.css(".track")

            if not tracks:
                raise Exception("No tracks found")

            for track in tracks:
                endpoint = track.css(
                    '.playlist-btn-download a::attr(href)').extract_first()
                url = f"{self.site}{endpoint}"
                minutes_and_seconds = track.css(
                    ".playlist-duration::text").extract_first()
                ms = self.duration_to_ms(minutes_and_seconds)

                track_data = {
                    'name': track.css(".playlist-name em::text").extract_first(),
                    'artist': track.css(".playlist-name b::text").extract_first(),
                    'download_url': url,
                    'duration_ms': ms,
                    'crawled': "✅",
                }

                tracks_data += [track_data]

            target_name = self.crawled_dict[meta_url]['init_name']
            target_artist = self.crawled_dict[meta_url]['init_artist']
            target_ms = self.crawled_dict[meta_url]['init_duration_ms']

            closest_track = self.closest_track(
                tracks_data, target_name, target_artist, target_ms)

            for key in self.crawled_dict[meta_url]:
                closest_track[key] = self.crawled_dict[meta_url][key]

            self.crawled_dict[meta_url] = {
                **self.crawled_dict[meta_url], **closest_track}
        except:
            self.crawled_dict[meta_url] = {
                **self.crawled_dict[meta_url], **blank_track}

        yield self.crawled_dict[meta_url]

    def duration_to_ms(self, duration_str):
        if not duration_str:
            return 0

        time_obj = datetime.strptime(duration_str, '%M:%S')
        milliseconds = (time_obj.minute * 60 + time_obj.second) * 1000

        return milliseconds

    def closest_track(self, objects, target_name, target_artist, target_ms):
        track = max(objects, key=lambda obj: (
            self.str_similarity(obj['name'], target_name),
            self.str_similarity(obj['artist'], target_artist),
            -abs(int(obj['duration_ms']) - int(target_ms))
        ))

        self.add_similarity(track, target_name, target_artist, target_ms)

        return track

    def add_similarity(self, track, target_name, target_artist, target_ms):
        track['similarity_name'] = self.str_similarity(
            track['name'], target_name)

        track['similarity_artist'] = self.str_similarity(
            track['artist'], target_artist)

        track['similarity_duration'] = self.int_similarity(
            track['duration_ms'], int(target_ms))

        similarity_score = (
            track['similarity_name'] + track['similarity_artist'] + track['similarity_duration']) / 3 * 100

        if similarity_score > 80:
            track['similarity_sign'] = "🟢"
        elif similarity_score > 50:
            track['similarity_sign'] = "🟡"
        elif similarity_score > 35:
            track['similarity_sign'] = "🟠"
        else:
            track['similarity_sign'] = "🔴"

        track['similarity_score'] = similarity_score

    def str_similarity(self, str1, str2):
        return difflib.SequenceMatcher(None, str1, str2).ratio()

    def int_similarity(self, target_int, compare_int):
        return 1 - abs(int(target_int) - int(compare_int)) / max(int(target_int), int(compare_int))
