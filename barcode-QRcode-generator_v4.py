# Input: .csv of ID contents
# Output: Folder with corresponding QR codes
# Mark Whitty
# UNSW
# 20190328 Fixing bug whereby all codes were the same as the first one! Probably PDF generator not liking same filename.
# 20190319 V3 Read input from file and parse to generate QR code as well as human readable format
# 20190305 V2 Testing fast generation with timestamp, works well, takes about 25ms to make and display each one and makes a PDF (under development)
# 20190125 Working
# Derived from https://pypi.org/project/PyQRCode/
import pyqrcode
import os
import sys
import time
import cv2
import numpy as np
from numpy import array
import datetime as dt
from fpdf import FPDF


def read_qr_labels_from_file(filename):
    f = open(filename, "r")
    # Select relevant columns (for testing only)
    labels = f.readlines()
    #print(labels)
    return labels



def generate_QR_codes(qr_content, dest_path):
    #qr_content_human_string = qr_content.strftime('%Y-%m-%d_%H.%M.%S.%f%z')  # Convert item to string, in case it isn't already.
    #time_seconds_since_epoch = original_qr_content.timestamp()
    # In some cases newlines need to be removed, others we need the correct type to be passed in
    # to be processed and displayed in associated text (eg. date).
    new_code = pyqrcode.create(qr_content, error='l', mode='binary', encoding=None)  #, version=10, )

    image_path = os.path.join(dest_path, (qr_content + '.png'));
    #new_png = new_code.png(image_path, scale=6, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xff])
    #new_code.show()  # Very slow!

    # Display the image along with border
    code_size = len(new_code.code)
    image_array2 = np.ones((code_size+8, code_size+8), np.uint8)
    image_array1 = 1 - array(new_code.code, np.uint8)   # For some reason this needs to be inverted!
    image_array2[4:(4+code_size), 4:(4+code_size)] = image_array1
    # Add blank area at bottom for human readable text
    h,w = image_array2.shape
    blank_strip = np.ones((int(h/2), w), dtype=image_array2.dtype)
    image_array2 = np.r_[image_array2, blank_strip]

    image_array2 = image_array2*255  # Scale 0:1 values to 0:255

    scale_factor = 20  # Resize the image to be larger by simply scaling it up

    image_array2 = cv2.resize(image_array2, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)
    #cv2.imshow("New code: ", image_array2)
    #cv2.waitKey(0)

    y_text_pos = h*scale_factor
    x_text_pos = 0  #int(w*scale_factor/2)

    # Write content onto image
    #cv2.putText(image_array2, "Timestamp: YYYY-MM-DD_HH.MM.SS.uS", (x_text_pos, int(y_text_pos*1.03)),
    #            fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.5, color=(0, 0, 0), thickness=1)
    #cv2.putText(image_array2, human_string, (x_text_pos, y_text_pos),
    #    fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=0.5, color=(0, 0, 0), thickness=1)


    cv2.imwrite(image_path, image_array2)


    #print(new_code.terminal(quiet_zone=1))
    return image_path


def add_page_to_PDF(pdf, image_path, total_pages):
    # Write content into a PDF, see https://www.blog.pythonlibrary.org/2018/06/05/creating-pdfs-with-pyfpdf-and-python/
    pdf.add_page()
    pdf.set_auto_page_break(False)
    pdf.set_font("times", size=16)
    QR_width_pdf = 210  # Width (and height) of QR code (including border) on PDF (cm, assuming A4)
    pdf.image(image_path, x=0, y=0, w=QR_width_pdf)
    # Add a blank cell the size of the image
    pdf.cell(QR_width_pdf, QR_width_pdf, txt="", ln=1, align="L")
    if len(human_string) > 16:
        print("barcode-QRcode-generator::add_page_to_PDF:: too many strings in code to display on page")
        pdf.close()
        exit(1)
    if len(human_string) > 8:
        human_string_first_eight = human_string[0:8]
        human_string_remainder = human_string[8:]
        pdf.set_xy(10, 210)
        for line in human_string_first_eight:
            pdf.cell(100, 8, txt=line, ln=2, align="L")
        pdf.set_xy(105, 210)
        for line in human_string_remainder:
            pdf.cell(100, 8, txt=line, ln=2, align="L")
    else:
        pdf.set_xy(10, 210)
        for line in human_string:
            pdf.cell(100, 8, txt=line, ln=2, align="L")

    # Go to 1.5 cm from bottom to print footer
    pdf.set_y(-15)
    # Print centered page number
    pdf.cell(0, 10, "Page "+str(pdf.page_no())+" of "+str(total_pages), 0, 1, 'C')
    pdf.set_font("times", size=8)
    pdf.cell(100, 5, txt="QR code generated on " + dt.datetime.now().strftime('%Y-%m-%d_%H.%M.%S') + " by Mark Whitty", ln=1, align="L")

    return pdf


def add_title_page(pdf, total_pages, filename, headers):
    pdf.add_page()
    pdf.set_auto_page_break(False)
    pdf.set_font("times", size=16)
    #pdf.cell(100, 8, txt=Document Title, ln=2, align="L")
    pdf.multi_cell(0, 10, txt="This document containing QR codes was generated using the file " +
        filename + " on " + dt.datetime.now().strftime('%Y-%m-%d_%H.%M.%S') +
             "\n\nIt contained " + str(len(headers)) + " headers as follows:\n", align="L")

    for header_item in headers:
        pdf.cell(100, 10, txt=header_item, ln = 1, align="L")


# Main
if __name__ == '__main__':
# arg1: filename of input csv relative to current working directory, eg. 'WVV_Rowley_2019_cane\WVV_Rowley_2019_cane.csv'
# arg2: output folder, eg. 'WVV_Rowley_2019_cane'


    # Read list of filenames
    input_filename = sys.argv[1]
    labels = read_qr_labels_from_file(input_filename)

    # Read destination path
    if len(sys.argv) < 3:
        dest_path = "."
    else:
        dest_path = sys.argv[2]

    # Create target directory & all intermediate directories if don't exists
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
        print("Directory ", dest_path, " Created ")
    else:
        print("Warning: directory ", dest_path, " already exists, existing files may be overwritten")

    # Set up blank window
    #cv2.imshow("New code: ", np.zeros((100, 100), np.uint8))


    start_time = dt.datetime.now()

    header_row = labels[0]
    headers = [x.strip() for x in header_row.split(',')]
    headers[0] = headers[0][3:]
    # For some reason there are a few extra characters in the first cell


    pdf = FPDF()
    pdf.set_compression(True)
    pdf.set_author("Mark Whitty @ UNSW")
    pdf.set_title(os.path.basename(input_filename)[:-4])
    total_pages = len(labels)-1
    add_title_page(pdf, total_pages, os.path.basename(input_filename), headers)

    delimiter = "-"  # Delimiter used between fields in machine readable code

    num_labels_generated = 0

    # Generate output files based on labels
    for label in labels[1:]:
        split_values = [x.strip() for x in label.split(',')]

        machine_string = ""
        human_string = []
        # Make machine readable content (no error checking done here on string lengths)
        for j in range(len(headers)-1):
            machine_string = machine_string + headers[j] + delimiter + split_values[j] + delimiter
        machine_string = machine_string + headers[j+1] + delimiter + split_values[j+1]  # Last item don't add underscore

        # Make human readable content
        for j in range(len(headers)):
            human_string.append(headers[j] + " = " + split_values[j])
        #human_string[j+1] = headers[j+1] + " = " + split_values[j+1]  # Last item don't add newline

        image_path = generate_QR_codes(machine_string, dest_path)

        add_page_to_PDF(pdf, image_path, total_pages)
        try:
            os.remove(image_path)
        except OSError:
            pass
        num_labels_generated += 1

    pdf.output(os.path.join(dest_path, (os.path.basename(input_filename[:-4]) + '.pdf')))
    pdf.close()


    current_time = dt.datetime.now()
    print(str(num_labels_generated) + " images in " + str(((current_time - start_time).seconds)) + " seconds")

        #  Code below is for timing and generating QR codes quickly with timestamps
        #current_time = dt.datetime.now()
        #if((current_time-start_time).seconds > 3):
        #    break
        # Use time.time() to get time in seconds (float) since the epoch
        # Use datetime.datetime.now() to get this in human readable format
        #generate_SVG(dt.datetime.now(), dest_path)
        #print(str(i) + " images in " + str(((current_time-start_time).microseconds/1000)) + " milliseconds")
        # Taking about 25 ms to make and display each image.

