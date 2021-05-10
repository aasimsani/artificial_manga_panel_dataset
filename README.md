# Artifical Manga Panel Dataset - AMP-D
## The problem
I love manga, but can't read Japanese. And Google Translate isn't so great with Japanese text localization and doesn't offer a free solution for OCR+translation. So I decided to build something that'll help me translate the manga more efficiently into English. Additionally, the technology to detect the speech bubbles could also help official translators translate manga faster. Sadly I couldn't find a dataset which was free and publicly available to train my speech bubble detector on so I made this.

## What is in this repo?
This repository contains the associated files and links to create an artificial manga panel dataset.
Here's a sample of an image created with this code:
<br>
<img src="https://github.com/aasimsani/artificial_manga_panel_dataset/blob/main/docs/misc_files/sample.png" width=425>

## Setup and usage
If you just want to use the dataset and not change anything you can find it at <put link to kaggle here>

If you'd like to change the way the creator works, make your own files or contribute to the project pleae follow these instructions

1. Libraqm is required for rendering CJK text properly. Follow instructions [here](https://github.com/HOST-Oman/libraqm)
2. ```pip3 install -r requirements.txt```
3. You can get the base materials for the dataset by [emailing me](mailto:aasimsani05@gmail.com) for the key and then running:
  ```
  export GOOGLE_APPLICATION_CREDENTIALS=config/ampd_key.json
  dvc pull
  ```
4. In case you want to modify individual scripts for scraping or cleaning this downloaded data you can find them in ```main.py```
5. Before you start just run ```python3 main.py --run_tests``` to make sure
you have all the libraries installed and things are working fine
6. Now you can run ```python3 main.py --generate_pages N``` to make pages
  1. You can also run the metadta generation ```python3 main.py --create_page_metadata N``` and the page rendering ```python3 main.py --render_pages```     seperately. The render pages call will read the ```datasets/page_metadata/``` folder to find files to render.
7. You can modify ```preprocessing/config_file.py``` to change how the generator works to render various parts of the page

## Current progress:

Steps:
- [x] Find relevant japanese dialogue dataset
- [x] Find manga like japanese fonts
- [x] Find different text bubble types
- [x] Find manga images or other black and white images to use to fill panels
- [x] Create a few manga page layout templates
- [x] Create manga panels by combining the above elements
- [x] Create font transformations
- [x] Replace layout templates with manga panel generator
- [ ] Upload dataset to Kaggle
- [ ] Create a custom speech bubble creator (Reach goal)

### Data variety
- 196 fonts with >80% character coverage
- 91 unique speech bubble types
- 2,801,388 sentence pairs in Japanese and English
- 337,039 illustration

### How the base dataset was made?
1. Downloaded JESC dataset to get sentence pairs of English and Japanese
2. Found fonts from fonts website mentioned below
3. Downloaded Tagged Anime Illustrations dataset from Kaggle
4. Found and created different types of speech bubbles. Tagged which parts you can render text within.
5. Verified which fonts were viable and could cover at least 80% of the characters in the JESC dataset
6. Converted all the images to black and white 
7. Created default layout set/layouting engine to create pages 
8. Create metadata for these pages from the layouting engine and populate each panel with:
  1. What image the panel comprises of
  2. What textbubble is associated with it and it's metadata (font, text and render data)
9. Bounce page and it's panel's metadata to json in parallel.
9. Used renderer to create dataset from the generated json in parallel.

### How does the creation and rendering work?
#### Creating the metadata
1. Each Manga Page Image is represented by a Page object which is a special type of Panel object which has children panels and those have sub-panels in a tree-like fashion.
2. Each Page has N panels which is determined by segmenting the page into rectangles as follows:
  1. First a top level set of panels are created. e.g. divide the page into 2 rectnagles 
  2. Then based on which type of layout is selected one or both of the panels are further subdivided into panels e.g. I want 4 panels on this page. So I can divide two panels into two, one panel into three and leave one as is, etc.
  3. These "formulas" of layouts for pages are hard coded per number of panels for now.
  4. In addition to this, the dividion of panels into sub-panels is not equal and the panels are sub-divided randomly across one axis. e.g. 1 panel can have 30% of the area and the other 70%.
  5. These panels as they are being subdivided are entered as children of a parent panel resulting in a tree originating at the Page as the root.
3. Once this is done the panels are then are put through various affine transforms and slicing to result in the iconic "Manga Panel" like layout. Refer example above.
4. After the transformations, the panels are then shrunk in size to create panel boundaries which are visible.
5. Once shrinking is done, there's a chance of adding a background to the whole page and subsequently removing a panel or two randomly to create a white space or a foreground effect
6. Once this is done each panel is then populated with a background image which is selected randomly and a number of speech bubbles are created as follows:
  1. First a template image for a speech bubble is selected out of the 91 base templates. This template is then put through a series of transformations. (flipping it horizontally/vertically, rotating it slightly, inverting it, stretching it along the x or y axis)
  2. Along with this the tagged writing area within the bubble is also transformed
  3. Once this is done a selected font, with a random font size and a selected piece of text are then resized such that they can be rendered onto the bubble either top to bottom or left to right depending on a user-defined probability
7. After this the metadata is written into a JSON file
8. This creation of one page sequentially and is wrapped in a single function that allows it to be dumped to JSON in parallel
#### Rendering the pages
1. Once the JSON files are dumped, the folder where they were dumped is scanned, and then each file is loaded again via a load_data method in the Page class which recreates the data. This is then subsequently rendered by each page class's render method. This operation is done concurrently and in parallel for speed.

### Resources used for creating dataset:

1. [JESC dataset](https://nlp.stanford.edu/projects/jesc/)
2. [Tagged anime illustrations Kaggle dataset](https://www.kaggle.com/mylesoneill/tagged-anime-illustrations)
3. [Comic book pages Kaggle dataset](https://www.kaggle.com/cenkbircanoglu/comic-books-classification)
4. [Fonts allowed for commerical use from Free Japanese Fonts](https://www.freejapanesefont.com/) - Licences are on individual pages
5. [Object Detection for Comics using Manga109 Annotations](https://arxiv.org/pdf/1803.08670.pdf) - Used as benchmark
6. [Speech bubbles PSD file](https://www.deviantart.com/zombiesmile/art/300-Free-Speech-Bubbles-Download-419223430)
7. [Label studio](https://labelstud.io/)

### Licences and Citations
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
