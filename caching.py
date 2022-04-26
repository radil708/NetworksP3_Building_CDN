import requests
import zipfile
import os
import socket 
import csv
import time
import gzip
import shutil

ORIGIN_PORT = 8080
PAGEVIEWS_FILENAME = "pageviews.csv"
ORIGIN = "cs5700cdnorigin.ccs.neu.edu"
MAX_CACHE_SIZE_BYTES = 1000000 * 15
CACHED_FILES_LIST = "cached_files.txt"
MAX_NUM_FILES_TO_PRELOAD = 1000
"""
LFU cache 
"""
class Cache:
    def __init__(self) -> None:
        self.starttime = time.time()

        self.cached_files = []
        self.current_folder = os.path.abspath(os.getcwd())

        self.cached_folder = self.current_folder + '/cached_files'
        if os.path.exists(self.cached_folder): shutil.rmtree(self.cached_folder)
        os.makedirs(self.cached_folder)

        self.current_size = os.path.getsize(self.current_folder)

        #print('curr folder', self.current_folder, 'curr folder size', self.current_size)

    def load_pageviews_file(self):
        """
        Loads the list of most queries files into self.cached_files up to a max of 1000 files
        """
        with open(PAGEVIEWS_FILENAME) as pageviews_csv:
            reader = csv.reader(pageviews_csv)
            for row in reader:
                page, _ = row[0], row[1]
                self.cached_files.append(page)
                if len(self.cached_files) == MAX_NUM_FILES_TO_PRELOAD: break


    def preload_cache(self):
        """
        Adds all the most popular pages queried to the cache up to max cache size.
        """
        self.load_pageviews_file()
        print("Preloading the cache with most queried files.")

        for title in self.cached_files:
            if self.current_size < MAX_CACHE_SIZE_BYTES:
                complete_url = 'http://' + ORIGIN + ':' + str(ORIGIN_PORT) + '/' + title
                response = requests.get(url=complete_url)
                if response.status_code == 200:
                    self.cache_html_content(title, response.content)
                else:
                    print('Response code for webpage', title, 'is', response.status_code)
            else:
                break

        with open(CACHED_FILES_LIST, 'w') as cf:
            cached_files = os.listdir(self.cached_folder)
            for f in cached_files:
                cf.write(f + "\n")

    def cache_html_content(self, title, content):
        zip_filepath = self.cached_folder + '/' + title + ".zip"
        
        with gzip.open(zip_filepath, 'wb') as wfile:
            wfile.write(content)
        
        fsize = os.path.getsize(zip_filepath)
        self.current_size += fsize
        #print('curr zip file size', fsize, 'total', self.current_size)

def main():
    cache = Cache()
    cache.preload_cache()
    print("Caching deploy completed. Total time taken:", time.time() - cache.starttime)
main()
    