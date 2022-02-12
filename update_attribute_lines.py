#!/usr/bin/env python
# -*- coding: utf-8 -*-
import signal
import csv
import traceback
from importer import Import


class AttributeLine(Import):
    updated_ids = []
    applied_ids = []
    not_found_ids = []
    model = 'product.template'

    def run(self):
        with open(self.data_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            first = True
            current_product = ''
            rows = []
            try:
                for row in csv_reader:
                    if first:
                        first = False
                        continue
                    if not current_product:
                        current_product = row[0]
                    if row[0] == current_product:
                        rows.append(row)
                        continue

                    self.process_row(row)

                    rows = [row]
                    current_product = row[0]

                    if self.stop:
                        break
            except Exception:
                print(traceback.format_exc())

    def process_row(self, rows):
        if rows[0][0] in self.not_found_ids:
            return
        try:
            if int(rows[0][0]) in self.applied_ids:
                return
        except Exception:
            print(traceback.format_exc())
            return
        product = list(
            filter(
                lambda item: item['name'] == "product_{}".format(rows[0][0]),
                self.imported_records))
        if not len(product):
            # print("Product not found: {}".format(rows[0][0]))
            self.not_found_ids.append(rows[0][0])
            return

        product_id = product[0]['res_id']
        if product_id in self.applied_ids:
            return
        model = 'product.template'
        domain = [
            ['id', '=', product_id],
        ]
        fields = ['x_wp_variant_attributes']
        product = self.api.search_read(model, domain, fields, 1)

        for row in rows:
            attribute = self.api.get_record_id_by_external_identifier(
                'product.attribute', row[1])
            if not len(attribute):
                print(row[1])
                print("Attribute Not Found")
                continue
            value_external_ids = []
            for item in row[2].split('|'):
                value_external_ids.append('attribiute_value_' + item)
            attr_values = self.api.get_record_id_by_external_identifier(
                'product.attribute.value', value_external_ids)
            if len(attr_values):
                value_ids = [v['res_id'] for v in attr_values]
                if product[0]['x_wp_variant_attributes'] and row[1] in product[
                        0]['x_wp_variant_attributes']:
                    data = {
                        'attribute_id': attribute[0]['res_id'],
                        'product_tmpl_id': product_id,
                        'value_ids': [[6, 0, value_ids]],
                    }
                    print(data)
                    model = 'product.template.attribute.line'
                    self.api.create(model, [data])
                # else:
                #     data = {
                #         'attribute_id': attribute[0]['res_id'],
                #         'extra_product_tmpl_id': product_id,
                #         'value_ids': [[6, 0, value_ids]],
                #     }
                #     models.execute_kw(db, uid, password, 'extra.features.line',
                #                       'create', [data])
        self.updated_ids.append(product_id)


def main():
    line = AttributeLine('lines.csv')
    signal.signal(signal.SIGINT, line.signal_handler)
    line.run()


if __name__ == '__main__':
    main()
