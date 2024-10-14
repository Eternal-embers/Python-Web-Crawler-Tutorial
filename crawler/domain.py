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
