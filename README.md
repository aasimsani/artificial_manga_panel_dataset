# Artifical Manga Panel Dataset - AMP-D

## What is in this repo?
This repository contains the associated files and links to create an artificial manga panel dataset

## Current progress:

Steps:
- [x] Find relevant japanese dialogue dataset
- [x] Find manga like japanese fonts
- [x] Find different text bubble types
- [ ] Find manga images or other black and white images to use to fill panels
- [ ] Create a few manga page layout templates
- [ ] Create manga panels by combining the above elements
- [ ] Create font transformations
- [ ] Replace layout templates with manga panel generator
- [ ] Upload dataset to Kaggle

## Data variety
- 196 fonts with >80% character coverage
- 728 Speech bubble types (182 untransformed)
- 2,801,388 sentence pairs in Japanese and English

### How this dataset was made?
1. Downloaded JESC dataset to get sentence pairs
2. Found fonts from fonts website mentioned below
3. Downloaded Tagged Anime Illustrations dataset from Kaggle
4. Found and created different types of speech bubbles
5. Verified which fonts were viable and could cover at least 80% of the characters in the JESC dataset
6. Converted all the images to black and white 
7. Created default layout set/layouting engine
8. Created renderer which generates images by sampling from the text, fonts, images, speech bubbles and layouts
9. Used renderer to create dataset of fixed size

### Resources used:

1. [JESC dataset](https://nlp.stanford.edu/projects/jesc/)
2. [Tagged anime illustrations Kaggle dataset](https://www.kaggle.com/mylesoneill/tagged-anime-illustrations)
3. [Comic book pages Kaggle dataset](https://www.kaggle.com/cenkbircanoglu/comic-books-classification)
4. [Fonts allowed for commerical use from Free Japanese Fonts](https://www.freejapanesefont.com/) - Licences are on individual pages
5. [Object Detection for Comics using Manga109 Annotations](https://arxiv.org/pdf/1803.08670.pdf) - Used as benchmark
6. [Speech bubbles PSD file](https://www.deviantart.com/zombiesmile/art/300-Free-Speech-Bubbles-Download-419223430)

### Licences and Legal
**JESC dataset**
```
@ARTICLE{pryzant_jesc_2017,
   author = {{Pryzant}, R. and {Chung}, Y. and {Jurafsky}, D. and {Britz}, D.},
    title = "{JESC: Japanese-English Subtitle Corpus}",
  journal = {ArXiv e-prints},
archivePrefix = "arXiv",
   eprint = {1710.10639},
 keywords = {Computer Science - Computation and Language},
     year = 2017,
    month = oct,
}             ```
```

[**Speech bubble PSD file Licence**](https://friendlystock.com/terms-of-use/)


### How does the layouting engine work?
1. Each Manga Page Image is represented by a JSON file. The page description contains the following
    1. Layout types and how they're denoted (here for easy search of particular panel types)
        1. Horizontal panels only - ```h```
        2. Vertical panel only - ```v```
        3. Vertical and horizontal panels - ```vh```
        4. All of the above with panel shape transforms - ```vht``` or ```ht```
        5. All of the above on a background - ```vhtb```
        6. All of the above on a background with panel xy mis-alignment (sin/wave/etc) - ```vhtbm```
        7. All of the above with white space insertions - ```vhtbmw```
    2. Page size
    3. Page type (currently only single)
    4. Panel boundary widths
    5. Panel boundary types
2. Each Page then has N panels layed out in a particular format which is described as follows:
    1. Each panel has a rectangular baseline and a transformation matrix that changes it if needed. Each panel is represented as follows:
      1. Coords + Dims: (((topx, topy), (bottomx, bottomy), width, height))
      2. Transformations: ()
    2. Each panel also has a list of images that it's comprised of and how they've been inserted.
        1. Coords + Dims: (topx, topy, bottomx, bottomy, width, height)
        2. Transformations: ()
3. With the Panels each page also has a number of text bubbles on them. Usually the number being within (#panels-2 <= #bubbles <= #panels+2) of each panel on the depending on how large the panel is. Most bubbles are within the vicinity of a panel or within them with a small % of them peaking between panels. Each bubble has the following properties:
    1. Bubble type
    2. Bubble text (as a reference)
    3. Bubble text font
    4. Bubble text font size
    5. Coords + Dims: (topx, topy, bottomx, bottomy, width, height) 
    6. Transformations: ()