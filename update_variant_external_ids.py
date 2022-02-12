#!/usr/bin/env python
# -*- coding: utf-8 -*-
import signal
from api_connector import API
from importer import Import


class Variant(Import):
    updated_ids = []
    not_found_ids = []
    model = 'product.template'

    def get_variants(self):
        model = 'ir.model.data'
        domain = [
            ['model', '=', 'product.product'],
        ]
        fields = ['res_id', 'name']
        self.variants = self.api.search_read(model, domain, fields)

    def get_attr_values(self):
        model = 'ir.model.data'
        domain = [
            ['model', '=', 'product.attribute.value'],
        ]
        fields = ['res_id', 'name']
        self.attr_values = self.api.search_read(model, domain, fields)

    def process_row(self, row):
        if row[0].split('_')[-1] in self.not_found_ids:
            return
        product = list(
            filter(lambda item: item['name'] == row[0], self.imported_records))
        if not len(product):
            print("Product not found: {}".format(row[0]))
            return

        product_id = product[0]['res_id']

        external_id = list(
            filter(lambda item: item['name'] == 'variant_' + row[1],
                   self.variants))

        if len(external_id):
            return

        attr_value = list(
            filter(lambda item: item['name'] == 'attribiute_value_' + row[2],
                   self.attr_values))
        if not len(attr_value):
            print("ERROR: Couldn't find attr value: {}".format(row[2]))
            return
        value_id = attr_value[0]['res_id']
        model = 'product.product'
        domain = [
            ['product_tmpl_id', '=', product_id],
        ]
        fields = ['id', 'product_template_attribute_value_ids']
        variants = self.api.search_read(model, domain, fields)
        variant = None
        for item in variants:
            template_value_id = item['product_template_attribute_value_ids']
            domain = [
                ['id', '=', template_value_id],
            ]
            fields = ['id', 'product_attribute_value_id']
            model = 'product.template.attribute.value'
            variant_values = self.api.search_read(model, domain, fields,
                                                  1)
            for val in variant_values:
                if val['product_attribute_value_id'][0] == value_id:
                    variant = item['id']
                    break
        if not variant:
            print("Couldn't find the product variant")
            print("product_id: {}\twp_id: {}\tvalue: {}".format(
                product_id, row[2], value_id))
            return

        reference_data = {
            'module': '__import__',
            'model': 'product.product',
            'name': 'variant_' + row[1],
            'res_id': variant
        }
        model = 'ir.model.data'
        self.api.create(model, [reference_data])
        self.updated_ids.append(product_id)


def main():
    variant = Variant('variant_ids.csv')
    signal.signal(signal.SIGINT, variant.signal_handler)
    variant.run()


if __name__ == '__main__':
    main()
