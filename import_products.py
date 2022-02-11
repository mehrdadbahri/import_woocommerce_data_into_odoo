#!/usr/bin/env python
# -*- coding: utf-8 -*-
import signal
import re
import traceback
import base64
from api_connector import API
from importer import Import


class Product(Import):
    created_ids = []
    model = 'product.template'

    def __init__(self, data_file):
        self.data_file = data_file
        self.api = API()
        if self.api:
            self.get_imported_records(self)
            self.get_imported_categories(self)
            return True
        return False

    def get_imported_categories(self):
        model = 'ir.model.data'
        domain = [
            ['model', '=', 'product.public.category'],
        ]
        fields = ['res_id', 'name']
        self.imported_cats = self.api.search_read(model, domain, fields)

    def process_row(self, row):
        if self.already_imported(row[0]):
            return
        data = {
            'name': row[1],
            'website_published': row[3] == "True",
            'sale_ok': True,
            'purchase_ok': True,
            'type': 'product',
        }
        categ_ids = self.get_categories(row)
        description = self.get_description(row)
        if description:
            data['website_description'] = description
        if row[4] != "NULL":
            data['default_code'] = row[4]
        if row[5] != "NULL":
            data['lst_price'] = row[5]
        if row[6] != "NULL":
            try:
                model = 'wk.product.brand'
                brand = self.api.get_record_id_by_external_identifier(
                    model, row[6])
                if len(brand):
                    data['product_brand_id'] = brand[0]['res_id']
            except Exception:
                pass
        if row[10] != "NULL":
            data['website_meta_title'] = row[10].replace(
                '%%page%% %%sep%% %%sitename%%', '')
        if row[11] != "NULL":
            data['website_meta_description'] = row[11]

        if len(categ_ids):
            data['public_categ_ids'] = [(6, 0, categ_ids)]
        if row[13] and row[13] != "NULL":
            try:
                with open("uploads/" + row[13], "rb") as image_file:
                    b64_image = base64.b64encode(image_file.read())
                    data['image_1920'] = b64_image.decode('ascii')
            except Exception:
                print(traceback.format_exc())

        pid = None
        try:
            pid = self.api.create(self.model, [data])
            self.created_ids.append(pid)
        except Exception as e:
            print(e)

        if pid:
            self.upload_images(row, pid)

            reference_data = {
                'module': '__import__',
                'model': 'product.template',
                'name': row[0],
                'res_id': pid
            }
            self.api.create('ir.model.data', [reference_data])
            return pid

    def upload_images(self, row, pid):
        index = 14
        while len(row) > index:
            if row[index] != "NULL":
                try:
                    with open("uploads/" + row[index], "rb") as image_file:
                        b64_image = base64.b64encode(image_file.read())
                        image_data = {
                            'image_1920': b64_image.decode('ascii'),
                            'name': row[1],
                            'product_tmpl_id': pid
                        }
                        self.api.create('product.image', [image_data])
                except Exception:
                    print(traceback.format_exc())
            index += 1

    def get_categories(self, row):
        categ_ids = []
        if row[13] != "NULL":
            try:
                external_ids = row[13].split('|')
                for eid in external_ids:
                    cat = list(
                        filter(
                            lambda item: item['name'] == "product_category_{}".
                            format(eid), self.imported_cats))
                    if len(cat):
                        categ_ids.append(cat[0]['res_id'])
            except Exception:
                print(traceback.format_exc())
        return categ_ids

    def get_description(self, row):
        try:
            if row[2] != "NULL":
                description = row[2].replace('\\"', '"').replace('\\n', '\n')
                regex = r"<img.+?src=\"(.+?)\".+?/?>"
                matches = re.findall(regex, description, re.MULTILINE)
                for match in matches:
                    if isinstance(match, list):
                        old_url = match[0]
                    else:
                        old_url = match
                    description = self.replace_images(description, old_url)
                regex = r"<a.+?href=\"(.+?)\".+?/?>"
                matches = re.findall(regex, description, re.MULTILINE)
                for match in matches:
                    if isinstance(match, list):
                        old_url = match[0]
                    else:
                        old_url = match
                    description = self.replace_category_links(
                        description, old_url)
                return description
        except Exception:
            print(traceback.format_exc())
        return False


def main():
    product = Product('products.csv')
    signal.signal(signal.SIGINT, product.signal_handler)
    product.run()


if __name__ == '__main__':
    main()
