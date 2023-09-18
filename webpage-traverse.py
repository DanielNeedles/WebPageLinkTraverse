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
# Modify the 'start_url' and 'max_depth' variables as needed, then run the script to start crawling.

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import lxml 

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
        links.add(link)
    return links

# Function to perform web crawling
def crawl_web(start_url, max_depth):
    visited_links = set()
    link_graph = {}  # Dictionary to store the links between webpages

    stack = [(start_url, None, 0)]  # Tuple format: (current_url, parent_url, depth)

    while stack:
        current_url, parent_url, depth = stack.pop()
        if current_url not in visited_links and depth <= max_depth:
            #print(f"Crawling {current_url}, Depth: {depth}")

            # Download the page
            html_content = download_page(current_url)
            if html_content is not None:
                visited_links.add(current_url)

                # Extract links from the current page
                links = extract_links(html_content, current_url)

                # Store the link relationship between current_url and parent_url
                if parent_url:
                    if parent_url not in link_graph:
                        link_graph[parent_url] = []
                    link_graph[parent_url].append(current_url)

                # Add the links to the stack with increased depth
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
    start_url = "XXXXXX"  # Replace with your desired starting URL
    max_depth = 6  # Maximum depth to crawl

    link_graph = crawl_web(start_url, max_depth)

    # Print the link tree
    print(f"\nLink Tree for {start_url}:\n")
    print_link_tree(link_graph, start_url)
