######### FIRST MANUALY INSTALL THESE IN TERMINAL #########
  #pip3 install PyMuPDF
  #pip3 install boxdetect
  #pip3 install pillow #called as PIL (Python Image Library)
  #pip3 install matplotlib
  #brew install python-tk #tkinter for open directory path dialog
  #pip3 install natsort  #needed to easy sort image-paths based on numbers on the end
  #pip3 install pandas #needed for CSV manipulation

####IMPORTS
import tkinter
from tkinter import filedialog as fd
import os
import glob, sys, fitz # wird alles für PyMuPDF benötigt
from boxdetect import config, img_proc
from boxdetect.pipelines import get_checkboxes
import matplotlib.pyplot as plt
from PIL import Image
#from google.colab.patches import cv2_imshow #only needed in google colab
import cv2 #openCV needed to draw rectangle on image
import re #needed for regex in filename
from natsort import natsorted
import pandas as pd #needed for working with CSV

# To get better resolution
zoom_x = 2.0  # horizontal zoom
zoom_y = 2.0  # vertical zoom
mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension

#def boxDetectSetup(): #PROBLEM: variable scope is not global when in function
cfg = config.PipelinesConfig()
# important to adjust these values to match the size of boxes on your image
cfg.width_range = (25,38) #(25,38)
cfg.height_range = (25,38) #(25,38)
# the more scaling factors the more accurate the results but also it takes more time to processing
# too small scaling factor may cause false positives
# too big scaling factor will take a lot of processing time
cfg.scaling_factors = [0.5] # needs to be 0.5 for quadrats
# w/h ratio range for boxes/rectangles filtering
cfg.wh_ratio_range = (0.8, 1.2) #(0.8, 1.2)
# group_size_range starting from 2 will skip all the groups
# with a single box detected inside (like checkboxes)
cfg.group_size_range = (1, 1)
# num of iterations when running dilation tranformation (to engance the image)
cfg.dilation_iterations = 0

#def coordValuesOnPages(): #PROBLEM: variable scope is not global when in function
safety_border = 50 #20

coord_page_1 = [[1006, 1353],
                [1006, 1403],
                [1006, 1453],
                [1006, 1503],
                [1006, 1552]] #coordinates are CENTERS of checkboxes; example for 3 checkboxes; safety-border (ca. 20px) gets added dynamically when checking occurs
coord_page_2 = [[]] #page 2 in document is empty!
coord_page_3 = [[123, 473],
                [123, 739],
                [123, 1039],
                [123, 1315]] #4 checkboxes
coord_page_4 = [[201, 555],
                [720, 555],
                [201, 1017],
                [729, 1017]] #4 checkboxes
coord_page_5 = [[132, 1095],
                [132, 1173],
                [132, 1251],
                [132, 1325]] #4 checkboxes
coord_page_6 = [[198, 1017],
                [198, 1117],
                [198, 1210],
                [198, 1316]] #4 checkboxes
coord_page_7 = [[139, 459],
                [139, 681],
                [139, 898],
                [139, 1138]] #4 checkboxes
coord_page_8 = [[190, 452],
                [190, 689],
                [190, 924],
                [190, 1151]] #4 checkboxes
coord_page_9 = [[136, 1082],
                [136, 1185],
                [136, 1288],
                [136, 1392]] #4 checkboxes
coord_page_10 = [[186, 450],
                [186, 680],
                [186, 922],
                [186, 1164]] #4 checkboxes
coord_page_11 = [[131, 1082],
                [131, 1186],
                [131, 1289],
                [131, 1392]] #4 checkboxes
coord_page_12 = [[186, 454],
                [186, 691],
                [186, 925],
                [186, 1153]] #4 checkboxes
coord_page_13 = [[342, 597],
                [342, 780],
                [342, 963],
                [342, 1145]] #4 checkboxes
coord_page_14 = [[187, 1168],
                [187, 1263],
                [187, 1359],
                [187, 1453]] #4 checkboxes
coord_page_15 = [[155, 712],
                [155, 874],
                [155, 1035],
                [155, 1196]] #4 checkboxes
coord_page_16 = [[253, 705],
                [253, 869],
                [253, 1034],
                [253, 1204]] #4 checkboxes
coord_page_17 = [[114, 976],
                [114, 1070],
                [114, 1166],
                [114, 1261]] #4 checkboxes
coord_page_18 = [[217, 797],
                [217, 900],
                [217, 1004],
                [217, 1108]] #4 checkboxes
coord_page_19 = [[294, 771],
                [294, 954],
                [294, 1136],
                [294, 1319]] #4 checkboxes
#boxDetectSetup() #call functions
#coordValuesOnPages() #call functions

# Folder selection dialog
root = tkinter.Tk()
root.title("NAW-Test ORDNER (Unterordner erlaubt)")
folder_path = fd.askdirectory(parent=root,initialdir="/Users/florianfurrer/Documents/GitHub/naw-omr/",title='Wo liegen die NAW-Tests? (Unterordner erlaubt)') #change to "folder_path"

root.title("NAW-CSV Datei, um Werte anzuhängen")
csv_path = fd.askopenfilename(parent=root,initialdir="/Users/florianfurrer/Documents/GitHub/naw-omr/",title='An welches CSV die Werte anhängen?') #save filename of CSV

naw_csv = pd.read_csv(csv_path, sep=';')
print(naw_csv.head()) #just to make sure, print headrow with some lines

##IMPORTANT: only import correctly named sets of 19 pages
#all_files = glob.glob("**/*.pdf", recursive=True) #finds all PDFs in path from folder
all_files = glob.glob(folder_path + "/**/*.pdf", recursive=True) #finds all PDFs in path from folder
for filename in all_files:
  a = re.search("[A-Z][0-9]{3}[_](?:NAW)[-][0-9]",filename)
  b = re.search("[_](?:split-run-)[0-9]",filename)
  shortname = a.group(0)+b.group(0)
  c = re.search("([^\/]+$)", filename)
  pdf_motherfolder = filename.replace(c.group(0), "")
  sus_folder = "{}{}".format(pdf_motherfolder,shortname) #these are subfolder per SuS (=split-run-#)
  #create directory command
  os.makedirs(sus_folder, exist_ok=True) #ok=False ## only create if not existing? TRY EXCEPT. unten bei save image Pfad anpassen!
  doc = fitz.open(filename)  # open document
### CREATE EXCEPTION WITH CONTINUATION WHEN NOT 19 PAGES IN DOCUMENT
  if doc.page_count == 19:
    print("OK: Korrekte Seitenanzahl")
  else:
    print("ERROR: Falschen Seitenanzahl. {} statt 19 Seiten.".format(doc.page_count))
  for count, page in enumerate(doc, start=1):  # iterate through the pages
    pix = page.get_pixmap(matrix=mat)  # render page to an image
    img_path = "{}/{}_page-{}.png".format(sus_folder, shortname, page.number+1)
    pix.save(img_path)  # store image as a PNG

# Boxdetect
  #for img in os.listdir(img_path):
    checkboxes = get_checkboxes(
      img_path, cfg=cfg, px_threshold=0.3, plot=False, verbose=False) #set verbose=True for detailed output #px_threshold=0.6 #threshold = Schwelle True/False
    print("Output object type: ", type(checkboxes))
    for checkbox in checkboxes:
        print("Checkbox bounding rectangle (x,y,width,height): ", checkbox[0])
        print("Result of `contains_pixels` for the checkbox: ", checkbox[1])
        print("Display the cropout of checkbox:")
        plt.figure(figsize=(1,1))
        plt.imshow(checkbox[2])
        #plt.show()
    
    img_annot = cv2.imread(img_path)


  # IMPLEMENT HERE: ("Result of `contains_pixels` for the checkbox: ", checkbox[1]) (TRUE-FALSE) TO CSV-List

    box_shift = 50 #shift-value for checkbox drawing for screening

    #detect page from filename
    page_detected = re.findall("page-[0-9]+",img_path) #isolate e.g. "page-1"
    page_detected = re.findall("[0-9]+", page_detected[0]) #isolate number from e.g. "page-1" = "1"

    for checkbox in checkboxes:
      cb_values = checkbox[0] #export list from checkbox-nd.array
      cb_xmin = cb_values[0] #x=width-axis
      cb_xmax = cb_values[0]+cb_values[2]
      cb_ymin = cb_values[1] #y=height-axis
      cb_ymax = cb_values[1]+cb_values[3]
      #print(cb_xmin, " - ", cb_xmax, " - ",cb_ymin, " - ",cb_ymax, " - ",) # only for debugging
      
      #MAKE CHECK IF CHECKBOX TWICE ON SAME COORDINATE AND IF A COORDINATE WITHOUT CHECKBOX EXISTS # WRITE ERROR CODES TO IMG AS RED TEXT!
      coord_page = "coord_page_{}".format(page_detected[0]) #
      print(coord_page)

      for count2,i in enumerate(eval(coord_page),start=1): # eval() is used to select variable based on string
        #TRY: CREATE ERROR HANDLER?
        print("Position {}: ".format(i), end="")
        if cb_xmin > i[0]-safety_border and cb_xmax < i[0]+safety_border and cb_ymin > i[1]-safety_border and cb_ymax < i[1]+safety_border:
          print("checkbox {} found, with value={}".format(count2,checkbox[1])) #CREATE HERE INPUT TO CSV WITH TRUE/1 AND COMMA ++ DRAW Checkbox an value to COPY of image (subdirectory)
          if checkbox[1] == True:
            cv2.rectangle(img_annot, (cb_xmin-box_shift, cb_ymin), (cb_xmax-box_shift, cb_ymax), (255, 0, 0), -1)
            ##MAKE HERE DATA-FRAME EINTRAG FÜR APPEND IN CSV
            

          elif checkbox[1] == False:
            cv2.rectangle(img_annot, (cb_xmin-box_shift, cb_ymin), (cb_xmax-box_shift, cb_ymax), (255, 0, 0), 2)
            ##MAKE HERE DATA-FRAME EINTRAG FÜR APPEND IN CSV

            
        else:
          print("not found") #CREATE HERE INPUT TO CSV WITH FALSE/0 AND COMMA
      print("--------") # NEW ROW IN CSV?

    cv2.imwrite(img_path,img_annot)


  images = glob.glob(sus_folder + "/*.png") #make list of all PNGs for one SuS
  images = natsorted(images)
  images_opened = []
  for image in images:
    image_open = Image.open(image)
    image_open = image_open.convert("RGB")
    images_opened.append(image_open)
  
  start_image = images_opened[0]
  images_opened.pop(0)
  start_image.save("{}/{}-marked.pdf".format(pdf_motherfolder, shortname),save_all=True, append_images=images_opened)
  
  for image_path in images:
    os.remove(image_path)
    print("removed: {}".format(image_path))
  os.removedirs(sus_folder)

""" WORKS - BUT CHANGE STRUCTURE ABOVE TO FIND OUT WHICH BOX IS WHICH
new_data = pd.DataFrame({'team': ['D', 'D', 'E', 'E'],
                   'points': [6, 4, 4, 7],
                   'rebounds': [15, 18, 9, 12]})
new_data.to_csv(csv_path, mode='a', sep=';', index=False, header=False)
"""