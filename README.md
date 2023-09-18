# WebPageLinkTraverse

## Purpose
Given a webpage and depth, WebPageLinkTraverse will traverse the weblinks and report any broken links.

## Description
This Python script is a web crawler that starts from a given URL, downloads the contents of webpages, and recursively looks for links in those pages. It builds a link graph to track the relationships between webpages and prints out a tree structure of these links at the end. The crawler can handle both HTML and XML content.

## Pseudo Code:
 - Import the necessary libraries: requests, BeautifulSoup, urllib.parse, lxml (if used)
 - Define functions for downloading web pages, extracting links, performing web crawling, and printing the link tree.
 - Set the starting URL and maximum depth for crawling.
 - Initialize data structures (visited_links, link_graph) and a stack for traversal.
 - While the stack is not empty and the maximum depth is not reached:
   - Pop a URL from the stack.
   - Download the page content.
   - Extract links from the page.
   - Store the link relationship between the current URL and its parent URL.
   - Add the child links to the stack.
 - Print the link tree.

 Note:
 - Ensure that the 'lxml' library is installed for parsing both HTML and XML content.
 - Be responsible and respect website terms of service and robots.txt files when web crawling.

## Usage:
Modify the 'start_url' and 'max_depth' variables as needed, then run the script to start crawling.


