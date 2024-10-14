# Python 爬虫入门

在这篇文章中，我将分享一个来自 Youtube 的 Python 爬虫的 demo，此 Python 爬虫非常简单易懂，适合初学者入门。

你可以在 [Python Web Crawler Tutorial](https://www.youtube.com/watch?v=nRW90GASSXE&list=PL6gx4Cwl9DGA8Vys-f48mAH9OKSUyav0q) 观看完整的视频教程。

## 爬虫介绍

爬虫（Web crawler）是一种自动化的程序，它按照一定的规则，自动地抓取互联网信息。它为搜索引擎从互联网上下载网页，是搜索引擎数据收集的核心部分。爬虫的基本工作流程大致如下：

1. 发现新链接：爬虫从一组已知的URL开始，访问这些网页，并提取网页中的链接。

2. 下载网页：爬虫访问这些链接，下载网页内容。

3. 存储网页：下载的网页内容被存储在数据库中，供搜索引擎索引使用。

4. 提取信息：爬虫提取网页中的信息，如文本、图片、视频等。

5. 更新数据库：爬虫定期重新访问网页，更新数据库中的信息。

6. 避免重复：爬虫会记录已经访问过的网页，避免重复抓取。

在本文介绍的爬虫，将通过给定一个起始 URL，将爬取该网站的所有链接，被爬取到的链接也将被爬取，每次都将爬取到的链接存储到文件中。

## 项目初始化

我们使用 Pycharm 编写项目，首先需要创建一个新项目，使用默认的 `venv` 环境，构建项目结构如下：

```text
- crawler      
    - general.py   
    - link_finder.py
    - spider.py
    - domin.py
    - main.py      
```

## 创建工作目录

在工作目录中，我们需要创建两个文件：`queue.txt` 和 `crawled.txt`

其中 `queue.txt` 用于存放待爬取的 URL，`crawled.txt` 用于存放已爬取完的 URL。

ok，那么爬虫每次都会从 `queue.txt` 中取出一个 URL，然后访问该 URL，并将该网页中的链接存入 `queue.txt` 中,爬取完该 URL 的所有链接后将此 URL 存入 `crawled.txt` 中。

为了提高爬虫的效率，我们不能每次都从文件中读取 URL，因为文件IO操作是很耗时的，所以我们可以将 URL 存入内存中，每次取出一个 URL 进行访问，并将访问过的 URL 存入文件中。而集合解决一切，我们将文件中的 URL 存入到集合里，集合存储在内存中，因此大大提高了效率。

在 `general.py` 文件中，我们定义了一些函数，用于创建项目目录、创建数据文件、写入数据、读取数据、删除数据，以及实现文件和集合之间的转换。

当创建项目时，会根据项目名称创建文件夹，并在项目文件夹中创建 `queue.txt` 和 `crawled.txt` 文件。

`general.py`

```Python
import os


# Each website you crawl is a separate project(folder)
def create_project_dir(directory):
    if not os.path.exists(directory):
        print('Creating project ' + directory)
        os.mkdir(directory)


# create queue and crawled files (if not created)
def create_data_files(project_name, base_url):
    queue = project_name + '/queue.txt'
    crawled = project_name + '/crawled.txt'
    if not os.path.isfile(queue):
        write_file(queue, base_url)
    if not os.path.isfile(crawled):
        write_file(crawled, '')


# create a new file
def write_file(path, data):
    f = open(path, 'w')
    f.write(data)
    f.close()


# Add data onto an existing file
def append_to_file(path, data):
    with open(path, 'a') as file:
        file.write(data + '\n')


# Delete the contents of a file
def delete_file_contents(path):
    with open(path, 'w'):
        pass


# Read a file and convert each line to set items
def file_to_set(file_name):
    result = set()
    with open(file_name, 'rt') as f:  # read text mode
        for line in f:
            result.add(line.replace('\n', ''))
    return result


# Iterate through a set, each item will be a new line in file
def set_to_file(links, file):
    delete_file_contents(file)
    for link in sorted(links):
        append_to_file(file, link)
```

## 解析网页

ok, 接下来我们编写 `link_finder.py` 文件，用于解析网页，提取链接，我们将链接存入到集合中。

其中 `handle_starttag` 有必有进行解释一番，`LinkFinder` 继承了 `HTMLParser` 类，`HTMLParse` 解析HTML是事件驱动的，我们重写了 `handle_starttag` 方法，当遇到 `<a>` 标签时，我们提取其 `href` 属性，并将其加入到集合中。

当解析器遇到 HTML 文档中的特定元素时，它会触发相应的事件，并调用用户定义的事件处理函数。这些事件处理函数包括：

`handle_starttag(tag, attrs)`: 处理开始标签。
`handle_endtag(tag)`: 处理结束标签。
`handle_data(data)`: 处理文本数据。
`handle_comment(data)`: 处理注释。
`handle_entityref(name)`: 处理实体引用（如 &amp;）。
`handle_charref(name)`: 处理字符引用（如 &#123;）。

```Python
from html.parser import HTMLParser
from urllib import parse


class LinkFinder(HTMLParser):

    def __init__(self, base_url, page_url):
        super().__init__()
        self.base_url = base_url
        self.page_url = page_url
        self.links = set()

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for(attribute, value) in attrs:
                if attribute == 'href':
                    url = parse.urljoin(self.base_url, value)
                    self.links.add(url)

    def page_links(self):
        return self.links

    def error(self, message):
        pass
```

`LinkFinder` 仅仅是处理网页时的工具，我们的爬虫将会使用 `LinkFinder` 类来解析网页，并将链接存入到集合中。

## 爬虫

`spider.py` 文件中，导入这些包：

```Python
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
import gzip
from io import BytesIO
from link_finder import LinkFinder
from general import *
```

通过在 `Spider` 类中定义公共变量，让所有的爬虫实例都共享数据，这样不会重复爬取相同的 URL。

在数据域中添加了一个 `domain_name`，这是为了限制爬取的范围，只爬取指定域名下的网页，因为爬取的网页中可能存在外链，假如爬取到 `YouTube`，如果不限制域名，那么爬虫将会去爬取 `YouTube` 的所有链接，这可不是我们想要的。

`boot()` 方法用于初始化项目，创建项目文件夹、创建数据文件、读取数据文件，并将数据文件转换为集合。

```Python
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
```

`craw_page()` 方法爬取一个 URL，如果页面没有爬取过，则将页面中的所有链接添加到队列中，然后从队列中移除此链接，接着将它加入到已爬取的集合中，最后更新数据文件。

```Python
    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            print(thread_name + ' crawling ' + page_url)
            print('Queue ' + str(len(Spider.queue)) + ' | Crawled ' + str(len(Spider.crawled)))
            Spider.add_links_to_queue(Spider.gather_links(page_url))
            Spider.queue.remove(page_url)
            Spider.crawled.add(page_url)
            Spider.update_files()
```

接下来完成 `add_links_to_queue()`、`gather_links()` 和 `update_files()` 方法。

`add_links_to_queue()` 方法将页面中的所有链接添加到队列中，对于每一个链接，如果链接不在在待爬取队列、已爬取集合中，且链接在限定域名，则将其添加到待爬取队列中。

```Python
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
```

`gather_links()` 对 URL 发起请求，将返回的 `response` 字节数据编码为 `utf-8` 字符串，并使用 `LinkFinder` 类解析 HTML 字符串，返回所有链接。

try-except 块处理异常，保证爬取过程中出现错误能继续爬取。

```Python
    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            response = urlopen(page_url)
            if 'text/html' in response.getheader('Content-Type'): # check if content is html
                html_bytes = response.read()
                html_string = html_bytes.decode('utf-8') # response return bytes
            finder = LinkFinder(Spider.base_url, page_url)
            finder.feed(html_string) # parse html string
        except:
            print('Error: can not crawl page')
            return set()
        return finder.page_links() # return all links on page
```

以上 `gather_links()` 足够清晰，但是为了丰富异常处理和解决一些无法爬取的情况，我对其进行了拓展：

* `User-Agent` 头部用于模拟浏览器，避免被网站认为是爬虫。
* 处理 `content_encoding` 头部用于解压缩网页内容，避免乱码。
* 对各类异常给出详细的提示，用于排查错误。

```Python
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
```

`update_files()` 方法将集合转换为文件，保证爬取的数据及时更新到文件中。

```Python
    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)
```

## 域名解析

`domain.py` 文件用于解析域名，获取域名的主域名和子域名。

```Python
from urllib.parse import urlparse


# Get domain name(example.com)
def get_domain_name(url):
    try:
        results = get_sub_domain_name(url).split('.')
        return results[-2] + '.' + results[-1]
    except:
        return ''


# Get sub domin name(name.example.com)
# url = "https://www.example.com:8080/path/to/page?query=arg#fragment" 返回 "www.example.com:8080"
def get_sub_domain_name(url):
    try:
        return urlparse(url).netloc
    except:
        return ''
```

## 多线程爬取

一切都准备完毕，接下来编写主程序 `main.py`。

主要是创建线程，创建工作队列，将初始 URL 放入队列中，启动线程，等待线程结束。其中 `create_jobs()` 和 `crawl()` 相互调用，以实现不断的爬取。

有必要解释一下 `Queue` 类，它是一个线程安全的队列，可以安全地在多个线程之间共享数据，程序中 `queue` 用于在线程之间共享 URL 队列。

```Python
import threading
from queue import Queue
from spider import Spider
from domain import *
from general import *

PROJECT_NAME = 'tencent'
HOMEPAGE = "https://www.tencent.com/"
DOMAIN_NAME = get_domain_name(HOMEPAGE)
QUEUE_FILE = PROJECT_NAME + '/queue.txt'
CRAWLED_FILE = PROJECT_NAME + '/crawled.txt'
NUMBER_OF_THREADS = 8
queue = Queue()
Spider(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME)


# create worker threads (will die when main exits)
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True  # die whenever the main exit
        t.start()


# do the next job in the queue
def work():
    while True:
        url = queue.get()
        Spider.crawl_page(threading.current_thread().name, url)
        queue.task_done()


# Each queued link is a new job
def create_jobs():
    for link in file_to_set(QUEUE_FILE):
        queue.put(link)
    queue.join()  # block until all tasks are done
    crawl()


# Check if there are items in the queue, if so crawl them
def crawl():
    queued_links = file_to_set(QUEUE_FILE)
    if len(queued_links) > 0:
        print(str(len(queued_links)) + ' links in the queue')
        create_jobs()


if __name__ == '__main__':
    try:
        create_workers()  # create worker threads
        crawl()
    except Exception as e:
        print(f"An error occurred: {e}")
```

如果你需要爬取其他网站，只需要修改 `PROJECT_NAME` 和 `HOMEPAGE` 即可。可以尝试爬取这些网站，看看效果：

```text
https://www.mi.com/
https://www.microsoft.com/zh-cn/
https://www.apple.com/cn/
```