# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

"""Elastic Search Pipeline for scrappy expanded with support for multiple items"""

from datetime import datetime
from elasticsearch import Elasticsearch, helpers
from six import string_types

import logging
import hashlib
import types


class InvalidSettingsException(Exception):
    pass


class TuhuPipeline(object):
    settings = None
    es = None
    items_buffer = []

    @classmethod
    def validate_settings(cls, settings):
        def validate_setting(setting_key):
            if settings[setting_key] is None:
                raise InvalidSettingsException('%s is not defined in settings.py' % setting_key)

        required_settings = {'ELASTICSEARCH_INDEX', 'ELASTICSEARCH_TYPE'}

        for required_setting in required_settings:
            validate_setting(required_setting)

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls()
        ext.settings = crawler.settings

        cls.validate_settings(ext.settings)

        es_servers = ext.settings.get('ELASTICSEARCH_SERVERS')
        es_servers = es_servers if isinstance(es_servers, list) else [es_servers]

        ext.es = Elasticsearch(hosts=es_servers, timeout=ext.settings.get('ELASTICSEARCH_TIMEOUT', 60))
        return ext

    def process_item(self, item, spider):
        if isinstance(item, types.GeneratorType) or isinstance(item, list):
            for each in item:
                self.process_item(each, spider)
        else:
            self.index_item(item)
            logging.debug('Item sent to Elastic Search %s' % self.settings['ELASTICSEARCH_INDEX'])
            print('---------------------------------------------------------------------------')
            print('indexing item now!!!!!')
            return item

    def get_unique_key(self, unique_key):
        if isinstance(unique_key, list):
            unique_key = unique_key[0].encode('utf-8')
        elif isinstance(unique_key, string_types):
            unique_key = unique_key.encode('utf-8')
        else:
            raise Exception('unique key must be str or unicode')

        return unique_key

    def index_item(self, item):

        index_name = self.settings['ELASTICSEARCH_INDEX']
        index_suffix_format = self.settings.get('ELASTICSEARCH_INDEX_DATE_FORMAT', None)
        index_suffix_key = self.settings.get('ELASTICSEARCH_INDEX_DATE_KEY', None)
        index_suffix_key_format = self.settings.get('ELASTICSEARCH_INDEX_DATE_KEY_FORMAT', None)

        if index_suffix_format:
            if index_suffix_key and index_suffix_key_format:
                dt = datetime.strptime(item[index_suffix_key], index_suffix_key_format)
            else:
                # this statement is in use
                dt = datetime.now()
            index_name += "-" + datetime.strftime(dt,index_suffix_format)
        elif index_suffix_key:
            index_name += "-" + index_suffix_key

        index_action = {
            '_index': index_name,
            '_type': self.settings['ELASTICSEARCH_TYPE'],
            '_source': dict(item)
        }

        if self.settings['ELASTICSEARCH_UNIQ_KEY'] is not None:
            item_unique_key = item[self.settings['ELASTICSEARCH_UNIQ_KEY']]
            unique_key = self.get_unique_key(item_unique_key)
            item_id = hashlib.sha1(unique_key).hexdigest()
            index_action['_id'] = item_id
            logging.debug('Generated unique key %s' % item_id)

        self.items_buffer.append(index_action)

        if len(self.items_buffer) >= self.settings.get('ELASTICSEARCH_BUFFER_LENGTH', 100):
            self.send_items()
            self.items_buffer = []

        print('indexing an item now')

    def send_items(self):
        helpers.bulk(self.es, self.items_buffer)
        print('sending items to Elasticsearch now!')

    def close_spider(self, spider):
        if len(self.items_buffer):
            self.send_items()
