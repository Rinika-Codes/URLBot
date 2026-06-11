import requests
import re

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from database import pages_collection
from database import chunks_collection
import uuid
from chroma_client import chroma_collection, chroma_client

visited_links = set()


def clean_text(text):

    # remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # remove weird newline symbols
    text = text.replace("\\n", " ")

    return text.strip()


def chunk_text(text, chunk_size=500):

    chunks = []

    words = text.split()

    for i in range(0, len(words), chunk_size):

        chunk = " ".join(words[i:i + chunk_size])

        chunks.append(chunk)

    return chunks


def crawl_website(url, max_pages=5):

    global visited_links
    visited_links = set()

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    all_content = []
    pages_collection.delete_many({})
    chunks_collection.delete_many({})

    global chroma_collection
    try:
        chroma_client.delete_collection("chunks_collection")
    except Exception:
        pass
    chroma_collection = chroma_client.get_or_create_collection("chunks_collection")

    crawl(
        base_url=url,
        current_url=url,
        headers=headers,
        all_content=all_content,
        max_pages=max_pages
    )

    return {
        "pages_crawled": len(visited_links),
        "content": all_content
    }


def crawl(base_url, current_url, headers, all_content, max_pages):

    # stop if max pages reached
    if len(visited_links) >= max_pages:
        return

    # avoid duplicate crawling
    if current_url in visited_links:
        return

    try:

        print("Crawling:", current_url)

        response = requests.get(
            current_url,
            headers=headers,
            timeout=5
        )

        # mark visited AFTER successful request
        visited_links.add(current_url)

        soup = BeautifulSoup(response.text, "html.parser")

        # remove useless tags
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()

        raw_text = soup.get_text(
            separator=" ",
            strip=True
        )

        cleaned_text = clean_text(raw_text)

        # skip tiny/empty pages
        if len(cleaned_text) < 100:
            return

        # save page content
        page_data = {
        "website": base_url,
        "page_url": current_url,
        "content": cleaned_text[:3000]
        }

        # save clean copy in response
        all_content.append(page_data.copy())

        # save to MongoDB
        pages_collection.insert_one(page_data)

        # create chunks

        chunks = chunk_text(cleaned_text)

        chroma_ids = []
        chroma_docs = []
        chroma_metadatas = []

        for index, chunk in enumerate(chunks):

            chunk_data = {
            "website": base_url,
            "page_url": current_url,
            "chunk_number": index,
            "chunk_text": chunk
            }

            chunks_collection.insert_one(chunk_data)

            chroma_ids.append(str(uuid.uuid4()))
            chroma_docs.append(chunk)
            chroma_metadatas.append({
                "website": base_url,
                "page_url": current_url,
                "chunk_number": index
            })

        if chunks:
            chroma_collection.add(
                ids=chroma_ids,
                documents=chroma_docs,
                metadatas=chroma_metadatas
            )


        # extract links
        links = soup.find_all("a")

        for link in links:

            href = link.get("href")

            if not href:
                continue

            full_url = urljoin(base_url, href)

            # remove fragments
            full_url = full_url.split("#")[0]

            # normalize trailing slash
            if full_url.endswith("/"):
                full_url = full_url[:-1]

            # skip empty urls
            if not full_url:
                continue

            # skip mail/javascript links
            if full_url.startswith("mailto:"):
                continue

            if full_url.startswith("javascript:"):
                continue

            # skip files
            blocked_extensions = (
                ".pdf",
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".zip"
            )

            if full_url.lower().endswith(blocked_extensions):
                continue

            # keep only internal links
            if is_internal_link(base_url, full_url):

                crawl(
                    base_url,
                    full_url,
                    headers,
                    all_content,
                    max_pages
                )

    except Exception as e:
        print("ERROR:", e)


def is_internal_link(base_url, target_url):

    base_domain = urlparse(base_url).netloc
    target_domain = urlparse(target_url).netloc

    return base_domain == target_domain