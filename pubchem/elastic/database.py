import argparse
import logging
import pathlib
import time
from typing import Dict

import elasticsearch
import indigo
import urllib3
from core import info


class ElasticDatabase:
    def __init__(self, arg_ns: argparse.Namespace):
        self.arg_ns = arg_ns
        self.index = arg_ns.elastic_index
        self.session = indigo.Indigo()
        self.es = elasticsearch.Elasticsearch(
            [arg_ns.elastic_url],
            verify_certs=arg_ns.elastic_verify_certs,
            ssl_show_warn=arg_ns.elastic_verify_certs,
        )

    def __bulk(self, body: Dict, tries: int = 0):
        if tries >= 30:
            raise TimeoutError
        try:
            self.es.bulk(index=self.index, body=body)
        except (
            elasticsearch.exceptions.ConnectionTimeout,
            urllib3.exceptions.ReadTimeoutError,
        ) as err_:
            logging.warning(err_)
            time.sleep(5)
            info('Retrying...')
            self.__bulk(body, tries + 1)

    def handler(self, source_file: pathlib.Path):
        docs = []
        indexed: int = 0
        molecule: indigo.IndigoObject
        for indexed, molecule in enumerate(
            self.session.iterateSDFile(str(source_file)), 1
        ):
            try:
                # todo add check for incremental update
                # todo get pubchem id?
                doc = {
                    "smiles": molecule.canonicalSmiles(),
                    "fingerprint": molecule.fingerprint(type='sim')
                    .oneBitsList()
                    .split(' '),
                }
                docs.append({"index": {}})  # todo: add here upsert/update?
                docs.append(doc)
                if len(docs) >= 10000:
                    info(f'Processed {indexed} rows')
                    self.__bulk(docs)
                    time.sleep(1)
                    docs = []
            except indigo.IndigoException as e:
                logging.error("Cannot upload molecule: %s", e)
        if len(docs) > 0:
            info(f'Processed {indexed} rows')
            self.__bulk(docs)
        self.es.indices.refresh(index=self.index)
