#!/usr/bin/env python
# -*- coding: utf-8 -*-
import signal
from importer import Import


class URL(Import):
    updated_ids = []
    not_found_ids = []
    model = 'product.template'

    def process_row(self, row):
        product = list(filter(
            lambda item: item['name'] == row[0],
            self.imported_records))
        if not len(product):
            return
        product = product[0]
        if product['res_id'] in self.updated_ids:
            return

        data = {
            'wp_urls': row[1]
        }

        self.api.update(self.model, [product['res_id']], data)
        self.updated_ids.append(product['res_id'])


def main():
    url = URL('urls.csv')
    signal.signal(signal.SIGINT, url.signal_handler)
    url.run()


if __name__ == '__main__':
    main()
