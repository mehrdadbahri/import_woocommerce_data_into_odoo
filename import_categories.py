#!/usr/bin/env python
# -*- coding: utf-8 -*-
import signal
import re
from importer import Import


class Category(Import):
    created_ids = []
    model = 'product.public.category'

    def process_row(self, row):
        if self.already_imported(row[0]):
            return

        data = {
            'name': row[1],
        }
        if row[3]:
            try:
                parent_id = self.api.get_record_id_by_external_identifier(
                    self.model, row[3])
                data['parent_id'] = parent_id
            except Exception:
                # print("Parent not found: {}, ignoring...".format(row[0]))
                return
        if row[2]:
            description = row[2].replace('\\"', '"').replace('\\n', '\n')
            description = description.replace('#^*#', ',')
            regex = r"<img.+?src=\"(.+?)\".+?/?>"
            matches = re.findall(regex, description, re.MULTILINE)
            for match in matches:
                description = self.replace_images(description, match[0])
            data['website_description'] = description

        model = 'product.public.category'
        pid = self.api.create(model, [data])

        self.created_ids.append(pid)

        reference_data = {
            'module': '__import__',
            'model': 'product.public.category',
            'name': row[0],
            'res_id': pid
        }
        model = 'ir.model.data'
        self.api.create(model, [reference_data])


def main():
    category = Category('categories.csv')
    signal.signal(signal.SIGINT, category.signal_handler)
    category.run()


if __name__ == '__main__':
    main()
