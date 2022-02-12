#!/usr/bin/env python
# -*- coding: utf-8 -*-
import signal
import json
from importer import Import


class Price(Import):
    updated_ids = []
    not_found_ids = []
    model = 'product.template'

    def process_row(self, row):
        if row[0].split('_')[-1] in self.not_found_ids:
            return
        product = list(
            filter(lambda item: item['name'] == "product_{}".format(row[0]),
                   self.imported_records))
        if not len(product):
            # print("Product not found: {}".format(rows[0][0]))
            self.not_found_ids.append(row[0])
            return
        product_id = product[0]['res_id']
        json_data = row[1].replace('{\\v', '{\\"v').replace('\\"', '"')
        if json_data[-1] == '"':
            json_data = json_data[:-1]
        json_data = json_data.replace('#^*#^', ',')
        data = json.loads(json_data)
        variants = data['f9e544f77b7eac7add281ef28ca5559f']['regular_price']
        if not variants:
            return
        if len(variants.keys()) > 1:
            vals = {'lst_price': 0}
            model = 'product.template'
            self.api.update(model, [product_id], vals)
            for item in variants:
                variant = self.api.get_record_id_by_external_identifier(
                    'product.product', 'variant_' + item)
                if not len(variant):
                    print("Attribute Not Found: {}".format(item))
                    continue
                domain = [['product_tmpl_id', '=', product_id],
                          [
                              'ptav_product_variant_ids', '=',
                              variant[0]['res_id']
                          ]]
                fields = ['id']
                model = 'product.template.attribute.value'
                variant_line = self.api.search_read(model, domain, fields,
                                                    1)
                vals = {'price_extra': int(float(variants[item]))}
                self.api.update(model, [variant_line[0]['id']], vals)
        elif len(variants.keys()) == 1:
            vals = {
                'lst_price': int(float(variants[list(variants.keys())[0]]))
            }
            model = 'product.template'
            self.api.update(model, [product_id], vals)
        self.updated_ids.append(product_id)


def main():
    price = Price('variant_prices.csv')
    signal.signal(signal.SIGINT, price.signal_handler)
    price.run()


if __name__ == '__main__':
    main()
