# addresschecker
Pure Python Address Spell Checking based on [Peter Norvig's Blog Post](https://norvig.com/spell-correct.html) and [Tyler Barrus's pyspellchecker Package](https://github.com/barrust/pyspellchecker).

## Quick Start

After installation, we can easily use the `corrections()` member function in the `AddressChecker()`:

```python
from addresschecker import Addresschecker

address_checker = Addresschecker()
target_address = '1410 NE Campuus Parkwayy'       # the input can be a single word or whole address
address_checker.corrections(target_address)       # correction() will return the top-k candidates
```

## Incrementally Update Word Frequency List

We also provide method to incrementally update the word frequency list:

```python
from addresschecker import AddressChecker

textfile_path = 'incremental_training_data.txt'

address_checker = AddressChecker()
address_checker._word_frequency._load_textfile(textfile_path)
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


## Note
This work is part of UW ENGINE(Electrical & Computer Engineering, Innovation and Entrepreneurial) capstone program with Telenav in 2019/2020. For more information please visit [UW ENGINE](https://www.ece.uw.edu/entrepreneurship/entrepreneurial-capstone/). 

