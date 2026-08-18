#!/usr/bin/env python3
"""
Simple Website Downloader
Recursively downloads a website's pages, links, and assets (images, CSS, JS)
to a local folder, following same-domain <a href> links.
"""

import argparse
import posixpath
from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag
from pathlib import Path
import requests
from bs4 import BeautifulSoup


class WebsiteDownloader:
    def __init__(self, url, output_dir):
        self.url = url
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.downloaded = set()  # assets already saved
        self.visited_pages = set()  # pages already crawled

    def download(self):
        """Download the website, following links to other same-domain pages"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {self.url} to {self.output_dir}")

        queue = deque([self.url])
        self.visited_pages.add(self.url)

        while queue:
            page_url = queue.popleft()
            html_content = self._download_page(page_url)
            if html_content is None:
                continue

            soup = BeautifulSoup(html_content, 'html.parser')
            self._download_assets(soup, page_url)
            new_links = self._process_links(soup, page_url, queue)

            local_path = self._get_local_path(page_url)
            self._save_file(local_path, str(soup).encode('utf-8'))
            print(f"Saved page: {local_path}")

            queue.extend(new_links)

        print(f"\nDownload complete! Files saved to {self.output_dir}")

    def _download_page(self, url):
        """Download a single page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return None

    def _download_assets(self, soup, page_url):
        """Download CSS, JS, images, and other assets"""
        # Download images
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                new_path = self._download_asset(src, page_url)
                if new_path:
                    img['src'] = new_path
                    
        # Download CSS
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                new_path = self._download_asset(href, page_url)
                if new_path:
                    link['href'] = new_path
                    
        # Download JavaScript
        for script in soup.find_all('script', src=True):
            src = script.get('src')
            if src:
                new_path = self._download_asset(src, page_url)
                if new_path:
                    script['src'] = new_path

    def _process_links(self, soup, page_url, queue):
        """Rewrite <a href> links to local paths and queue new same-domain pages"""
        new_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']

            # Skip non-page links (mailto, tel, javascript, in-page anchors)
            if href.startswith(('mailto:', 'tel:', 'javascript:', '#')):
                continue

            full_url, _ = urldefrag(urljoin(page_url, href))

            if not self._is_same_domain(full_url):
                continue

            a['href'] = self._relative_path(full_url, page_url)

            if full_url not in self.visited_pages:
                self.visited_pages.add(full_url)
                new_links.append(full_url)

        return new_links
                    
    def _download_asset(self, url, page_url):
        """Download a single asset file"""
        full_url = urljoin(page_url, url)
        
        # Skip if already downloaded
        if full_url in self.downloaded:
            return self._relative_path(full_url, page_url)
            
        # Skip external resources (optional)
        if not self._is_same_domain(full_url):
            return None
            
        try:
            response = self.session.get(full_url, timeout=10)
            response.raise_for_status()
            
            local_path = self._get_local_path(full_url)
            self._save_file(local_path, response.content)
            self.downloaded.add(full_url)
            
            print(f"Downloaded: {local_path}")
            return self._relative_path(full_url, page_url)
            
        except Exception as e:
            print(f"Failed to download {full_url}: {e}")
            return None
            
    def _is_same_domain(self, url):
        """Check if URL is from the same domain"""
        return urlparse(url).netloc == urlparse(self.url).netloc or not urlparse(url).netloc
        
    def _get_local_path(self, url):
        """Convert URL to local file path"""
        parsed = urlparse(url)
        path = parsed.path.lstrip('/')
        
        # Handle empty path or directory
        if not path or path.endswith('/'):
            path += 'index.html'
        # Page URLs with no file extension (e.g. /about) -> save as .html
        elif '.' not in path.rsplit('/', 1)[-1]:
            path += '.html'
            
        # Handle query parameters
        if parsed.query:
            path = path.replace('?', '_').replace('&', '_')
            
        return path

    def _relative_path(self, target_url, from_page_url):
        """Compute target's local path relative to the page linking to it"""
        target_path = self._get_local_path(target_url)
        from_dir = posixpath.dirname(self._get_local_path(from_page_url))
        return posixpath.relpath(target_path, from_dir or '.')
        
    def _save_file(self, filepath, content):
        """Save content to file"""
        full_path = self.output_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'wb') as f:
            f.write(content if isinstance(content, bytes) else content.encode('utf-8'))


def main():
    parser = argparse.ArgumentParser(
        description='Download a website and its assets to a local folder'
    )
    parser.add_argument('url', help='Website URL to download')
    parser.add_argument(
        '-o', '--output',
        default='downloaded_site',
        help='Output directory (default: downloaded_site)'
    )
    
    args = parser.parse_args()
    
    downloader = WebsiteDownloader(args.url, args.output)
    downloader.download()


if __name__ == '__main__':
    main()
