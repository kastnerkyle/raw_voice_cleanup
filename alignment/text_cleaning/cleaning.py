""" modified from https://github.com/keithito/tacotron """
import re
from . import cleaners

def _clean_text(text, cleaner_names):
  for name in cleaner_names:
    cleaner = getattr(cleaners, name)
    if not cleaner:
      raise Exception('Unknown cleaner: %s' % name)
    text = cleaner(text)
  return text

if __name__ == "__main__":
    text ="In 1492 Mr. Columbus sailed the ocean blue."
    print("Original:", text)
    print("Cleaned:", _clean_text(text, ["english_cleaners"]))

    text ="In 1492 Mr. Columbus sailed the ocean blue."
