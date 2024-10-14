from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
import gzip
from io import BytesIO
from link_finder import LinkFinder
from general import *


class Spider:
    # Class variables (shared among all instances)
    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    queue = set()
    crawled = set()

    def __init__(self, project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        self.boot()
        self.crawl_page('First spider', Spider.base_url)

    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)

    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(thread_name + ' crawling ' + page_url)
            print('Queue ' + str(len(Spider.queue)) + ' | Crawled ' + str(len(Spider.crawled)))
            Spider.add_links_to_queue(Spider.gather_links(page_url))
            Spider.queue.remove(page_url)
            Spider.crawled.add(page_url)
            Spider.update_files()

    @staticmethod
    def is_valid(url):
        # 定义允许的文件拓展名
        valid_extensions = ['html', '.htm', '.php', '.jsp', '.asp', '.aspx']
        parsed_url = urlparse(url)
        _, ext = os.path.splitext(parsed_url.path)
        return ext in valid_extensions

    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/58.0.3029.110 Safari/537.3'
            }
            req = Request(page_url, headers=headers)
            response = urlopen(req)
            if 'text/html' in response.getheader('Content-Type', ''):
                content_encoding = response.getheader('Content-Encoding', '')
                html_bytes = response.read()
                if content_encoding == 'gzip':  # 解压缩内容
                    buffer = BytesIO(html_bytes)
                    with gzip.open(buffer, 'rt', encoding='utf-8') as f:
                        html_string = f.read()
                else:  # 直接解码内容
                    html_string = html_bytes.decode("utf-8")
            finder = LinkFinder(Spider.base_url, page_url)
            finder.feed(html_string)
        except HTTPError as e:
            print(f'HTTP Error: {e.code} - {e.reason} for URL {page_url}')
            return set()
        except URLError as e:
            print(f'URL Error: {e.reason} for URL {page_url}')
            return set()
        except UnicodeDecodeError:
            print(f'Decode Error: Could not decode content from {page_url}')
            return set()
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            return set()
        return finder.page_links()

    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if url in Spider.queue:
                continue
            if url in Spider.crawled:
                continue
            if Spider.domain_name not in url:
                continue
            Spider.queue.add(url)

    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)
