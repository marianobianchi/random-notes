# coding=utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import namedtuple
import httplib
import requests
import ssl
from timeit import default_timer as timer
import urllib


class Timer(object):
    def __init__(self, data=None, verbose=False):
        self.data = data if data is not None else {}
        self.verbose = verbose

    def __enter__(self):
        self.start = timer()

    def __exit__(self, *args, **kwargs):
        self.end = timer()
        self.elapsed_time = self.end - self.start
        if self.verbose:
            print('code snippet took {n} seconds'.format(n=self.elapsed_time))
        self.data['elapsed_time'] = self.elapsed_time


Response = namedtuple('Response', 'status_code content')


class Request(object):
    def __init__(self, host):
        self.host = host

    def get(self, url, params):
        raise Exception('Subclasses must define this method')


class HighLevelRequest(Request):

    def get_endpoint(self, url):
        host = self.host if not self.host.endswith('/') else self.host[:-1]
        url = url if url.startswith('/') else '/' + url
        return host + url

    def get(self, url, params):
        endpoint = self.get_endpoint(url)
        response = requests.get(endpoint, params=params)
        return Response(response.status_code, response.content)


class LowLevelRequest(Request):
    def __init__(self, *args, **kwargs):
        super(LowLevelRequest, self).__init__(*args, **kwargs)
        # Since the host can be an IP addresses, it will likely not match the
        # SSL cert hostnames
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False

    def join_path_and_query(self, url, params):
        url = url if url.startswith('/') else '/' + url
        params = urllib.urlencode(params)
        return '{u}?{q}'.format(u=url, q=params)

    def get(self, url, params):
        address = self.join_path_and_query(url, params)
        conn = httplib.HTTPSConnection(self.host, context=self.ssl_context)
        conn.request('GET', address)
        resp = conn.getresponse()
        return Response(resp.status, resp.read())


def usando_dns():
    """
    =======
    /etc/resolv.conf
    nameserver 208.67.222.222  # OpenDNS
    =======
    Cada request (total: 100) tardó en promedio 0.409232928753 segundos
    (min: 0.307535171509; max: 1.62553405762)
    """
    url = 'buscar'
    params = {'categoria': 'deficit_habitacional', 'texto': 'villa'}
    req = HighLevelRequest('https://epok.buenosaires.gob.ar/')
    return req.get(url, params)


def salteando_dns():
    """
    Cada request (total: 100) tardó en promedio 0.187145149708 segundos
    (min: 0.142405033112; max: 1.3960249424)
    """
    url = '/buscar/'
    params = {'categoria': 'deficit_habitacional', 'texto': 'villa'}
    req = LowLevelRequest('200.16.89.103')
    response = req.get(url, params)
    return response


def promediando_tiempos(func, tries=100):
    tiempos = []
    data = {}
    for i in range(tries):
        with Timer(data):
            func()
        tiempos.append(data.pop('elapsed_time'))
        print('.', end='')

    print('')
    seconds = sum(tiempos) / len(tiempos)
    print(('Cada request (total: {t}) tardó en promedio {s} segundos '
           '(min: {min}; max: {max})').format(s=seconds,
                                              t=len(tiempos),
                                              min=min(tiempos),
                                              max=max(tiempos)))


if __name__ == '__main__':
    intentos = 50
    print('Ejecutando request usando DNS')
    promediando_tiempos(usando_dns, intentos)

    print('Ejecutando request sin usar DNS')
    promediando_tiempos(usando_dns, intentos)
