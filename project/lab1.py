from flask import Flask, render_template, request, make_response, jsonify
from werkzeug.utils import secure_filename
import io
import os

from collections import Counter
from nltk.stem.snowball import SnowballStemmer
#from nltk.corpus import stopwords #불용어 제거
import nltk
# 정규표현식을 사용해서 특수문자를 제거
import re
import pandas as pd
import numpy as np
import pytagcloud
###########
import sys
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter
from tqdm import tqdm, tqdm_notebook
from time import sleep

# debug option
debug = 0
# input option
password = b''
pagenos = set()
maxpages = 0
# output option
outfile = None
outtype = None
imagewriter = None
rotation = 0
stripcontrol = False
layoutmode = 'normal'
encoding = 'utf-8'
pageno = 1
scale = 1
caching = True
showpageno = True
laparams = LAParams()
######


#nltk.download('stopwords')
app = Flask(__name__)
imagewriter = None
@app.route('/')
def load_file():
   return render_template('index.html')

def extract_text_from_pdf(pdf_path):
    #####################33
    PDFDocument.debug = debug
    PDFParser.debug = debug
    CMapDB.debug = debug
    PDFPageInterpreter.debug = debug
    rsrcmgr = PDFResourceManager(caching=caching)
    fake_file_handle = io.StringIO()
    #outfp = open('1.txt', 'w', encoding=encoding)
    device = TextConverter(rsrcmgr, fake_file_handle, laparams=laparams,
                                   imagewriter=imagewriter)

    with open(pdf_path, 'rb') as fp:
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for page in PDFPage.get_pages(fp, pagenos,
                                           maxpages=maxpages, password=password,
                                           caching=caching, check_extractable=True):
                page.rotate = (page.rotate+rotation) % 360
                interpreter.process_page(page)

        device.close()
        text = fake_file_handle.getvalue()
    if text:
        return text



def make_wordcloud(word,filename):
    tag2 = word
    taglist = pytagcloud.make_tags(tag2, maxsize=80)
    #pdf 파일 명으로 wordcloud 저장하는 코드
    image_filename=filename.split(".")[0]+"_wordcloud.jpg"
    real_image_filename="static/"+image_filename;
    pytagcloud.create_tag_image(taglist, real_image_filename, size=(900, 600), fontname='Nobile', rectangular=False)

    return image_filename

def parsing(data):
    # 소문자와 대문자가 아닌 것은 공백으로 대체한다.
    only_english=re.sub("[^a-zA-Z\\s]","",data)

    #소문자로 변환 및 토큰화
    no_capitals=only_english.lower().split()

    #불용어 제거
    blacklist=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','alk','me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "youre", "youve", "youll", "youd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "its", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "thatll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "dont", 'should', "shouldve", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "arent", 'couldn', "couldnt", 'didn', "didnt", 'doesn', "doesnt", 'hadn', "hadnt", 'hasn', "hasnt", 'haven', "havent", 'isn', "isnt", 'ma', 'mightn', "mightnt", 'mustn', "mustnt", 'needn', "neednt", 'shan', "shant", 'shouldn', "shouldn't", 'wasn', "wasnt", 'weren', "werent", 'won', "wont", 'wouldn', "wouldnt",'cid','english']

    words = [word for word in no_capitals if not word in blacklist]
    counts=Counter(words)

    #가장 많이 나오는 최다빈도 100순위
    most_common_word_top_200=counts.most_common(100)
    return most_common_word_top_200

@app.route('/wordcloud', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']

      f.save(secure_filename(f.filename))
      data=parsing(extract_text_from_pdf(f.filename))
      wordcloud= make_wordcloud(data,f.filename)
      list_data=list(data)
      return render_template('index0.html',data=list_data, wordcloud=wordcloud)


if __name__ == '__main__':
   app.run(debug = True)
