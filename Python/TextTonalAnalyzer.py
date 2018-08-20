# Copyright © 2018. All rights reserved.
# Author: German Yakimov

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import csv
import time
from threading import Thread
from Python.Services.DatabaseCursor import DatabaseCursor
from Python.Services.Lemmatizer.Lemmatizer import Lemmatizer
from Python.Services.DocumentPreparer import DocumentPreparer
from Python.Services.TextWeightCounter import TextWeightCounter
from Python.Services.Classifier import Classifier
from Python.Services.Logger import Logger
from Python.Services.Configurator import Configurator
from Python.Services.PathService import PathService


class TextTonalAnalyzer:
    def __init__(self, classifier_name='NBC'):
        # Services
        self._configurator = Configurator()
        self._configurator.configure()

        self._database_cursor = DatabaseCursor()
        self._document_preparer = DocumentPreparer()
        self._text_weight_counter = TextWeightCounter()
        self._classifier = Classifier()
        self.__logger = Logger()
        self._lemmatizer = Lemmatizer()
        self._path_service = PathService()

        if not self.__logger.configured:
            self.__logger.configure()

        # Data
        self._classifier_name = classifier_name

        self._text = None
        self.tonal = None
        self.probability = 0

        self._unigrams = None
        self._bigrams = None
        self._trigrams = None

        self._unigrams_weight = None
        self._bigrams_weight = None
        self._trigrams_weight = None

        self._unigrams_weight_counted = False
        self._bigrams_weight_counted = False
        self._trigrams_weight_counted = False

        self.__logger.info('TextTonalAnalyzer was successfully initialized.', 'TextTonalAnalyzer.__init__()')

    def _reset_data(self):
        self._text = None
        self.tonal = None
        self.probability = 0

        self._unigrams = None
        self._bigrams = None
        self._trigrams = None

        self._unigrams_weight = None
        self._bigrams_weight = None
        self._trigrams_weight = None

        self._unigrams_weight_counted = False
        self._bigrams_weight_counted = False
        self._trigrams_weight_counted = False

        self.__logger.info('Data was successfully reset.', 'TextTonalAnalyzer._reset_data()')

    def _split_into_unigrams(self):
        self._unigrams = self._document_preparer.split_into_unigrams(self._text)

    def _split_into_bigrams(self):
        self._bigrams = self._document_preparer.split_into_bigrams(self._text)

    def _split_into_trigrams(self):
        self._trigrams = self._document_preparer.split_into_trigrams(self._text)

    def _document_prepare(self):
        self._unigrams = self._document_preparer.split_into_unigrams(self._text)
        self._bigrams = self._document_preparer.split_into_bigrams(self._text)
        self._trigrams = self._document_preparer.split_into_trigrams(self._text)

    def _check_text_in_dataset(self):
        path_to_dataset = self._path_service.get_path_to_dataset('dataset_with_unigrams.csv')

        with open(path_to_dataset, 'r', encoding='utf-8') as file:
            dataset = csv.reader(file)
            for doc in dataset:
                doc = ''.join(doc).split(';')
                if doc[0] == self._text:
                    self.tonal = doc[1]
                    self.probability = 1

                    self.__logger.info('Document is in dataset.', 'TextTonalAnalyzer._check_text_in_dataset()')
                    return True

        return False

    def _count_weight_by_unigrams(self):
        self._unigrams_weight = self._text_weight_counter.count_weight_by_unigrams(self._unigrams)
        self._unigrams_weight_counted = True

    def _count_weight_by_bigrams(self):
        self._bigrams_weight = self._text_weight_counter.count_weight_by_bigrams(self._bigrams)
        self._bigrams_weight_counted = True

    def _count_weight_by_trigrams(self):
        self._trigrams_weight = self._text_weight_counter.count_weight_by_trigrams(self._trigrams)
        self._trigrams_weight_counted = True

    def detect_tonal(self, text):
        self._reset_data()

        self._text = self._lemmatizer.lead_to_initial_form(text)

        if not self._text:
            self.tonal = 'Unknown'

            self.__logger.warning('Text is empty.', 'TextTonalAnalyzer.detect_tonal()')
            return None

        self._document_prepare()

        if not self._check_text_in_dataset():
            # self._unigrams_weight = self._text_weight_counter.count_weight_by_unigrams(self._unigrams)
            # self._bigrams_weight = self._text_weight_counter.count_weight_by_bigrams(self._bigrams)
            # self._trigrams_weight = self._text_weight_counter.count_weight_by_trigrams(self._trigrams)

            threads = list()
            threads.append(Thread(target=self._count_weight_by_unigrams, args=()))
            threads.append(Thread(target=self._count_weight_by_bigrams, args=()))
            threads.append(Thread(target=self._count_weight_by_trigrams, args=()))

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            while not self._unigrams_weight_counted or not self._bigrams_weight_counted or \
                    not self._trigrams_weight_counted:
                time.sleep(0.01)

            self._classifier.configure(self._classifier_name, self._unigrams_weight, self._bigrams_weight,
                                       self._trigrams_weight)
            self.tonal, self.probability = self._classifier.predict()
            self.__logger.page_break()
