# addresschecker
Pure Python Address Spell Checking based on [Peter Norvig's Blog Post](https://norvig.com/spell-correct.html) and [Tyler Barrus's pyspellchecker Package](https://github.com/barrust/pyspellchecker).


## Installation

To install from source
```python
git clone https://github.com/andgitisaac/addresschecker.git
cd addresschecker
python setup.py install
```

## Usage

After installation, one should be able to use the `AddressChecker` easily.

```python
from addresschecker import Addresschecker

address_checker = Addresschecker()

# the input can be just a single word or the entire address
target_address = "1410 NE Campuus Parkwayy"

# By default, it will return the top-10 candidates of each word
address_checker.corrections(target_address)
```

If you want to obtain all possible candidates for one single word, give `candidates()` a shot.


## Incrementally Update Word Frequency List

We also provide method to incrementally update the word frequency list:

```python
from addresschecker import AddressChecker

textfile_path = 'incremental_training_data.txt'

address_checker = AddressChecker()
address_checker._word_frequency._load_text_file(textfile_path)
```

To save the new word frequency list:
```python
address_checker.save_dictionary(new_model_path)
```

## Current Word Frequency List

In order to develop a word frequency list that can correctly detect the misspellings, we modified the model from pyspellchecker with the following corpus:

- [OpenSubtitles](http://opus.nlpl.eu/OpenSubtitles2018.php): 3.2G entries of tokens from English TV and movies subtitles
- [OpenAddress](https://github.com/openaddresses/openaddresses): 100M entries of real address in United States
- Telenav User Queries: 2M entries of real user queries from Telenav

Current word frequency list contain 158,751 unique words.

## Note
This work is part of UW ENGINE(Electrical & Computer Engineering, Innovation and Entrepreneurial) capstone program with Telenav in 2019/2020. For more information please visit [UW ENGINE](https://www.ece.uw.edu/entrepreneurship/entrepreneurial-capstone/). 

