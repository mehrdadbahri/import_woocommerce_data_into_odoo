#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import traceback
import base64
import mimetypes
from progress.bar import Bar


class Import(object):

    def run(self):
        with open(self.data_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            csv_lines = list(csv_reader)
            first = True
            try:
                with Bar('processing rows', max=len(csv_lines)-1) as bar:
                    for row in csv_lines:
                        if first:
                            first = False
                            bar.next()
                            continue
                        self.process_row(row)

                        if self.stop:
                            break
                        bar.next()
            except Exception:
                print(traceback.format_exc())

    def signal_handler(self, signal, frame):
        self.stop = True

    def get_imported_records(self):
        model = 'ir.model.data'
        domain = [
                ['model', '=', self.model],
            ]
        fields = ['res_id', 'name']
        self.imported_records = self.api.search_read(model, domain, fields)

    def get_imported_products(self):
        model = 'ir.model.data'
        domain = [
            ['model', '=', 'product.template'],
        ]
        fields = ['id', 'res_id', 'name']
        self.products = self.api.search_read(model, domain, fields)

    def already_imported(self, name):
        for item in self.imported_records:
            if item['name'] == name:
                return True
        return False

    def replace_images(self, text, old_url):
        try:
            with open(self.uploads_path + old_url, "rb") as image_file:
                imageBase64 = base64.b64encode(image_file.read())
            mimetype = mimetypes.guess_type(old_url)[1]
            attachment_data = {
                'res_model': 'ir.ui.view',
                'name': old_url.split('/')[-1],
                'res_id': 0,
                'type': 'binary',
                'mimetype': mimetype,
                'datas': imageBase64.decode('ascii')
            }
            model = 'ir.attachment'
            attch_id = self.api.create(model, [attachment_data])
            new_url = "/web/image/{}".format(attch_id)
            description = text.replace(old_url, new_url)
        except Exception:
            print(traceback.format_exc())
        return description

    def replace_category_links(self, description, old_url):
        try:
            with open(self.uploads_path + old_url, "rb") as image_file:
                imageBase64 = base64.b64encode(image_file.read())
            mimetype = mimetypes.guess_type(old_url)[1]
            attachment_data = {
                'res_model': 'ir.ui.view',
                'name': old_url.split('/')[-1],
                'res_id': 0,
                'type': 'binary',
                'mimetype': mimetype,
                'datas': imageBase64.decode('ascii')
            }
            model = 'ir.attachment'
            attch_id = self.api.create(model, [attachment_data])
            new_url = "/web/image/{}".format(attch_id)
            description = description.replace(old_url, new_url)
        except Exception:
            print(traceback.format_exc())
        return description
