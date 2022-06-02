# -*- coding: utf-8 -*-

# Working: splitting into sets of 19 in directory with same name as PDF-file


#!pip3 install PyMuPDF
#!pip3 install PyPDF2

import os
import glob, sys, fitz
from PyPDF2 import PdfFileWriter, PdfFileReader
import tkinter
from tkinter import filedialog as fd
import re #needed for regex in filename


# Folder selection dialog
root = tkinter.Tk()
root.title("NAW-Test ORDNER (Unterordner erlaubt)")
folder_path = fd.askdirectory(parent=root,initialdir="/Users/florianfurrer/OneDrive - PHZH/Downloads/ALLE NAW für Splittung/",title='Wo liegen die NAW-Tests? (Unterordner erlaubt)') #change to "folder_path"

all_files = glob.glob(folder_path + "/**/*.pdf", recursive=True) #finds all PDFs in path from folder

#####

for filename in all_files:
  ##### AB HIER ANPASSEN!!!!
  #print(filename)
  a = re.search("[A-Z][0-9]{3}[N]{1}[0-9]{1}",filename)
  filename_shortened = a.group(0)
  #print(filename_shortened)
  dir_name = "{}/{}".format(folder_path, filename_shortened)
  #create directory command
  if os.path.exists(dir_name) == False:
    os.makedirs(dir_name, exist_ok=False) # only create if not existing? TRY EXCEPT. unten bei save image Pfad anpassen!
  os.chdir(dir_name) #CHANGE TO DIRECTORY NEEDED?

  doc = fitz.open(filename)  # open document
  # CREATE EXCEPTION WITH CONTINUATION WHEN NOT 19 PAGES IN DOCUMENT
  if doc.page_count % 19 == 0:
    print("OK: vermutlich vollständige Sets mit allen Seiten")
  else:
    print("ERROR: Bei {} falschen Seitenanzahl ({} Seite/n). Ein oder mehrere Testhefte sind unvollständig".format(filename_shortened, doc.page_count))
    ## ABORT!

#  splitted_pdf = "{}_splitted.pdf".format(filename_shortened) # legacy? No more needed?

####### BIS HIER
input_pdf = PdfFileReader(filename)

start = 0
end = 19
check = 0
split_runs = int(doc.page_count/19)
print("Necessary numbers of split runs: {}".format(split_runs))

'''
for split_run in range(split_runs): # how many splitting runs needed?
  print("run")
  new_pdf = PdfFileWriter()
  for page_num in range(start, end):
    new_pdf.addPage(input_pdf.getPage(page_num))
    #print(page_num)
    new_name="{}/{}_SuS-{}.pdf".format(dir_name, filename_shortened, split_run+1)
    with open(new_name, "wb") as output_stream:
      new_pdf.write(output_stream)
  output_stream.close()
  start += 19
  end += 19
  check += 1 #to check if splits complete. 

if check == split_runs:
  print("Splitted successfully {} times.".format(split_runs))
else:
  print("Splitting not successful. Only {} out of {} times registered.".format(check, split_runs+1))
'''