# Website Downloader

A simple Python tool to download a website's HTML and assets (images, CSS, JavaScript) to a local folder.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
python website_downloader.py https://example.com
```

Specify output directory:
```bash
python website_downloader.py https://example.com -o my_folder
```

## Features

- Recursively crawls and downloads every same-domain page reachable via `<a href>` links
- Downloads and updates paths for:
  - Images (`<img>` tags)
  - CSS files (`<link>` tags)
  - JavaScript files (`<script>` tags)
- Rewrites links/hrefs to relative local paths so the downloaded site browses correctly offline
- Only downloads resources and pages from the same domain (external links are left as-is)
- Creates proper directory structure mirroring the site's URL paths
- Skips already downloaded pages/files (avoids loops and duplicate work)

## Example

```bash
python website_downloader.py https://example.com -o example_site
```

This will create a `example_site` folder with the website contents.
