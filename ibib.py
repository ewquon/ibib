#!/usr/bin/env python
"""
An interactive bibtex module
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import webbrowser

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from wordcloud import WordCloud

keyword_aliases = {
    # note: keywords are converted to lowercase when the keyword map is created
    'blerg': ['foo','bar'],
    'LES': ['les','large eddy simulation','large-eddy simulation',
            'large-eddy simulation (les)'],
    'WRF': ['wrf','weather research and forecasting model',
            'weather research and forecasting'],
    'ALM': ['alm','actuator line (al) model','actuator line model',
            'actuator line modeling'],
    'ADM': ['adm','actuator disk model','generalized actuator disk model'],
    'CFD': ['cfd','cfd simulation','computational fluid dynamics'],
    'wind turbines': ['wind turbines','wind turbine'],
    'wind farms': ['wind farms','wind farm','wind plants','wind plant'],
    'wakes': ['wakes','turbine wake',
              'wind turbine wake','wind turbine wakes',
              'wind-turbine wake','wind-turbine wakes'],
    'wake modeling': ['wake modeling','wake model','analytical wake model'],
    'wind tunnel experiment': ['wind tunnel experiment','wind tunnels',
                               'wind-tunnel experiment'],
    'shear': ['shear','wind shear','inflow shear'],
    'blade loading': ['blade loading','blade loads'],
    'boundary layer': ['boundary layer','turbulent boundary layer',
                       'planetary boundary layer','atmospheric boundary layer',
                       'convective boundary layer','stable boundary layer'],
}

class InteractiveBibtex(object):
    """Class that processes bibtex for keywords"""
    def __init__(self,bibfile):
        parser = BibTexParser(common_strings=True)
        parser.customization = convert_to_unicode
        with open(bibfile) as bib:
            bibdb = bibtexparser.load(bib, parser=parser)
        self.entries = bibdb.entries
        self.map_keywords()

    def map_keywords(self):
        # create mapping between keywords and articles to read
        keyword_map = {}
        for idx, entry in enumerate(self.entries):
            try:
                keywords = entry['keywords']
            except KeyError:
                continue
            else:
                keywords = keywords.split(',')
            for keyword in keywords:
                keyword = keyword.strip().lower()
                if keyword in keyword_map.keys():
                    keyword_map[keyword].append(idx)
                else:
                    keyword_map[keyword] = [idx]
        total_keywords = sum([len(indices) for keyword,indices in keyword_map.items()])
        #print(total_keywords)
        #print(keyword_map.keys())

        # consolidate identical keywords
        updated_keywords = {}
        for keyword,aliases in keyword_aliases.items():
            newlist = []
            for kw in list(keyword_map.keys()):
                if kw in aliases:
                    newlist += keyword_map.pop(kw)
            if len(newlist) > 0:
                keyword_map[keyword] = newlist
        assert sum([len(indices) for keyword,indices in keyword_map.items()]) == total_keywords
        #for keyword,indices in keyword_map.items():
        #    print(keyword,len(indices))

        # remove duplicates
        for keyword,indices in keyword_map.items():
            keyword_map[keyword] = list(set(indices))

        self.keyword_map = keyword_map
        self.counts = {keyword: len(indices) for keyword,indices in keyword_map.items()}
        self.series = pd.Series(self.counts).sort_values(ascending=False)

    def keyword_counts(self):
        for keyword,count in self.series.iteritems():
            print(keyword,count)
        print(len(self.keyword_map.keys()),'unique keywords',
              'mentioned',self.series.sum(),'times',
              'in',len(self.entries),'entries')

    def keyword_bar_plot(self,figsize=(11,8.5)):
        fig,ax = plt.subplots(figsize=figsize)
        baridx = np.arange(len(self.series))
        ax.bar(baridx,self.series)
        ax.set_xticks(baridx)
        ax.set_xticklabels(self.series.index)
        ax.tick_params(axis='x',labelrotation=90)
        plt.tight_layout()
        return fig,ax

    def word_cloud(self,interactive=False,
                   figsize=(11,8.5),dpi=100,bkg='white',cmap='viridis'):
        """
        Parameters
        ----------
        interactive : False or str
            Interaction may be:
            * "open" : open a random doi
            * "pop" : open a random doi and remove it from the list
        figsize : tuple
            Figure size, kwarg for plt.subplots()
        dpi : int
            Figure resolution, kwarg for plt.subplots()
        bkg : str
            WordCloud background color
        cmap : str or matplotlib colormap
            From which to select text colors
        """
        # generate the word cloud
        wc = WordCloud(width=int(figsize[0]*dpi),height=int(figsize[1]*dpi),
                       background_color=bkg,colormap=cmap)
        wc.generate_from_frequencies(self.counts)
        # show the image
        fig,ax = plt.subplots(figsize=figsize,dpi=dpi)
        img = wc.to_array()
        ax.imshow(img,interpolation='bilinear')
        ax.axis('off')
        plt.tight_layout()
        # create event handlers
        if not interactive==False:
            def on_click(event):
                if not event.inaxes:
                    return
                i,j = int(np.round(event.xdata)), int(np.round(event.ydata))
                selected = wc.get_word_by_color(img[j,i,:])
                if selected is not None:
                    s = f'Articles about {selected}'
                    print(f'\n{s}')
                    print(len(s)*'-')
                    indices = self.keyword_map[selected]
                    if len(indices) == 0:
                        print('No more articles to open')
                        return
                    if interactive in ['open','pop']:
                        to_open = np.random.choice(indices)
                        for idx in indices:
                            authors = self.entries[idx]['author']
                            title = self.entries[idx]['title']
                            if idx == to_open:
                                pre = '* '
                                try:
                                    url = 'https://doi.org/'+self.entries[idx]['doi']
                                except KeyError:
                                    url = 'https://lmgtfy.com/?q='+title.replace(' ','+')
                                webbrowser.open(url,new=2)
                            else:
                                pre = '  '
                            print(pre+authors[:20]+' - '+title[:55])
                        if interactive == 'pop':
                            self.keyword_map[selected].remove(to_open)
            fig.canvas.mpl_connect('button_press_event', on_click)
        # show
        return fig,ax

#------------------------------------------------------------------------------

if __name__ == '__main__':
    import sys
    if len(sys.argv) <= 1:
        sys.exit('Specify bib file')
    bib = InteractiveBibtex(sys.argv[1])
    bib.keyword_counts()
    #bib.keyword_bar_plot()
    #bib.word_cloud()
    bib.word_cloud(interactive='pop')
    plt.show()

