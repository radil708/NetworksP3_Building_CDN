import requests
import zipfile
import os

"""
Handles the client request. Either gets the html from source or cache
and returns the html to the client.
"""
class HttpServer:
    def get_html(self, client_request):
        # if client_request in cache, get_html_from_cache
        # else 
        #requests.get(client_request)
        pass

"""
The LRU cache will replace the last recently used (requested) html with the
latest item requested by the client. Timestamps are used to keep track of
the last time an item was requested.
"""
class Cache:
    def __init__(self) -> None:
        # format of cache: {request: freq_req}
        self.in_memory_cache = {}
        self.folder_size = 0
        self.current_folder = os.path.abspath(os.getcwd())
    
    def add_request_to_cache(self, client_request):
        # add the client's request to the cache
        # replacing the last recently used element in the cache
        pass

    def calculate_folder_size(self):
        for path, _, files in os.walk(self.current_folder):
            for f in files:
                fp = os.path.join(path, f)
                self.folder_size += os.path.getsize(fp)

    def write_to_file(self, html_data):
        filename = "ex.txt"
        with open(filename, 'w') as f:
            f.write(html_data)
            self.zip_file(filename)

    def zip_file(self, filepath):
        # https://stackoverflow.com/questions/42214376/zip-single-file
        # zip the file to cache
        zip_filepath = filepath.replace('.txt', '.zip')
        zipfile.ZipFile(zip_filepath, mode='w').write(filepath)
    
    def write_cache_to_file(self):
        # cache to file
        pass

    def get_html_from_cache(self, client_request):
        # unzip the file with appropriate filename and get the appropriate html 
        # update the timestamp_last_requested of the client_request
        pass
    
    
