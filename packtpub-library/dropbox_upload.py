# -*- coding: utf-8 -*-

import dropbox
import ConfigParser


class DropboxPackt(object):

    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read('settings.cfg')
        self.access_token = config.get('DROPBOX', 'access_token')

    def upload_file(self, file_name):
        client = dropbox.client.DropboxClient(self.access_token)
        fileobject = open(file_name, 'rb')
        response = client.put_file('packt/%s' % file_name, fileobject)
        print response

if __name__ == '__main__':
    packt_object = FreeBookPackt()
    packt_object.claim_book()
    dropbox_packt_object = DropboxPackt()
    print '###################  READING EPUB  ###################'
    dropbox_packt_object.upload_file(packt_object.file_name)
    print '###################  READING PDF  ###################'
    dropbox_packt_object.upload_file(
        packt_object.file_name.replace('.epub', '.pdf'))
