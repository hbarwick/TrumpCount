#!C:\Users\halla\PycharmProjects\untitled\venv\Scripts\python.exe
# TrumpQuoteWordCounter.py - Downloads transcripts of Donald Trump speeches and counts the occurrence of each word used.

import requests
import bs4
import re
import logging
import time
import csv

logging.basicConfig(level=logging.INFO, format=" %(asctime)s - %(levelname)s - %(message)s")


def getmostusedwords():
    """Downloads the 100 most used words in the English language from Wikipedia"""
    wiki = downloadhtml("https://en.wikipedia.org/wiki/Most_common_words_in_English")
    most_frequent_words = []
    logging.info("Collecting 100 most used words from Wikipedia")
    for i in wiki.select(".extiw"):
        word = i.text.lower()
        most_frequent_words.append(word)
    most_frequent_words = most_frequent_words[:100]
    logging.debug(f"Most frequent words: {most_frequent_words}")
    return most_frequent_words


def getlinks():
    """Loops through all pages of quotes and returns a list of all relevant links"""
    link_list = []
    logging.info("Getting links")
    for page in range(1, 2):    # Reduce this range to limit number of pages downloaded to speed up collection
        url = r"https://www.rev.com/blog/transcript-category/donald-trump-transcripts/page/" + str(page) + "?view=all"
        try:
            pagehtml = downloadhtml(url)
            data = pagehtml.findAll('div', attrs={'class': 'fl-post-grid'})
            logging.debug(f"Getting links from page {url}")
            for div in data:
                links = div.findAll('a')
                for a in links:
                    link_list.append(a.get("href"))
            time.sleep(0.5)
        except requests.exceptions.RequestException:
            logging.error("ERROR - Download failed")
            break
    return link_list


def downloadhtml(url):
    """Downloads the HTML from supplied URL and returns BeautifulSoup of the html"""
    res = requests.get(url)
    res.raise_for_status()
    logging.info(f"Downloading from {url}")
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    return soup


def parsetranscipt(url):
    """Connects to url and downloads html, uses regex to split the text into 3 groups for Name, Time & Quote. Returns list."""
    soup = downloadhtml(url)
    transcript = soup.find("div", "fl-callout-text").text
    regex = re.compile(r"(\w+\s\w+.)\s(.\d\d.\d\d.\d?\d?.?)\s(.+)")  # Regex splits out 3 groups: Name, Time, Quote
    split_transcript = regex.findall(transcript)
    logging.debug(f"Split data: {split_transcript}")
    return split_transcript


def splitquotes(split_transcript):
    """Takes regex findall list produced by parsetranscript and splits out the text on Trumps quotes. Returns string"""
    trumps_quotes = ""
    for item in split_transcript:
        if (item[0]) == "President Trump:" or 'Donald Trump:' or "President Donald Trump:":
            trumps_quotes += (item[2])  # item 2 contains all quote
    logging.debug(f"Returning Trump quotes: {trumps_quotes}")
    return trumps_quotes


def writefile(parseinput):
    """Takes string output and appends to a text file"""
    with open("TrumpQuotes.txt", "a+", encoding="utf-8") as file:
        logging.debug(f"{file} opened, now writing {parseinput}")
        try:
            file.write(parseinput)
        except UnicodeDecodeError:
            logging.error("UnicodeDecodeError: Could not write this section")


def readfile(file):
    """Reads a txt file and returns a string"""
    with open(file, "r", encoding="utf-8") as inputfile:
        filestring = inputfile.read()
        logging.debug(f"{file} opened for reading.")
    return filestring


def splitwords(inputstring):
    """Takes inputstring, removes punctuation except for apostrophes, returns list of words"""
    logging.info("Splitting out words and removing punctuation")
    word_list = re.findall(r"[a-zA-Z’]+", inputstring)
    logging.info("Removing any numbers")
    refined_word_list = [item for item in word_list if not item.isdigit()]
    logging.debug(f"Returning word list: {refined_word_list}")
    return refined_word_list


def countwords(word_inputs):
    """ Takes a list of word_inputs, counts words and returns wordcount dictionary"""
    wordcount = {}
    logging.info("Counting words.")
    for word in word_inputs:
        lword = word.lower()
        if lword not in wordcount:
            wordcount.update({lword: 1})
        else:
            wordcount[word.lower()] += 1
    return wordcount


def dictionarysorter(inputdict):
    """Takes inputdict and sorts key values from high to low, returns list"""
    logging.info("Sorting output.")
    sorted_count = sorted(inputdict.items(), key=lambda x: x[1], reverse=True)
    return sorted_count


def removemostused(sortedlist):
    """Takes sortedlist input and removes those that appear in the 100 most used list"""
    most_used_words = getmostusedwords()
    unique = []
    for word in sortedlist:
        if word[0] not in most_used_words:
            unique.append(word)
    return unique


def askyesno(question):
    """Returns True/False for Y/N answer to input question"""
    answer = input(question)
    if answer.lower().strip() == "n":
        return False
    elif answer.lower().strip() == "y":
        return True
    else:
        logging.info(f"Invalid input - User entered {answer}")
        print("Invalid Input")
        return askyesno(question)


def displayresult(orderedcountedlist):
    """Takes orderedcountedlist and prints out in easier to read format"""
    logging.debug("Printing out results:")
    for item in orderedcountedlist:
        print(str(item[0]) + " - " + str(item[1]))


def writecsv(sortedlist):
    try:
        with open("TrumpMostUsedWords.csv", "w", newline='') as output:
            csv_output = csv.writer(output)
            csv_output.writerow(['Word', 'Occurrence'])
            for row in sortedlist:
                csv_output.writerow(row)
    except PermissionError:
        input("Could not write to 'TrumpMostUsedWords.csv'. Ensure file is closed, then press enter to try again.")
        writecsv(sortedlist)


logging.info("Start of program")


download = askyesno("Do you need to download new data? Y/N: ")
if download:
    for link in getlinks():
        try:
            all_quotes = parsetranscipt(link)
            trump_quotes = splitquotes(all_quotes)
            writefile(trump_quotes)
        except requests.exceptions.RequestException:
            logging.error("ERROR - Download failed")
            break
    writefile(trump_quotes)

trump_words = splitwords(readfile("TrumpQuotes.txt"))

trump_word_count = countwords(trump_words)
sorted_trump_words = dictionarysorter(trump_word_count)

ask = askyesno("Would you like to remove the 100 most commonly used words? Y/N: ")
if not ask:
    print("The most used words by Trump are: ")
    writecsv(sorted_trump_words)
    displayresult(sorted_trump_words)

else:
    unique_trump_words = removemostused(sorted_trump_words)
    print("The most used words by Trump (minus top 100 most used words in English) are: ")
    writecsv(sorted_trump_words)
    displayresult(unique_trump_words)

