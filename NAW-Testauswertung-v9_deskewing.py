#FLOMR v1.9 - 2022-01

######### FIRST MANUALY INSTALL THESE IN TERMINAL #########
  #pip3 install PyMuPDF
  #pip3 install boxdetect
  #pip3 install pillow #called as PIL (Python Image Library)
  #pip3 install matplotlib
  #brew install python-tk #tkinter for open directory path dialog
  #pip3 install natsort  #needed to easy sort image-paths based on numbers on the end
  #pip3 install pandas #needed for CSV manipulation
  #pip3 install deskew #use for deskewing image

####IMPORTS
from asyncore import write
from fileinput import filename
import tkinter
from tkinter import filedialog as fd
import os
import glob, sys, fitz # wird alles für PyMuPDF benötigt
from boxdetect import config, img_proc
from boxdetect.pipelines import get_checkboxes
import matplotlib.pyplot as plt
from PIL import Image
import cv2 #openCV needed to draw rectangle on image
import re #needed for regex in filename
from natsort import natsorted
import pandas as pd #needed for working with CSV
from datetime import datetime
import csv
#following used for deskewing
import numpy as np
from skimage import io
from skimage.transform import rotate
from skimage.color import rgb2gray
from deskew import determine_skew
#from matplotlib import pyplot as plt #bereits vorhanden

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
cfg.scaling_factors = [0.9] # needs to be 0.5 for quadrats
# w/h ratio range for boxes/rectangles filtering
cfg.wh_ratio_range = (0.9, 1.1) #(0.95, 1.05)
# group_size_range starting from 2 will skip all the groups
# with a single box detected inside (like checkboxes)
cfg.group_size_range = (1, 1)
# for this image we will use rectangles as a kernel for morphological transformations
cfg.morph_kernels_type = ['rectangles', 'lines']  # 'lines'
cfg.morph_kernels_thickness = [4]
# num of iterations when running dilation tranformation (to engance the image)
cfg.dilation_iterations = 0

#def coordValuesOnPages(): #PROBLEM: variable scope is not global when in function
safety_border = 60 #20

coord_page_1_1 = [[1006, 1353],
                [1006, 1403],
                [1006, 1453],
                [1006, 1503],
                [1006, 1552]] #(NAW-1), coordinates are CENTERS of checkboxes; example for 3 checkboxes; safety-border (ca. 20px) gets added dynamically when checking occurs
coord_page_1_2 = [[1022,1142],
                [1022, 1192],
                [1022, 1242],
                [1022, 1290],
                [1022, 1340],
                [1022, 1440],
                [1022, 1489],
                [1022, 1539]] #(NAW-2), 8 checkboxes
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

keys = [
  "Orig_Filename","StudentIn","SuS","NAW-Version","check-log","exec-time","path",
  "p1-c1","p1-c2","p1-c3","p1-c4","p1-c5","p1-c6","p1-c7","p1-c8",
  "p2",
  "p3-c1","p3-c2","p3-c3","p3-c4",
  "p4-c1","p4-c2","p4-c3","p4-c4",
  "p5-c1","p5-c2","p5-c3","p5-c4",
  "p6-c1","p6-c2","p6-c3","p6-c4",
  "p7-c1","p7-c2","p7-c3","p7-c4",
  "p8-c1","p8-c2","p8-c3","p8-c4",
  "p9-c1","p9-c2","p9-c3","p9-c4",
  "p10-c1","p10-c2","p10-c3","p10-c4",
  "p11-c1","p11-c2","p11-c3","p11-c4",
  "p12-c1","p12-c2","p12-c3","p12-c4",
  "p13-c1","p13-c2","p13-c3","p13-c4",
  "p14-c1","p14-c2","p14-c3","p14-c4",
  "p15-c1","p15-c2","p15-c3","p15-c4",
  "p16-c1","p16-c2","p16-c3","p16-c4",
  "p17-c1","p17-c2","p17-c3","p17-c4",
  "p18-c1","p18-c2","p18-c3","p18-c4",
  "p19-c1","p19-c2","p19-c3","p19-c4"
  ]

def main():
  cb_dict = dict.fromkeys(keys, None)

  # Folder selection dialog
  root = tkinter.Tk()
  root.title("NAW-Test ORDNER (Unterordner erlaubt)")
  folder_path = fd.askdirectory(parent=root,initialdir="/Users/florianfurrer/Documents/GitHub/naw-omr/",title='Wo liegen die NAW-Tests? (Unterordner erlaubt)') #change to "folder_path"

  root.title("NAW-CSV Datei, um Werte anzuhängen")
  csv_path = fd.askopenfilename(parent=root,initialdir="/Users/florianfurrer/Documents/GitHub/naw-omr/",title='An welches CSV die Werte anhängen?') #save filename of CSV
  #naw_csv = pd.read_csv(csv_path, sep=';') #DEBUG ONLY
  #print(naw_csv.head()) #just to make sure, print headrow with some lines #DEBUG ONLY

  #create log file for security
  now = datetime.now()
  logfilePath = folder_path+"/log_"+now.strftime("%Y-%m-%d_%H.%M.%S")+".txt"
  log = open(logfilePath,"a")
  checkLog = False #use to mark in CSV (and maybe to delete if log-file is empty)
  def write_to_log(logString):
    log.write(logString)
    log.write("\n")
    log.write("#########################################")
    log.write("\n")

  # Beispiel-Benennung: Z206_AN1631_1 (=NAW-1) Z206_AN1631_2 (=NAW-2)
  ## USER INFO: only import correctly named sets of 19 pages
  all_files = glob.glob(folder_path + "/**/*.pdf", recursive=True) #finds all PDFs in path from folder
  for filename in all_files:
    a = re.search("[A-Z][0-9]{3}[_].{6}[_][0-9]",filename)
    naw_choice = a[0]
    naw_choice = naw_choice[-1]
    shortname = a.group(0)
    if "-marked" in filename:
      write_to_log("!!!   {} was already processed. (signed with '-marked')".format(filename))
      checkLog = True
    else:
      c = re.search("([^\/]+$)", filename)
      pdf_motherfolder = filename.replace(c.group(0), "")
      sus_folder = "{}{}".format(pdf_motherfolder,shortname) #these are subfolder per SuS (=split-run-#)
      #create directory command
      os.makedirs(sus_folder, exist_ok=True) #ok=False ## only create if not existing? TRY EXCEPT. unten bei save image Pfad anpassen!
      doc = fitz.open(filename)  # open document
      if doc.page_count != 19:
        write_to_log("!!!   ERROR: Falschen Seitenanzahl bei {}. {} statt 19 Seiten.".format(shortname, doc.page_count))
        checkLog = True
      else:
        #print("OK: Korrekte Seitenanzahl") #DEBUG ONLY
        ##sys.exit() # abort program if wrong number of pages #obsolete because of logfile

        for count, page in enumerate(doc, start=1):  # iterate through the pages
          pix = page.get_pixmap(matrix=mat)  # render page to an image
          img_path = "{}/{}_page-{}.png".format(sus_folder, shortname, page.number+1)
          pix.save(img_path)  # store image as a PNG

          def detection():
            # Boxdetect
            #for img in os.listdir(img_path):
            checkboxes = get_checkboxes(
              img_path, cfg=cfg, px_threshold=0.3, plot=False, verbose=False) #set verbose=True for detailed output #px_threshold=0.6 #threshold = Schwelle True/False
            for checkbox in checkboxes:
              #print("Checkbox bounding rectangle (x,y,width,height): ", checkbox[0]) ##DEBUG ONLY
              #print("Result of `contains_pixels` for the checkbox: ", checkbox[1]) ##DEBUG ONLY
              #print("Display the cropout of checkbox:") ##DEBUG ONLY
              plt.figure(figsize=(1,1))
              plt.imshow(checkbox[2])
              #plt.show() ##DEBUG ONLY
            
            img_annot = cv2.imread(img_path)
            return img_annot, checkboxes
          img_annot, checkboxes = detection()
          box_shift = 50 #shift-value for checkbox drawing for screening

          #detect page from filename
          page_detected = re.findall("page-[0-9]+",img_path) #isolate e.g. "page-1"
          page_detected = re.findall("[0-9]+", page_detected[0]) #isolate number from e.g. "page-1" = "1"
          coord_page = "coord_page_{}".format(page_detected[0]) #[0] Eigenheit des Regex, da Zusatzinformationen mitgegeben werden

          if int(page_detected[0])!=2: # no checkbox detection for page 2 (empty - maybe throws error if not skipped)
            if coord_page=="coord_page_1":
              if int(naw_choice) == 1:
                coord_page = "coord_page_1_1"
                #print("NAW-{} Test".format(naw_choice)) #DEBUG ONLY
              elif int(naw_choice) == 2:
                coord_page = "coord_page_1_2"
                #print("NAW-{} Test".format(naw_choice)) #DEBUG ONLY
          ##maybe overkill - MAKE CHECK IF CHECKBOX TWICE ON SAME COORDINATE AND IF A COORDINATE WITHOUT CHECKBOX EXISTS
            cb_checksum = 0 # zurückstellen des Counters für die Anzahl entdeckten Checkboxes auf der Seite
            for checkbox in checkboxes:
              cb_values = checkbox[0] #export list from checkbox-nd.array
              cb_xmin = cb_values[0] #x=width-axis
              cb_xmax = cb_values[0]+cb_values[2]
              cb_ymin = cb_values[1] #y=height-axis
              cb_ymax = cb_values[1]+cb_values[3]
              #print(cb_xmin, " - ", cb_xmax, " - ",cb_ymin, " - ",cb_ymax, " - ",) # only for debugging

              for count2,i in enumerate(eval(coord_page),start=1): # eval() is used to select variable based on string
                #print("Position {}: ".format(i), end="") #DEBUG ONLY
                if cb_xmin > i[0]-safety_border and cb_xmax < i[0]+safety_border and cb_ymin > i[1]-safety_border and cb_ymax < i[1]+safety_border:
                  #print("checkbox {} found, with value={}".format(count2,checkbox[1])) #DEBUG ONLY
                  if checkbox[1] == True:
                    cv2.rectangle(img_annot, (cb_xmin-box_shift, cb_ymin), (cb_xmax-box_shift, cb_ymax), (255, 0, 0), -1)
                    cb_checksum = cb_checksum+1 #Checkbox counter um 1 erhöhen, um gegen length der coord-page-Liste abzugleichen
                    cb_to_csv(cb_dict, "X", page_detected[0], count2)

                  elif checkbox[1] == False:
                    cv2.rectangle(img_annot, (cb_xmin-box_shift, cb_ymin), (cb_xmax-box_shift, cb_ymax), (255, 0, 0), 2)
                    cb_checksum = cb_checksum+1 #Checkbox counter um 1 erhöhen, um gegen length der coord-page-Liste abzugleichen
                    cb_to_csv(cb_dict, "-", page_detected[0], count2)
                
                #else: #DEBUG ONLY
                  #print("not found") #DEBUG ONLY
                #print("--------") #DEBUG ONLY

            if cb_checksum != len(eval(coord_page)): #1196 × 1688
              cv2.putText(img_annot,'FEHLER',(500,1550),cv2.FONT_HERSHEY_DUPLEX,4,(0,0,255),4,2)
              #deskew(img_path)
            # #CREATE HERE INPUT TO CSV WITH "NF" - OVERKILL? IN EXCEL MACHEN?

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
          #print("removed: {}".format(image_path)) ##DEBUG ONLY
        os.removedirs(sus_folder)
        write_to_log("√   {} successful".format(shortname))

    properties_to_csv(cb_dict, shortname, naw_choice, filename, csv_path, checkLog)
  write_to_log("INFO:   Run completed with all files from chosen directory.")

def cb_to_csv(cb_dict, value, page, count2):
  curr_key = str("p"+str(page)+"-c"+str(count2)) #construct key, e.g. "p1-c2"
  cb_dict[curr_key] = value

def properties_to_csv(cb_dict, shortname, naw_choice, filename, csv_path, checkLog):
  now = datetime.now()
  cb_dict["Orig_Filename"] = shortname
  cb_dict["StudentIn"] = shortname[0:4] #erste 4 characters
  cb_dict["SuS"] = shortname[0:-2] #ohne letzten 2 characters
  cb_dict["NAW-Version"] = naw_choice
  cb_dict["check-log"] = checkLog ##if log-entry make yes, if not "-"
  cb_dict["exec-time"] = now.strftime("%Y-%m-%d_%H:%M:%S")
  cb_dict["path"] = filename
  dict_to_csv(csv_path,keys,cb_dict)

def dict_to_csv(csv_path,keys,cb_dict): #Write to file at end of loop
  for k,v in cb_dict.items(): #alle None to "nf" (not found) ersetzen
    if v is None:
      cb_dict[k] = "nf"
  with open(csv_path,"a") as csvfile:
    writer = csv.DictWriter(csvfile, delimiter=";", fieldnames=keys)
    writer.writerow(cb_dict)

def deskew(img_path):
    img_annot2 = io.imread(img_path)
    grayscale = rgb2gray(img_annot2)
    angle = determine_skew(grayscale)
    rotated = rotate(img_annot2, angle, resize=False) * 255
    io.imsave(img_annot2, rotated.astype(np.uint8))
    return img_annot2
'''
'''

main() #run program
