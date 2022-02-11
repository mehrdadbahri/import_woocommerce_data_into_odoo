#!/usr/bin/env python
# -*- coding: utf-8 -*-
import signal
import base64
from api_connector import API
from importer import Import


class Variant(Import):
    updated_ids = []
    not_found_ids = []
    model = 'product.product'

    def __init__(self, data_file):
        self.data_file = data_file
        self.api = API()
        if self.api:
            self.get_imported_products(self)
            return True
        return False

    def get_variants(self):
        model = 'ir.model.data'
        domain = [
            ['model', '=', 'product.product'],
        ]
        fields = ['res_id', 'name']
        self.variants = self.api.search_read(model, domain, fields)

    def process_row(self, row):
        variant = list(filter(
            lambda item: item['name'] == row[0],
            self.variants))
        if not len(variant):
            # print("Product not found: {}".format(row[0]))
            return

        variant_id = variant[0]['res_id']
        try:
            with open("uploads/"+row[1], "rb") as image_file:
                vals = {
                    'image_1920': base64.b64encode(
                        image_file.read()).decode('ascii')
                }
                self.api.update(self.model, [variant_id], vals)
                self.updated_ids.append(variant_id)
        except Exception as e:
            print(e)


def main():
    variant = Variant('variant_imgs.csv')
    signal.signal(signal.SIGINT, variant.signal_handler)
    variant.run()


if __name__ == '__main__':
    main()
