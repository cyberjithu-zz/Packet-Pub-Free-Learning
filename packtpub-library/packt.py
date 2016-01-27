# -*- coding: utf-8 -*-

import sys
import requests
import ConfigParser
from time import sleep
from scrapy.selector import Selector
import os.path


class FreeBookPackt(object):

    start_url = 'https://www.packtpub.com/packt/offers/free-learning'
    base_url = 'https://www.packtpub.com'
    my_ebook_url = 'https://www.packtpub.com/account/my-ebooks'

    def __init__(self, *args, **kwargs):
        settings = ConfigParser.RawConfigParser()
        settings.read('settings.cfg')
        self.email = settings.get('PACKTPUB', 'email')
        self.password = settings.get('PACKTPUB', 'password')
        self.chunk_size = int(settings.get('DOWNLOAD', 'chunk_size'))
        self.download_speed = int(settings.get('DOWNLOAD', 'down_speed'))
        self.total_chunk = self.chunk_size * self.download_speed

    def progress_bar(self, current, total, file_name='my_file'):
        proggress_bar_length = 100
        fill_length = proggress_bar_length * current / total
        percentage = round((100 * current / float(total)), 2)
        display_bar = '#' * fill_length + '-' * \
            (proggress_bar_length - fill_length)

        sys.stdout.write(
            '[{}] {}{} --{}{}/{}{}--{}\r'.format(display_bar, percentage, '%', '[ ' + str(round((current / 1024.0), 2)), 'mb', str(round((total / 1024.0), 2)), 'mb ]', file_name))
        sys.stdout.flush()

    def add_config(self, name):
        settings = ConfigParser.RawConfigParser()
        settings.add_section('FILE')
        settings.set('FILE', 'name', name)

    def download_book(self, request, file_name, link, download_speed=1, chunk_size=1024):
        total_chunk = download_speed * chunk_size
        with open(file_name, 'wb') as handle:
            response = request.get(link, stream=True)
            if not response.ok:
                # Something went wrong
                print 'Error'
            print '################### ESTIMATING FILE SIZE  ###################'
            total_length = response.headers.get('content-length')
            if total_length:
                total_length = (int(total_length) / (total_chunk))
            else:
                total_length = sum(
                    1 for i in response.iter_content(total_chunk))
                sleep(2)
                response = request.get(self.base_url + link, stream=True)
            for index, block in enumerate(response.iter_content(total_chunk)):
                self.progress_bar(
                    download_speed * index, download_speed * total_length, file_name)
                handle.write(block)
            else:
                sys.stdout.write(
                    '[{}] {}{} ---{}\n'.format('#' * 100, 100, '%', 'Done !' + self.file_name))

    def claim_book(self):
        FORM_BUILD_ID_XPATH = '//form[@id="packt-user-login-form"]/div/input[@name="form_build_id"]/@id'
        FORM_ID_XPATH = '//form[@id="packt-user-login-form"]/div/input[@name="form_id"]/@value'

        BOOK_LINK_XPATH = '//div[@class="float-left free-ebook"]/a/@href'
        BOOK_NAME_XPATH = '//div[@id="product-account-list"]/div[@class="product-line unseen"]/@title'
        EPUB_LINK_XPATH = '//div[@id="product-account-list"]/div[@class="product-line unseen"]/div[@class="product-buttons-line toggle"]/div[@class="download-container cf "]/a[div[@format="epub"]]/@href'
        PDF_LINK_XPATH = '//div[@id="product-account-list"]/div[@class="product-line unseen"]/div[@class="product-buttons-line toggle"]/div[@class="download-container cf "]/a[div[@format="pdf"]]/@href'

        data = requests.get('https://www.packtpub.com/').content
        response = Selector(text=data)
        form_build_id = response.xpath(FORM_BUILD_ID_XPATH).extract()[0]
        form_id = response.xpath(FORM_ID_XPATH).extract()[0]
        self.formdata = {
            'form_build_id': form_build_id, 'form_id': form_id, 'op': 'Login'}
        user = {'password': self.password, 'email': self.email}
        self.formdata.update(user)
        print self.formdata

        req = requests.session()
        req.post(self.start_url, data=self.formdata)
        print '###################        Login         ###################'
        sel = Selector(text=req.get(self.start_url).content)
        book_link = self.base_url + \
            sel.xpath(BOOK_LINK_XPATH).extract()[0]
        req.get(book_link)
        info = req.get(self.my_ebook_url).content
        print '################### BOOK ADDED TO LIBRARY ###################'
        sell = Selector(text=info)
        name = sell.xpath(BOOK_NAME_XPATH).extract()[0]
        self.file_name = name + '.epub'
        if not os.path.isfile(self.file_name):
            link = sell.xpath(EPUB_LINK_XPATH).extract()[0]
            link = self.base_url + link
            self.download_book(
                req, self.file_name, link, self.download_speed, self.chunk_size)
            pdf_link = sell.xpath(PDF_LINK_XPATH).extract()[0]
            pdf_link = self.base_url + pdf_link
            self.download_book(
                req, self.file_name.replace('.epub', '.pdf'), pdf_link, self.download_speed, self.chunk_size)

        else:
            print 'FILE ALREADY DOWNLOADED'