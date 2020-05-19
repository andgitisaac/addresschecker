# addresschecker

Pure Python Address Spell Checking based on [Peter Norvig's Blog Post](https://norvig.com/spell-correct.html) and [Tyler Barrus's pyspellchecker Package](https://github.com/barrust/pyspellchecker).

## Quick Start

```python
from addresschecker import Addresschecker

address_checker = Addresschecker()
target_address = '1410 NE Campuus Parkwayy'
address_checker.corrections(target_address)
```

## Incrementally Update Word Frequency List

```python
from addresschecker import Addresschecker

textfile_path = 'incremental_training_data.txt'

address_checker = AddressChecker()
address_checker._word_frequency._load_textfile(textfile_path)
```

```python
address_checker.summary()
```

## Current Word Frequency List

In order to develop a word frequency list that can correctly detect the misspellings, we modified the model from pyspellchecker with the following corpus:

- [OpenSubtitles](http://opus.nlpl.eu/OpenSubtitles2018.php): 3.2G entries of tokens from English TV and movies subtitles
- [OpenAddress](https://github.com/openaddresses/openaddresses): 100M entries of real address in United States
- Telenav User Queries: 2M entries of real user queries from Telenav
