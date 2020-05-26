from __future__ import absolute_import, division, unicode_literals

import os
import json
import string
from collections import Counter

from .utils import load_file, write_file, _parse_into_words, ENSURE_UNICODE

DEFAULT_DICTIONARY_NAME = "en.char.json.gz"

class AddressChecker(object):
    __slots__ = ["_distance", "_tokenizer", "_case_sensitive", "_word_frequency"]
        
    def __init__(self, distance=2, tokenizer=None, case_sensitive=False, dictionary_name=None):
        """ The AddressChecker is used to correct the misspellings in the \
            address string. The algorithm is based on the work of Peter Norvig \
            (https://norvig.com/spell-correct.html).

        Arguments:
            distance {int} -- The edit distance to use. (default: {2})
            tokenizer {function} -- The method to tokenize string. (default: {None})
            case_sensitive {bool} -- Whether to treat the word in dictionary \
                case-sensitive or not. (default: {False})
            dictionary_name {[str]} -- The path to the word dictionary under resources/. \
                (default: {en.char.json.gz})
        """
        
        self.distance = distance
        self._tokenizer = _parse_into_words if not tokenizer else tokenizer
        self._case_sensitive = case_sensitive
        self._word_frequency = WordFrequency(self._tokenizer, self._case_sensitive)


        # Currently, we focus on the addresses in English only.
        if not dictionary_name:
            dictionary_name = DEFAULT_DICTIONARY_NAME
        self.load_dictionary(dictionary_name=dictionary_name)

    def __contains__(self, key):
        """ Check if the word is in the dictionary.

        Arguments:
            key {[string]} -- Word needs to be checked.

        Returns:
            [bool] -- Whether the word is in the dict.
        """
        key = ENSURE_UNICODE(key)
        return key in self._word_frequency

    def __getitem__(self, key):
        """ Get the frequency of the word in the dictionary.

        Arguments:
            key {[string]} -- The query word.

        Returns:
            [int] -- Frequency of the word in the dict. \
                Return 0 if it's not in the dict.
        """
        key = ENSURE_UNICODE(key)
        return self._word_frequency[key]

    @property
    def distance(self):
        """ Get the edit distance.

        Returns:
            [int] -- The edit distance.
        """
        return self._distance

    @distance.setter
    def distance(self, val):
        """ Set the edit distance.

        Arguments:
            val {[int]} -- The edit distance.

        Raises:
            TypeError: if val is not an integer.
            ValueError: if val is not 1 or 2.
        """
        
        if not isinstance(val, int):
            raise TypeError("The edit distance should be an integer.")
        
        if 0 < val <= 2:
            self._distance = val
        else:
            raise ValueError("The edit distance should be 1 or 2.")
    
    def load_dictionary(self, dictionary_name=None):
        """ Load the word frequency list.

        Raises:
            ValueError: if the language dictionary does not exist.
        """

        here = os.path.dirname(__file__)
        full_filename = os.path.join(here, "resources", dictionary_name)
        if not os.path.exists(full_filename):
            raise ValueError("The language dictionary does not exist!")
        self._word_frequency.load_dictionary(full_filename)
    
    def save_dictionary(self, filepath, encoding="utf-8", gzipped=True):
        """ Save the word frequency list for future use.

        Arguments:
            filepath {[str]} -- The output filepath

        Keyword Arguments:
            encoding {str} -- The encoding method (default: {"utf-8"})
            gzipped {bool} -- Whether to gzip the dictionary or not (default: {True})
        """

        data = json.dumps(self.word_frequency.dictionary, sort_keys=True)
        write_file(filepath, encoding, gzipped, data)
    
    def _split_words(self, sentence):
        """ Split the sentence into words using the tokenizer. Default tokenizer \
            split the sentence on a whitespace.

        Arguments:
            sentence {[str]} -- A sentence need to be splitted.

        Returns:
            [list(str)] -- A list of splitted words.
        """
        sentence = ENSURE_UNICODE(sentence)
        return self._tokenizer(sentence)
    
    def _need_check(self, word):
        """ Check if the word needs to be checked.

        Arguments:
            word {[str]} -- A query word.

        Returns:
            [bool] -- Whether the word should be checked.
        """
        
        if len(word) == 1 and word in string.punctuation:
            return False
        elif len(word) > self._word_frequency.longest_word_length + 3:
            # magic number to allow removal of up to 2 letters.
            return False
        elif isinstance(word, (float, int)):
            return False
        else:
            return True
    
    def known(self, words):
        """ The subset of words that appear in the dict.

        Arguments:
            words {[list(str)]} -- A list of words.

        Returns:
            [set(str)] -- A subset of words.
        """
        words = [
            ENSURE_UNICODE(w) if self._case_sensitive \
                else ENSURE_UNICODE(w).lower() \
                    for w in words
        ]
        
        res = filter(
            lambda x: x in self._word_frequency.dictionary \
                and self._need_check(x),
            words
        )
        return set(res)
    
    def unknown(self, words):
        """ The subset of words that do NOT appear in the dict.

        Arguments:
            words {[list(str)]} -- A list of words.

        Returns:
            [set(str)] -- A subset of words.
        """
        words = [
            ENSURE_UNICODE(w) if self._case_sensitive \
                else ENSURE_UNICODE(w).lower() \
                    for w in words
        ]
        
        res = filter(
            lambda x: x not in self._word_frequency.dictionary \
                and self._need_check(x),
            words
        )
        return set(res)
    
    def edit_distance_1(self, word):
        """ Return all of the words that are 1 edit dist away from the word.

        Arguments:
            word {[str]} -- A query word.

        Returns:
            [set(str)] -- A list of words.
        """
        word = ENSURE_UNICODE(word)
        if not self._case_sensitive:
            word = word.lower()
        
        if not self._need_check(word):
            return set([word])        
        
        letters = self._word_frequency.letters
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]

        # Joining multiple sets can be improved by itertools.
        return set(deletes + transposes + replaces + inserts)
    
    def edit_distance_2(self, word):
        """ Return all of the words that are 2 edit dist away from the word.

        Arguments:
            word {[str]} -- A query word.

        Returns:
            [set(str)] -- A list of words.
        """
        word = ENSURE_UNICODE(word)
        if not self._case_sensitive:
            word = word.lower()

        return set(
            w2 for w1 in self.edit_distance_1(word) \
                for w2 in self.edit_distance_1(w1)
        )

    def candidates(self, word):
        """ Helper of returning all of the potential spelling corrections of \
            a word according to the edit distance.

        Arguments:
            word {[str]} -- A query word.

        Returns:
            [set(str)] -- A set of possible corrected words.
        """
        word = ENSURE_UNICODE(word)
        if not self._need_check(word):
            return set([word])
        if word in self._word_frequency._valid_abbreviation:
            return set([word])
        
        # Obtain edit dist 1 candidates
        res_1 = self.edit_distance_1(word)
        known_res_1 = self.known(res_1)
        if known_res_1: return known_res_1

        # Obtain edit dist 2 candidates if all of the 
        # edit dist 1 candidates are unknown.
        res_2 = set()
        if self._distance == 2:
            for w in res_1:
                res_2.update(self.edit_distance_1(w))
            known_res_2 = self.known(res_2)
            if known_res_2: return known_res_2
        return set([word])
    
    def corrections(self, sentence, k=10, method="naive"):
        """ Return the top-k candidates of each word in a given sentence.

        Arguments:
            word {[type]} -- A query sentence.
            k {int} -- Number of candidates to return. (default: {10})
            method {str} -- The score function. (default: {"naive"})

        Raises:
            ValueError: if the score function is invalid.

        Returns:
            [list(tuple(str, list(str)))] -- A list of (query word, candidates).
        """
        outputs = []
        for word in self._split_words(sentence):
            if word.isdigit():
                candidates = [word]
            else:
                candidates = self._corrections(word, k=k, method=method)
            outputs.append(
                (word, candidates)
            )
        return outputs

    def _corrections(self, word, k, method="naive"):
        """ Helper for returning the top-k candidates of the word for the corrected misspelling.

        Arguments:
            word {[type]} -- A query word.
            k {int} -- Number of candidates to return.
            method {str} -- The score function. (default: {"naive"})

        Raises:
            ValueError: if the score function is invalid.

        Returns:
            [list(str)] -- A list of candidates.
        """

        if method not in ["naive"]:
            raise ValueError("Invalid method for word score calculation.")

        word = ENSURE_UNICODE(word)
        candidates = list(self.candidates(word))
        candidates = sorted(
            candidates,
            reverse=True,
            key=lambda x: self.calculate_word_score(x, method=method)
        )
        top_k_candidates = candidates[:k]
        # top_k_candidates_with_scores = [(x, self.calculate_word_score(x)) for x in top_k_candidates]
        # return top_k_candidates_with_scores
        return top_k_candidates

    def calculate_word_score(self, word, method="naive"):
        """Calculate the score of the word. \
            The score indicates how "correct" the word is.

        Arguments:
            word {[str]} -- A query word.
            method {str} -- The score function. (default: {"naive"})

        Raises:
            ValueError: if the score function is invalid.

        Returns:
            [double] -- The score of the word.
        """
        score = 0.0
        if method == "naive":
            score = self._word_score_naive(word)
        else:
            raise ValueError("Invalid method for word score calculation.")
            
        return score        

    def _word_score_naive(self, word):
        """ Calculate the probability of the word in the dict.

        Arguments:
            word {[str]} -- A query word.

        Returns:
            [double] -- The score of the word.
        """
        total_words = self._word_frequency.total_words
        word = ENSURE_UNICODE(word)
        return self._word_frequency.dictionary[word] / total_words
    

class WordFrequency(object):
    __slots__ = [
        "_valid_char",
        "_valid_abbreviation",
        "_dictionary",
        "_total_words",
        "_unique_words",
        "_letters",
        "_tokenizer",
        "_case_sensitive",
        "_longest_word_length"
    ]

    def __init__(self, tokenizer=None, case_sensitive=False):
        """ The word frequency list of the language.

        Arguments:
            tokenizer {function} -- The method to tokenize string. (default: {None})
            case_sensitive {bool} -- Whether to treat the word in dictionary \
                case-sensitive or not. (default: {False})
        """
       
        self._valid_char = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-\'\"0123456789.()')
        self._valid_abbreviation = set(abbr.lower() for abbr in [
            'NW', 'NE', 'SW', 'SE', 'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', \
            'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', \
            'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'Ave', 'Rd', 'St', 'Ln', 'Dr', 'Way', 'Blvd'])

        self._dictionary = Counter()
        self._total_words = 0
        self._unique_words = 0
        self._letters = set()
        self._case_sensitive = case_sensitive
        self._longest_word_length = 0
        self._tokenizer = _parse_into_words if not tokenizer else tokenizer

    def __str__(self):
        return "Unique words: {}\t Thresholding: {}\t".format(self._unique_words, min(self._dictionary))

    def __contains__(self, key):
        key = ENSURE_UNICODE(key)
        if not self._case_sensitive:
            key = key.lower()
        return key in self._dictionary    

    def __getitem__(self, key):
        key = ENSURE_UNICODE(key)
        if not self._case_sensitive:
            key = key.lower()    
        return self._dictionary.get(key, 0)    

    def __str__(self):
        th = self._dictionary[min(self._dictionary, key=self._dictionary.get)]
        return "Total words: {}\t Unique words: {}\t Thresholding: {}\t".format(self._total_words, self._unique_words, th)
    
    @property
    def dictionary(self):
        """ Get the word frequency list where 
            - key: word
            - value: word frequency (int)

        Returns:
            [dict] -- The word frequency dictionary.
        """
        return self._dictionary
    
    @property
    def total_words(self):
        """ Get the sum of word frequency of the language dictionary.

        Returns:
            [int] -- Sum of word frequency.
        """
        return self._total_words
    
    @property
    def unique_words(self):
        """ Get the number of unique words in the language dictionary.

        Returns:
            [int] -- Number of unique words.
        """
        return self._unique_words

    @property
    def letters(self):
        """ Get the unique letters in the language dictionary.

        Returns:
            [set] -- Set of unique letters.
        """
        return self._letters

    @property
    def longest_word_length(self):
        """ Get the length of the longest word in the language dictionary.

        Returns:
            [int] -- Length of the longest word.
        """
        return self._longest_word_length    

    def _update_dictionary(self):
        """ Update the dictionary. """
        self._longest_word_length = 0
        self._total_words = sum(self._dictionary.values())
        self._unique_words = len(self._dictionary.keys())
        self._letters = set()
        for key in self._dictionary:
            if len(key) > self._longest_word_length:
                self._longest_word_length = len(key)
            self._letters.update(key)

    def tokenize(self, sentence):
        """ Split the sentence into words using the tokenizer. \
            Default tokenizer split the sentence on a whitespace or punctuation except:
                1. underscore (_)
                2. pound sign (#)
                3. apostrophe (')

        Arguments:
            sentence {[str]} -- A sentence need to be splitted.

        Yields:
            [list(str)] -- A list of splitted words.
        """
        sentence = ENSURE_UNICODE(sentence)
        for word in self._tokenizer(sentence):
            yield word if self._case_sensitive else word.lower()
    
    def keys(self):
        """ Iterator of keys (word) in the dictionary.

        Yields:
            [words] -- The words in the dict.
        """
        for key in self._dictionary.keys():
            yield key
    
    def items(self):
        """ Iterator of the items (word, freq) in the dictionary.

        Yields:
            [str] -- The word in the dict.
            [int] -- The corresponding word frequency in the dict.
        """
        for key in self._dictionary.keys():
            yield key, self._dictionary[key]

    def load_dictionary(self, filename, encoding="utf-8"):
        """ Load a dictionary.

        Arguments:
            filename {[str]} -- Filename of the dictionary.
            encoding {str} -- The encoding method. (default: {"utf-8"})
        """
        print("Loading Dictionary: {}".format(filename))

        with load_file(filename, encoding) as data:
            data = data if self._case_sensitive else data.lower()
            self._dictionary.update(json.loads(data, encoding=encoding))
            self._update_dictionary()

        print("Dictionary Loaded!")

    def load_text_file(self, filename, encoding="utf-8", tokenizer=None):
        """ Load from a text file to build the dictionary.

        Arguments:
            filename {[str]} -- Filename of the text file.
            encoding {str} -- The encoding method. (default: {"utf-8"})
            tokenizer {function} -- The method to tokenize string. (default: {None})
        """
        with load_file(filename, encoding=encoding) as data:
            self._load_text(data, tokenizer)
            
    def load_sentence(self, sentences, encoding='utf-8', tokenizer=None):
        for sentence in sentences:
            self._load_text(sentence, tokenizer)

    def _load_text(self, text, tokenizer=None):
        """ Process the text in the text file to build the dictionary.

        Arguments:
            text {[str]} -- Input text string.

        Keyword Arguments:
            tokenizer {[function]} -- The method to tokenize string. (default: {None})
        """
        text = ENSURE_UNICODE(text)
        if tokenizer:
            words = [w if self._case_sensitive else w.lower() for w in tokenizer(text)]
        else:
            words = self.tokenize(text)

        self._dictionary.update(words)
        self._update_dictionary()
    
    def add_words(self, words):
        """ Add a list of words to the dictionary.

        Arguments:
            words {[list(str)]} -- A list of words.
        """
        words = [ENSURE_UNICODE(w) for w in words]
        self._dictionary.update(
            [word if self._case_sensitive else word.lower() for word in words]
        )
        self._update_dictionary()

    def pop(self, word, default=None):
        """ Remove the word and return the corresponding word frequency. \
            Return default if not found

        Arguments:
            key {[str]} -- A query word.
            default {[obj]} -- Return this object if not found (default: {None})

        Returns:
            [int] -- The corresponding word frequency.
        """
        word = ENSURE_UNICODE(word)
        if not self._case_sensitive:
            word = word.lower()

        return self._dictionary.pop(word, default)

    def remove_chars(self):
        """ Remove chars that is not on self._valid_char 

        Argumemts:
            None
        """
        chars = [ENSURE_UNICODE(c) for c in self._valid_char]
        for char in chars:
            for word in self._dictionary.items():
                if char in word:
                    self._dictionary.pop(word)
        self._update_dictionary()
        

    def remove_words(self, words):
        """ Remove a list of words from the dictionary.

        Arguments:
            words {[list(str)]} -- A list of words.
        """
        for word in words:
            self._dictionary.pop(word)
        self._update_dictionary()

    def remove_words_by_threshold(self, threshold=5):
        """ Remove words that its frequency is less than or equal to the given threshold.

        Arguments:
            threshold(int)
        """
        keys = [x for x in self._dictionary.keys()]
        for key in keys:
            if self._dictionary[key] <= threshold:
                self._dictionary.pop(key)
        self._update_dictionary()

