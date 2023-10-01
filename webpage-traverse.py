#!/usr/bin/env python3
#
# Web Crawler
# Author: Dan Needles/ChatGPT
# Date: September 8, 2023
#
# Description:
# This Python script is a web crawler that starts from a given URL, downloads the contents of webpages,
# and recursively looks for links in those pages. It builds a link graph to track the relationships between
# webpages and prints out a tree structure of these links at the end. The crawler can handle both HTML and XML content.
#
# Pseudo Code:
# - Import the necessary libraries: requests, BeautifulSoup, urllib.parse, lxml (if used)
# - Define functions for downloading web pages, extracting links, performing web crawling, and printing the link tree.
# - Set the starting URL and maximum depth for crawling.
# - Initialize data structures (visited_links, link_graph) and a stack for traversal.
# - While the stack is not empty and the maximum depth is not reached:
#   - Pop a URL from the stack.
#   - Download the page content.
#   - Extract links from the page.
#   - Store the link relationship between the current URL and its parent URL.
#   - Add the child links to the stack.
# - Print the link tree.
#
# Note:
# - Ensure that the 'lxml' library is installed for parsing both HTML and XML content.
# - Be responsible and respect website terms of service and robots.txt files when web crawling.
#
# Usage:
#   USAGE: webpage url [--anchor|-a]  [--depth|-d] [--brokenlinks|-b] [--spelling|-s] [--naughtywordlist|-n] [--verbose|-v] [--help|-h]

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import lxml 
import enchant
import string
import re

import argparse

def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

def usage(broken_links, spelling, naughty_wordlist, verbose, url, anchor, depth):
    # Create argument parser
    parser = argparse.ArgumentParser(description="Webpage tool")

    # Add arguments
    parser.add_argument('-b','--brokenlinks', action="store_true", dest="broken_links", help='Detect broken links.')
    parser.add_argument('-s','--spelling', action="store_true", dest="spelling", help='Detect bad spelling.')
    parser.add_argument('-n','--naughtywordlist', action="store_true", dest="naughty_wordlist", help='Skip these words on spell check.')
    parser.add_argument('-v','--verbose', action="store_true", dest="verbose", help='Provides extra debugging.')
    parser.add_argument('-u','--url', action="store", type=str, dest="url", required=True, help='Web address to start at and follow all links.')
    parser.add_argument('-a','--anchor', action="store", type=str, dest="anchor", help='Only check websites with this string or whoms parents have this string.')
    parser.add_argument('-d','--depth', action="store", type=str, dest="depth", help='Limit how many links to hop from the original url.')
    #parser.add_argument('-H','--help', action="store_true", dest="help_message")

    # Parse the command-line arguments
    args = parser.parse_args()
    broken_links = args.broken_links
    spelling = args.spelling
    naughty_wordlist = args.naughty_wordlist
    verbose = args.verbose
    url = args.url
    depth = args.depth
    anchor = args.anchor

    print(f"""
    args             = {args}
    broken_links     = {broken_links}
    spelling         = {spelling}
    naughty_wordlist = {naughty_wordlist}
    verbose          = {verbose}
    url              = {url}
    depth            = {depth}
    anchor           = {anchor}
    """)

    #Implied -H or --help OR the command arguments do not make sense.
    if not url or not depth or not anchor or not any([broken_links, spelling]):
        print("USAGE: --url|u webpage --anchor|-a anchor --depth|-d depth_level [--brokenlinks|-b] [--spelling|-s] [--naughtywordlist|-n] [--verbose|-v] [--help|-h]")
        exit(-1)
    return broken_links,spelling,naughty_wordlist,verbose,url,anchor,depth

# Function to download the contents of a webpage
def download_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return None

# Function to extract links from an HTML page
def extract_links(html_content, base_url):
    links = set()
    #parser = 'html.parser'
    parser = "lxml"  # Use lxml as the parser
    soup = BeautifulSoup(html_content, parser)
    for a_tag in soup.find_all('a', href=True):
        link = urljoin(base_url, a_tag['href'])
        link = link.split('#')[0] ## Ignore placement reference (if exists)
        links.add(link)
    return links

# Function to translate string to a string of words
def process_string(input_string, verbose):
    # Remove control characters using regular expression
    input_string = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', input_string)

    # Remove sentence punctuation. Remove word punct (to keep): dash, appostropy, slash (webpages), and underscore (git program references)
    # Period is a special case due to webpages and other program references. So check these word by word and discard only periods at the end
    sentence_punctuation=string.punctuation.replace('-','').replace("'", "").replace("/","").replace("_","").replace(".","")

    translator = str.maketrans('', '', sentence_punctuation)
    input_string = input_string.translate(translator)
    if verbose:
        try:
            print("WITHOUT PUNCTUATION:\n" + input_string)
        except Exception as e:
            output_string=input_string.encode("UTF-8")
            print("WITHOUT PUNCTUATION:\n")
            print(output_string)
            #print("WITHOUT PUNCTUATION:\n  Cannot print due to error:", e)

    # Split the string by spaces
    temp_words = input_string.split()
    words = []

    # Remove only sentence periods. Discard words that embed a period. Also discard words with _ or /
    for word in temp_words:
        temp_word = word.rstrip('.')
        if '.' not in temp_word and '/' not in temp_word and '_' not in temp_word:
            words.append(temp_word)
    return words

# Function to check spelling
def spell_check_html_xml(input_string,spell_checker,verbose):

    # Parse the HTML/XML content using BeautifulSoup
    soup = BeautifulSoup(input_string, 'html.parser')

    # Extract the text content from the parsed document
    text_content = soup.get_text(" ")
    if verbose:
        try:
            print("WEBPAGE:\n" + text_content)
        except Exception as e:
            print("WEBPAGE:\n  Cannot print due to error:", e)

    # Translate string to words and clean up
    words = process_string(text_content,verbose)

    # Tokenize the text content into words
    #cleaned_string = ''.join(char for char in text_content if char.isalpha())
    #words = cleaned_string.split()

    pattern1 = r'^.*[a-z][A-Z][a-z]+$' # Detect mashed together words to ignore
    pattern2 = r'^.*[A-Z][A-Z].*$'  ## Ignore Acronyms

    # Initialize a list to store misspelled words
    misspelled_words = []
    ok_words = ['elastiflow', 'sublicense', 'sublicenses', 'decompile', 'humanreadable', 'nonpersonally', 'splunk', 'sflow', 'namespaced', 'elasticsearch', 'analytics', 'cyber', 'ebooks', 'codespaces', 'kibana', 'distro', 'cowart', 'flagbased', 'glibc', 'redpanda', 'netflow', 'changelog', 'uptodate', 'maxmind', 'junos', 'roadmap', 'stdout', 'cribl', 'serverclass', 'multinode', 'realtime', 'flowsec', 'xsmall', 'xlarge', 'virtualized', 'singlemode', 'rackawareness', 'grafana', 'flowssec', 'lifecycle', 'logstash', 'dockerfile', 'fortinet', 'fortigate', 'citrix', 'plixer', 'ziften', 'pensando', 'cubro', 'gigamon', 'geospatial', 'tcpdump', 'pluribus', 'pmacct', 'procera', 'netscaler', 'ziften', 'pensando', 'sandvine', 'antrea', 'trammellch', 'cognitix', 'calix', 'recordssecond', 'remediate', 'telco','performant', 'unsampled', 'amasol', 'hubspot', 'licensors', 'cyberattack', 'cyberattacks', 'unsampled', 'reimagined', 'vmware', 'namespace', 'namespaces', 'encap', 'tanzu', 'logzio', 'ipaddr', 'hostname', 'async', 'enricher', 'config', 'lookup', 'lookups', 'reindexed', 'reindexing', 'reindex', 'changeme', 'kubernetes', 'linux', 'natively', 'jsonpretty', 'nameserver', 'inband', 'schema', 'schemas', 'opensearch', 'floweval', 'multicloud', 'digitalization', 'samplicator', 'geoscheme', 'datagrams', 'phion', 'renewables', 'squarespace', 'clickstream', 'exfiltration', 'deliverables', 'enrichers', 'atlanta', 'flowcoll', 'sonicwall', 'efauthpassword', 'efprivpassword', 'systemd', 'downsampling', 'liveness', 'sonicwall', 'downsampling', 'serverless', 'viptela', 'splunkbase', 'filesystem', 'ubiquiti', 'hsflowd', 'mikrotik', 'riskiq', 'errored', 'kafka', 'sophos', 'astaro', 'phion', 'netintact', 'velocloud', 'vxlan', 'codec', 'filebeat', 'appname', 'webhook', 'fortigatelab', 'hostnames', 'robcowart', 'manousos', 'solarwinds', 'germain', 'geolocation', 'geolite', 'ndjson', 'systemct', 'goller', 'annika', 'wickert', 'freie', 'netze', 'manousos', 'mainimport', 'timefunc', 'remediating', 'noauth', 'nopriv', 'packetparser', 'flowsets', 'libpcap', 'powertools', 'systemctl', 'signup', 'boolean', 'runtime', 'misconfiguration', 'anonymizing', 'subnet', 'msgid', 'ident', 'sdwan', 'uptime' ]

    # Check the spelling of each word and add misspelled words to the list
    for word in words:
        ## Get rid of single quoted words (but keep appostrophies)
        word=word.rstrip("'").lstrip("'")
        ## Have we already checked this time?
        if word not in misspelled_words:
            ## No numbers, only words with all letters
            if word.isalpha():
                ## Must be 3 letters or more
                if len(word) > 4:
                    ## Ignore mashed together words
                    match = re.match(pattern1, word)
                    if not match:
                        ## Ignore acronyms
                        match = re.match(pattern2, word)
                        if not match:
                            ## Check list of exceptions
                            if word.lower() not in ok_words:
                                ## Ignore Webpages and Git/program references with '_'
                                #if not word.endswith("com") and not word.startswith('http') and '/' not in word and '_' not in word:
                                if '_' not in word:
                                    if not spell_checker.check(word):
                                        ## Check if company or other capitalized word
                                        if not spell_checker.check(word.capitalize()):
                                            misspelled_words.append(word)

    # Return the list of misspelled words
    #try:
    #    print("Misspelled Words:\n" + misspelled_words)
    #except Exception as e:
    #    print("Misspelled Words:\n  Cannot print due to error:", e)
    return misspelled_words

# Function to perform web crawling
def crawl_web(start_url, max_depth, anchor, verbose):
    visited_links = set()
    link_graph = {}  # Dictionary to store the links between webpages

    stack = [(start_url, None, 0)]  # Tuple format: (current_url, parent_url, depth)

    # Initialize the spell checker
    spell_checker = enchant.request_dict("en_US")  # You can change "en_US" to the desired language

    while stack:
        current_url, parent_url, depth = stack.pop()
        if current_url not in visited_links and depth <= max_depth:
            if verbose:
                print(f"Crawling {current_url}, Depth: {depth} of {max_depth}")

            # Download the page
            html_content = download_page(current_url)
            if html_content is not None:
                visited_links.add(current_url)

                # Check spellin of webpage
                if anchor in current_url.lower():
                  misspelled_words = spell_check_html_xml(html_content,spell_checker,verbose)
                  if misspelled_words:
                    print("\n")
                    print(f"Misspellings on {current_url}")
                    for word in misspelled_words:
                      try:
                          print(word + " suggestions: " + str(spell_checker.suggest(word)))
                          #print(word)
                      except Exception as e:
                          print("Could not print out word or suggestions due the the error:", e)
                    
                    print("\n\n")

                # Extract links from the current page
                links = extract_links(html_content, current_url)

                # Store the link relationship between current_url and parent_url
                if parent_url:
                    if parent_url not in link_graph:
                        link_graph[parent_url] = []
                    link_graph[parent_url].append(current_url)

                # Add the links to the stack with increased depth if we are less than one removed from our main site
                if parent_url:
                    if anchor in parent_url.lower():
                        for link in links:
                            stack.append((link, current_url, depth + 1))

                ## First Level
                else:
                    for link in links:
                        stack.append((link, current_url, depth + 1))

            # BROKEN LINK
            else:
                visited_links.add(current_url)

                # Store the link relationship between current_url and parent_url
                if parent_url:
                    if parent_url not in link_graph:
                        link_graph[parent_url] = []
                    if current_url.lower().startswith("mailto"):
                        link_graph[parent_url].append(current_url)
                    else:
                        link_graph[parent_url].append(current_url + "-BROKEN")
    return link_graph

# Function to print the link tree
def print_link_tree(link_graph, node, level=0):
    if node in link_graph:
        for child in link_graph[node]:
            print("  " * level + "|-- " + child)
            print_link_tree(link_graph, child, level + 1)

# Example usage
if __name__ == "__main__":
    # Initialize variables
    broken_links = False
    spelling = False
    naughty_wordlist = False
    verbose = False
    anchor = ''
    url = ""  # Replace with your desired starting URL
    depth = 4  # Maximum depth to crawl

    # Get and parse commandline arguments
    broken_links,spelling,naughty_wordlist,verbose,url,anchor,depth = usage(broken_links, spelling, naughty_wordlist, verbose, url, anchor, depth)
    depth=int(depth)
    link_graph = crawl_web(url, depth, anchor, verbose)

    # Print the link tree
    print(f"\nLink Tree for {url}:\n")
    print_link_tree(link_graph, url)
