#!/usr/bin/env python
# -*- coding: utf-8 -*-
import signal
import phpserialize
from import_products import Product


class VariantProduct(Product):
    created_ids = []
    model = 'product.template'

    def process_row(self, row):
        pid = super().process_row(row)
        if pid and row[14] != "NULL":
            serialized_data = row[14].replace('\\"', '"')
            serialized_data = serialized_data.replace(':\\pa', ':"pa')
            if serialized_data[-1] == '"':
                serialized_data = serialized_data[:-1]
            attributes_data = phpserialize.loads(serialized_data.encode())
            variant_attributes = []
            for key in attributes_data:
                if isinstance(attributes_data[key][b'is_variation'], int):
                    if attributes_data[key][b'is_variation'] == 1:
                        variant_attributes.append(key.decode())
                else:
                    if attributes_data[key][b'is_variation'].decode() == '1':
                        variant_attributes.append(key.decode())
            if len(variant_attributes):
                vals = {
                    'x_wp_variant_attributes': ','.join(variant_attributes)
                }
                self.api.update(self.model, [pid], vals)


def main():
    product = VariantProduct('variant_products.csv')
    signal.signal(signal.SIGINT, product.signal_handler)
    product.run()


if __name__ == '__main__':
    main()
