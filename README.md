# addresschecker
Pure Python Address Spell Checking based on [Peter Norvig's Blog Post](https://norvig.com/spell-correct.html) and [Tyler Barrus's pyspellchecker Package](https://github.com/barrust/pyspellchecker).

## Requirement
* Python >= 2.7 (Python3 Preferred!)


## Installation

To install from source
```python
git clone https://github.com/andgitisaac/addresschecker.git
cd addresschecker
python setup.py install
```

## Quick Start

After installation, one should be able to use the `AddressChecker` easily.

```python
from addresschecker import Addresschecker

address_checker = Addresschecker()

# the input can be just a single word or the entire address
target_address = "1410 NE Campuus Parkwayy"

# By default, it will return the top-10 candidates of each word
address_checker.corrections(target_address)
```

If you want to obtain all possible candidates, instead of top-K, for one single word, give `candidates()` a shot.

```python
target_word = "Washinton"

# This will give you all candidates according to the current word frequency list.
address_checker.candidates(target_word)
```

If you'd like to tune the model, look at here:

```python
"""Case Sensitive Configuration"""

# The query sentences/words are treated as case sensitive.
# Note that one might need to re-train their own word frequency list from scratch when doing this.
address_checker = Addresschecker(case_sensitive=True)

"""Tokenizer Configuration"""

# One can define their own tokenizer to parse the input query.
def custom_tokenizer(text):
    return re.findall(r"\w+", text)

address_checker = Addresschecker(tokenizer=custom_tokenizer)


"""Edit Distance Configuration"""

# The generated candidates will be limited to words that are onle 1 edit distance away from the query word.
address_checker = Addresschecker(distance=1)
```


## Load The Word Frequency List

We've trained the model with several corpora that are mentioned below. The default word frequency list is `en.char.json.gz` under the `resources` folder. If you have your own, place it under the `resources` folder and initialize the `Addresschecker` with it by:

```python
# It should be something like: *.json.gz
dictionary_name = "dictionary_name"

# You should see the message on stdout to check whether it has been imported
address_checker = Addresschecker(dictionary_name=dictionary_name)
```

## Update The Word Frequency List

The `Addresschecker` has the ability to learn incrementally. Here we provide 3 different methods to update the word frequency list:

### Update from another word frequency list

```python
dictionary_path = "path/to/your/dictionary"

address_checker._word_frequency.load_dictionary(dictionary_path)
```

### Update from a text file

```python
textfile_path = "path/to/your/textfile"

address_checker._word_frequency._load_text_file(textfile_path)
```

### Update from list of sentences

```python
sentences = ["Example sentence 1", "Example sentence 2"]

address_checker._word_frequency._load_sentence_(sentences)
```

## Export The Word Frequency List

In case you want to save the current word frequency list, you can:

```python
new_model_path = "path/to/your/new/model"

# This should save your model in a *.json.gz file
address_checker.save_dictionary(new_model_path)
```

## Other Methods
These are some member functions under `Addresschecker` that are available:

* `known()` : Returns the words that are in the current word frequency list
* `unknown()` : Returns the words that are not in the current word frequency list
* `calculate_word_score()` : Returns the score of the word. The score suggests how "correct" is the word according to the word frequency list.

## Estabilshed Word Frequency List

In order to develop a word frequency list that can correctly detect the misspellings, we modified the model from pyspellchecker with the following corpus:

- [OpenSubtitles](http://opus.nlpl.eu/OpenSubtitles2018.php): 3.2G entries of tokens from English TV and movies subtitles
- [OpenAddress](https://github.com/openaddresses/openaddresses): 100M entries of real address in United States
- Telenav User Queries: 2M entries of real user queries from Telenav

Current word frequency list contain 158,751 unique words.

## Note
This work is part of UW ENGINE(Electrical & Computer Engineering, Innovation and Entrepreneurial) capstone program with Telenav in 2019/2020. For more information please visit [UW ENGINE](https://www.ece.uw.edu/entrepreneurship/entrepreneurial-capstone/).

## Credits
* Peter Norvig's post [How to Write a Spelling Corrector](https://norvig.com/spell-correct.html) for the spell checking algorithm
* Tyler Barrus's [project](https://github.com/barrust/pyspellchecker) for providing the basis of spell checker
