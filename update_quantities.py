#!/usr/bin/env python
# -*- coding: utf-8 -*-
import signal
from importer import Import


class Quantity(Import):
    updated_ids = []
    not_found_ids = []
    model = 'product.template'

    def process_row(self, row):
        if row[1] == "NULL" or int(float(row[1])) == 0:
            return
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
        domain = [
                ['id', '=', product_id],
            ]
        fields = ['product_variant_id']
        product = self.api.search_read(self.model, domain, fields)

        variant_id = product[0]['product_variant_id'][0]
        model = 'product.product'
        vals = {'dropship_qty': int(float(row[1]))}
        self.api.update(model, [variant_id], vals)

        self.updated_ids.append(product_id)


def main():
    quantity = Quantity('quantities.csv')
    signal.signal(signal.SIGINT, quantity.signal_handler)
    quantity.run()


if __name__ == '__main__':
    main()
