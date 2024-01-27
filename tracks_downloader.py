import sqlite3
import re
from playwright.sync_api import sync_playwright


class PlaywrightController:

    def __init__(self):
        self.chrome_args = [
            '--use-angle=vulkan',
            '--enable-gpu',
            '--no-sandbox',
            '--ignore-gpu-blocklist',
        ]

        self.db_cursor_init()
        self.create_downloaded_column()
        self.get_undownloaded_tracks()
        self.event_loop()

    def db_cursor_init(self):
        self.conn = sqlite3.connect('tracks.db')
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def create_downloaded_column(self):
        self.cursor.execute("PRAGMA table_info(tracks)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'downloaded_path' not in columns:
            self.cursor.execute(
                'ALTER TABLE tracks ADD COLUMN downloaded_path TEXT')
            self.conn.commit()

    def get_undownloaded_tracks(self):
        self.cursor.execute(
            "SELECT * FROM tracks WHERE downloaded_path IS NULL AND download_url IS NOT NULL")
        rows = self.cursor.fetchall()
        self.tracks = [dict(row) for row in rows]

    def start_session(self, pw):
        self.browser = pw.chromium.launch(headless=True,
                                          args=self.chrome_args,
                                          executable_path='E:\Programs\Development\PlaywrightBrowsers\chromium-1060\chrome-win\chrome.exe',
                                          timeout=0)

        self.page = self.browser.new_page()
        self.page.set_viewport_size({'width': 1920, 'height': 1080})

    def event_loop(self):
        with sync_playwright() as pw:
            self.start_session(pw)
            for track in self.tracks:
                if not track['download_url']:
                    continue
                
                self.page.goto(track['download_url'], timeout=0)
                self.page.wait_for_load_state('networkidle')
                button = self.page.get_by_text("Скачать")

                if (button):
                    with self.page.expect_download(timeout=120000) as download_info:
                        button.click()

                download = download_info.value
                extension = download.suggested_filename.split('.')[-1]
                filename = f"{track['init_artist']} - {track['init_name']}.{extension}"
                filename = self.sanitize_filename(filename)
                download.save_as(f"./downloads/{filename}")

                if not download.failure():
                    self.cursor.execute("""
                        UPDATE tracks
                        SET downloaded_path = ?
                        WHERE id = ?
                    """, (str(download.path()), track['id']))
                    self.conn.commit()
                    print(f"Downloaded {track['init_artist']} - {track['init_name']}")

    def go_to_next_track(self):
        print(f"Fetching {self.url}")
        self.page.goto(self.url, timeout=0)

    def sanitize_filename(self, filename):
        filename = re.sub(r'[\\/*?:"<>|]', "", filename)
        filename = filename.replace(' ', '_')
        return filename


PlaywrightController()
