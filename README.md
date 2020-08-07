# ibib

This module provides the `InteractiveBibtex` class that allows you to interact
with your bibtex database through a word cloud. 

Dependencies include a modified version of the `word_cloud` package:
  https://github.com/ewquon/word_cloud
This version includes a simple function to identify keywords from a word cloud
based on the text color (assumed to be unique). The added function in
`wordcloud/wordcloud.py` is:
```python
def get_word_by_color(self,rgb):
    if rgb == ImageColor.getcolor(self.background_color,mode='RGB'):
        return None
    selected = None
    for wordlayout in self.layout_:
        word,scale = wordlayout[0]
        colorstr = wordlayout[4]
        if colorstr == 'rgb({:d}, {:d}, {:d})'.format(*rgb):
            selected = word
            break
    return selected
```

I run `ibib.py` with a Zotero/Better-BibTeX bib file (exported with the "keep
updated" option) as input.

![BibTex Keyword Cloud](examples/bib_keyword_cloud.png)
