"""
MediaParser — Detects and structures multimedia content from HTML/text.
Supports: YouTube iframes/links, HTML5 video, social media embeds.
"""
import re
import logging

logger = logging.getLogger(__name__)

YOUTUBE_EMBED_RE = re.compile(
    r'(?:youtube\.com/embed/|youtu\.be/)([A-Za-z0-9_\-]{11})', re.IGNORECASE
)
YOUTUBE_WATCH_RE = re.compile(
    r'(?:youtube\.com/watch\?(?:.*&)?v=|youtu\.be/)([A-Za-z0-9_\-]{11})', re.IGNORECASE
)
TWITTER_RE = re.compile(r'twitter\.com/\w+/status/(\d+)', re.IGNORECASE)
INSTAGRAM_RE = re.compile(r'instagram\.com/p/([A-Za-z0-9_\-]+)', re.IGNORECASE)
TIKTOK_RE = re.compile(r'tiktok\.com/@[\w.]+/video/(\d+)', re.IGNORECASE)
VIMEO_RE = re.compile(r'vimeo\.com/(\d+)', re.IGNORECASE)
VIDEO_EXT_RE = re.compile(r'https?://[^\s"\'<>]+\.(?:mp4|webm|ogg)', re.IGNORECASE)


class MediaParser:
    """Parse HTML soup or raw text and return a list of structured media objects."""

    def parse_soup(self, soup):
        """Parse a BeautifulSoup object. Returns list of media dicts."""
        results = []
        seen = set()

        # 1. iframes
        for iframe in soup.find_all("iframe"):
            src = iframe.get("src", "") or ""
            media = self._classify_url(src)
            if media and media["embed_url"] not in seen:
                seen.add(media["embed_url"])
                results.append(media)

        # 2. anchor tags (plain links)
        for a in soup.find_all("a", href=True):
            media = self._classify_url(a["href"])
            if media and media["embed_url"] not in seen:
                seen.add(media["embed_url"])
                results.append(media)

        # 3. HTML5 video tags
        for vid in soup.find_all("video"):
            src = vid.get("src") or ""
            if not src:
                source = vid.find("source")
                if source:
                    src = source.get("src", "")
            if src and src not in seen:
                seen.add(src)
                results.append({"type": "video", "source": "html5", "embed_url": src})

        # 4. og:video meta
        og = soup.find("meta", property="og:video")
        if og and og.get("content"):
            url = og["content"]
            media = self._classify_url(url)
            if media and media["embed_url"] not in seen:
                seen.add(media["embed_url"])
                results.append(media)
            elif url not in seen:
                seen.add(url)
                results.append({"type": "video", "source": "og", "embed_url": url})

        return results

    def parse_text(self, text):
        """Parse raw text/HTML string for media URLs."""
        results = []
        seen = set()

        for m in YOUTUBE_WATCH_RE.finditer(text):
            vid_id = m.group(1)
            embed = f"https://www.youtube.com/embed/{vid_id}?autoplay=0"
            if embed not in seen:
                seen.add(embed)
                results.append({"type": "video", "source": "youtube", "embed_url": embed})

        for m in YOUTUBE_EMBED_RE.finditer(text):
            vid_id = m.group(1)
            embed = f"https://www.youtube.com/embed/{vid_id}?autoplay=0"
            if embed not in seen:
                seen.add(embed)
                results.append({"type": "video", "source": "youtube", "embed_url": embed})

        for m in VIMEO_RE.finditer(text):
            vid_id = m.group(1)
            embed = f"https://player.vimeo.com/video/{vid_id}"
            if embed not in seen:
                seen.add(embed)
                results.append({"type": "video", "source": "vimeo", "embed_url": embed})

        for m in TWITTER_RE.finditer(text):
            tweet_id = m.group(1)
            url = f"https://twitter.com/i/web/status/{tweet_id}"
            if url not in seen:
                seen.add(url)
                results.append({"type": "social", "source": "twitter", "embed_url": url})

        for m in INSTAGRAM_RE.finditer(text):
            shortcode = m.group(1)
            embed = f"https://www.instagram.com/p/{shortcode}/embed/"
            if embed not in seen:
                seen.add(embed)
                results.append({"type": "social", "source": "instagram", "embed_url": embed})

        for m in VIDEO_EXT_RE.finditer(text):
            url = m.group(0)
            if url not in seen:
                seen.add(url)
                results.append({"type": "video", "source": "html5", "embed_url": url})

        return results

    def _classify_url(self, url):
        if not url:
            return None

        # YouTube embed src
        m = YOUTUBE_EMBED_RE.search(url)
        if m:
            vid_id = m.group(1)
            embed = f"https://www.youtube.com/embed/{vid_id}?autoplay=0"
            return {"type": "video", "source": "youtube", "embed_url": embed}

        # YouTube watch link
        m = YOUTUBE_WATCH_RE.search(url)
        if m:
            vid_id = m.group(1)
            embed = f"https://www.youtube.com/embed/{vid_id}?autoplay=0"
            return {"type": "video", "source": "youtube", "embed_url": embed}

        # Vimeo
        m = VIMEO_RE.search(url)
        if m:
            return {"type": "video", "source": "vimeo",
                    "embed_url": f"https://player.vimeo.com/video/{m.group(1)}"}

        # Twitter
        m = TWITTER_RE.search(url)
        if m:
            return {"type": "social", "source": "twitter",
                    "embed_url": f"https://twitter.com/i/web/status/{m.group(1)}"}

        # Instagram
        m = INSTAGRAM_RE.search(url)
        if m:
            return {"type": "social", "source": "instagram",
                    "embed_url": f"https://www.instagram.com/p/{m.group(1)}/embed/"}

        # TikTok
        m = TIKTOK_RE.search(url)
        if m:
            return {"type": "social", "source": "tiktok",
                    "embed_url": f"https://www.tiktok.com/embed/{m.group(1)}"}

        # Raw video file
        if VIDEO_EXT_RE.match(url):
            return {"type": "video", "source": "html5", "embed_url": url}

        return None


media_parser = MediaParser()
