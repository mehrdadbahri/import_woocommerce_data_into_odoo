#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
import xmlrpc.client
import configparser
from pathlib import Path


class API(object):

    def __init__(self):
        try:
            self.get_config()
            self.uid, self.models = self.connect()
        except Exception:
            print(traceback.format_exc())

    def get_config(self):
        configs = configparser.ConfigParser()
        path = Path.home() / 'odoo_api.ini'
        configs.read(path)
        self.db = configs['database']['db']
        self.username = configs['database']['username']
        self.password = configs['database']['password']
        self.url = configs['database']['url']

    def connect(self):
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(
            self.url))
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(
            self.url))
        return uid, models

    def search_read(self, model, domain, fields, limit=False):
        records = self.models.execute_kw(self.db, self.uid, self.password,
                                         model, 'search_read', [domain], {
                                             'fields': fields,
                                             'limit': limit
                                         })
        return records

    def create(self, model, vals):
        record_id = self.models.execute_kw(self.db, self.uid, self.password,
                                           model, 'create', vals)
        return record_id

    def update(self, model, ids, vals):
        self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            'write',
            [ids, vals]
        )

    def unlink(self, model, ids):
        record_id = self.models.execute_kw(self.db, self.uid, self.password,
                                           model, 'unlink', [ids])
        return record_id

    def get_record_id_by_external_identifier(self, model, name):
        model = 'ir.model.data'
        domain = [['model', '=', model]]
        if type(name) == str:
            domain.append(['name', '=', name])
        else:
            domain.append(['name', 'in', name])
        fields = ['res_id']
        return self.api.search_read(model, domain, fields)[0]['res_id']
