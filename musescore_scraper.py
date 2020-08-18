#! /usr/bin/env python3
import sys, os, json
from bs4 import BeautifulSoup
from requests import get
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from PyPDF2 import PdfFileMerger

# A Python script to scrape the music sheets off of Musescore. Takes in a musescore url as a command line argument.

def svgToPdf(name, link):
    open(name + ".svg", "wb").write(get(link).content)
    renderPDF.drawToFile(svg2rlg(name + ".svg"), name + ".pdf")
    os.remove(name + ".svg")

def main():
    # obtain the url through command line arguments
    url = sys.argv[1]
    response = get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # scrape metadata such as the name of the sheet music and the number of pages
    title = soup.find_all("meta", property="og:title")[0].attrs["content"]
    json_data = json.loads(soup.find_all("div", attrs={"class": "js-store"})[0].attrs["data-content"])
    page_length = json_data["store"]["jmuse_settings"]["score_player"]["json"]["metadata"]["pages"]

    # obtain the link to the first sheet
    base_link = soup.find_all("link", attrs={"as": "image"})[0].attrs['href']
    # soup.find_all("link", attrs={"type": "image/svg+xml"})

    # prepare to combine all the pdfs
    pdf_merger = PdfFileMerger()

    # the next links are not on the page, but by replacing the number in the url we can get all the pages
    for i in range(page_length):
        print("Processing page " + str(i + 1) + " of " + str(page_length) + "...")
        name = "score_" + str(i)
        link = base_link.replace("score_0", name)
        svgToPdf(name, link)
        pdf_merger.append(name + ".pdf")
        os.remove(name + ".pdf")
        
    # download the resulting file
    pdf_merger.write(title + ".pdf")
    print("Download complete!")

if __name__ == "__main__":
    main()

