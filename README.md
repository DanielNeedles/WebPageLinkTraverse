# Web Crawler

## Author

Dan Needles/ChatGPT

## Description:

This Python script is a web crawler that starts from a given URL, downloads the contents of webpages, and recursively looks for links in those pages. Along the way, it checks the pages for spelling errors and bad links and prints those as it builds a link graph to track the relationships between web pages.  At the end, it prints out a tree structure of these links. The crawler can handle both HTML and XML content.

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

## Note:

 - Ensure the 'lxml' library is installed for parsing both HTML and XML content.
 - Be responsible and respect website terms of service and robots.txt files when crawling.
 
##USAGE: 

webpage --url|u webpage --anchor|-a anchor --depth|-d depth_level [--brokenlinks|-b] [--spelling|-s] [--naughtywordlist|-n] [--verbose|-v] [--help|-h]")
