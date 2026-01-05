#!/usr/bin/env python3
"""
InstaCommentGifGrabber v5.0 - Premium Terminal Experience
==========================================================
A beautifully designed CLI tool for extracting GIF stickers from Instagram comments.
Features persistent sessions, smart authentication, and a premium terminal UI.

Requirements:
    pip install playwright requests colorama
    playwright install chromium

Author: @ardel.yo (IG/TikTok) | @ardelyo (GitHub)
Version: 6.0.0 (Enterprise)
"""

import os
import re
import sys
import time
import random
import logging
import zipfile
import shutil
import urllib.parse
import requests
import concurrent.futures
from datetime import datetime
from tkinter import filedialog, Tk
from typing import List, Set
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page, Locator
import json
import threading
from moviepy import VideoFileClip

# Try to import colorama for cross-platform color support
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class Fore:
        CYAN = YELLOW = GREEN = RED = MAGENTA = WHITE = RESET = ""
    class Style:
        BRIGHT = DIM = RESET_ALL = ""

# ============================================================================
# CONFIGURATION
# ============================================================================
@dataclass
class Config:
    LOG_FILE: str = "grabber_browser.log"
    # New output structure: downloads/shortcode_timestamp/
    BASE_OUTPUT_DIR: str = "downloads"
    USER_DATA_DIR: str = "ig_browser_session"
    SCROLL_PAUSE: float = 2.0
    MAX_SCROLLS: int = 150
    HEADLESS: bool = False
    MAX_WORKERS: int = 5
    
    # Feature Flags
    DOWNLOAD_MEDIA: bool = True
    EXTRACT_COMMENTS: bool = True
    CONVERT_TO_MP4: bool = True

CONFIG = Config()

# ============================================================================
# UTILITY: MEDIA CONVERTER
# ============================================================================
class MediaConverter:
    @staticmethod
    def convert_gif_to_mp4(input_path: str, output_path: str) -> bool:
        """Convert GIF to MP4 using MoviePy."""
        try:
            # Load GIF
            clip = VideoFileClip(input_path)
            # Write MP4 (using libx264 codec for compatibility)
            # logger=None suppresses the progress bar from moviepy to keep our UI clean
            clip.write_videofile(output_path, codec="libx264", logger=None, audio=False)
            clip.close()
            return True
        except Exception as e:
            LOG.error(f"Conversion failed for {input_path}: {e}")
            return False

# ============================================================================
# UI UTILITIES - Enterprise Grade Terminal Interface
# ============================================================================
class UI:
    """Enterprise-grade terminal UI with rich visuals and performance tracking."""
    
    # Box drawing characters
    BOX_TL = '┌'
    BOX_TR = '┐'
    BOX_BL = '└'
    BOX_BR = '┘'
    BOX_H = '─'
    BOX_V = '│'
    
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def banner():
        banner = f"""
{Fore.CYAN}{Style.BRIGHT}
    ┌──────────────────────────────────────────────────────────────┐
    │                                                              │
    │   ██╗███╗   ██╗███████╗████████╗ █████╗  ASSET               │
    │   ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗ GRABBER             │
    │   ██║██╔██╗ ██║███████╗   ██║   ███████║                     │
    │   ██║██║╚██╗██║╚════██║   ██║   ██╔══██║                     │
    │   ██║██║ ╚████║███████║   ██║   ██║  ██║                     │
    │   ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝                     │
    │                                                              │
    │{Fore.WHITE}       Instagram Asset Grabber v6.0  │  Enterprise          {Fore.CYAN}│
    │                                                              │
    │{Style.DIM}   @ardel.yo (IG/TikTok)  │  @ardelyo (GitHub)            {Style.BRIGHT}│
    └──────────────────────────────────────────────────────────────┘
{Style.RESET_ALL}"""
        print(banner)
    
    @staticmethod
    def section(title: str):
        """Print a boxed section header."""
        width = 58
        padding = width - len(title) - 2
        left_pad = padding // 2
        right_pad = padding - left_pad
        print(f"\n{Fore.CYAN}    ┌{'─' * width}┐")
        print(f"    │{' ' * left_pad} {Style.BRIGHT}{title}{Style.RESET_ALL}{Fore.CYAN} {' ' * right_pad}│")
        print(f"    └{'─' * width}┘{Style.RESET_ALL}\n")
    
    @staticmethod
    def step(num: int, total: int, text: str):
        """Print a numbered step with visual indicator."""
        dots = '●' * num + '○' * (total - num)
        print(f"    {Fore.CYAN}{dots}{Style.RESET_ALL}  {text}")
    
    @staticmethod
    def success(text: str):
        print(f"    {Fore.GREEN}[OK]{Style.RESET_ALL} {text}")
    
    @staticmethod
    def warning(text: str):
        print(f"    {Fore.YELLOW}[!]{Style.RESET_ALL} {text}")
    
    @staticmethod
    def error(text: str):
        print(f"    {Fore.RED}[X]{Style.RESET_ALL} {text}")
    
    @staticmethod
    def info(text: str):
        print(f"    {Fore.WHITE}[i]{Style.RESET_ALL} {text}")
    
    @staticmethod
    def prompt(text: str) -> str:
        """Get styled input from user."""
        print(f"    {Fore.WHITE}Petunjuk: Paste Link Instagram atau geser (drag) folder ke sini.{Style.RESET_ALL}")
        return input(f"    {Fore.MAGENTA}>{Style.RESET_ALL} {text}: ").strip()
    
    @staticmethod
    def confirm(text: str) -> bool:
        """Get yes/no confirmation."""
        resp = input(f"    {Fore.MAGENTA}>{Style.RESET_ALL} {text} (y/N): ").strip().lower()
        return resp in ('y', 'yes')
    
    @staticmethod
    def wait_for_enter(text: str = "Press ENTER to continue..."):
        input(f"\n    {Fore.CYAN}>{Style.RESET_ALL} {text}")
    
    @staticmethod
    def progress_bar(current: int, total: int, width: int = 30, prefix: str = ""):
        """Print a clean progress bar with percentage."""
        pct = current / total if total else 0
        filled = int(width * pct)
        bar = '━' * filled + '╸' + '─' * (width - filled - 1) if filled < width else '━' * width
        status = f"{current}/{total}"
        print(f"\r    {prefix}{Fore.GREEN}{bar}{Style.RESET_ALL} {status} ({pct*100:.0f}%)", end='', flush=True)
    
    @staticmethod
    def stats_box(stats: dict):
        """Display a statistics box with key metrics."""
        print(f"\n    {Fore.CYAN}┌{'─' * 40}┐{Style.RESET_ALL}")
        for key, value in stats.items():
            print(f"    {Fore.CYAN}│{Style.RESET_ALL}  {key:<20} {Fore.WHITE}{value:>16}{Style.RESET_ALL}  {Fore.CYAN}│{Style.RESET_ALL}")
        print(f"    {Fore.CYAN}└{'─' * 40}┘{Style.RESET_ALL}")
    
    @staticmethod
    def final_report(stickers: int, duration: float, path: str = ""):
        """Display final operation report."""
        speed = stickers / duration if duration > 0 else 0
        print(f"""
    {Fore.GREEN}┌────────────────────────────────────────────┐
    │{Style.BRIGHT}          OPERATION COMPLETE                {Style.RESET_ALL}{Fore.GREEN}│
    ├────────────────────────────────────────────┤
    │  Stickers Extracted    {stickers:>18}  │
    │  Total Duration        {duration:>15.1f}s  │
    │  Average Speed         {speed:>13.2f}/sec  │
    └────────────────────────────────────────────┘{Style.RESET_ALL}
""")
        if path:
            UI.info(f"Saved to: {path}")

# ============================================================================
# LOGGING (File only, console is handled by UI)
# ============================================================================
def setup_logging() -> logging.Logger:
    logger = logging.getLogger("BrowserGrabber")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    
    fh = logging.FileHandler(CONFIG.LOG_FILE, mode='w', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s'))
    logger.addHandler(fh)
    return logger

LOG = setup_logging()

# ============================================================================
# UTILITY: GIPHY URL EXTRACTOR
# ============================================================================
def extract_giphy_url(proxy_url: str) -> str:
    if "giphy.com" in proxy_url:
        if proxy_url.startswith("https://media"):
            return proxy_url
        match = re.search(r'url=([^&]+)', proxy_url)
        if match:
            return urllib.parse.unquote(match.group(1))
    return proxy_url

# ============================================================================
# MAIN GRABBER CLASS
# ============================================================================
class BrowserGifGrabber:
    VERSION = "5.0.0"
    
    def __init__(self):
        LOG.info(f"InstaCommentGifGrabber v{self.VERSION} started")
        self._tk = Tk()
        self._tk.withdraw()
        self.gif_urls: Set[str] = set()
    
    def extract_shortcode(self, url: str) -> str:
        """Extract shortcode from various Instagram URL formats."""
        # Handle reel, p, tv, and reels paths
        match = re.search(r'/(?:p|reel|reels|tv)/([A-Za-z0-9_-]+)', url)
        if match:
            return match.group(1)
        # Fallback for old or alternative formats
        return url.strip('/').split('/')[-1].split('?')[0]
    
    def _download_media(self, url, folder, filename):
        if not url: return None
        try:
            resp = requests.get(url, stream=True, headers={"User-Agent": "Mozilla/5.0"})
            path = os.path.join(folder, filename)
            with open(path, 'wb') as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            print(f"    {Fore.GREEN}+ Captured:{Style.RESET_ALL} {filename}")
            return path
        except Exception as e:
            return None

    def extract_post_media(self, page: Page, save_dir: str):
        """Extracts media (images/videos) from the main post."""
        if not CONFIG.DOWNLOAD_MEDIA:
            return
            
        UI.section("POST MEDIA EXTRACTION")
        os.makedirs(save_dir, exist_ok=True)
        
        try:
            # wait for post to load
            page.wait_for_selector('article', timeout=5000)
            
            # Check for Carousel (ul in article)
            # We use a broad selector to see if there are multiple items
            carousel_arrow = page.query_selector("button[aria-label='Next']")
            
            seen_urls = set()
            media_count = 0
            
            # Helper to grab current view
            def scrape_current_view():
                nonlocal media_count
                # Images
                imgs = page.query_selector_all("article img")
                for img in imgs:
                    src = img.get_attribute('src')
                    if src and "instagram" in src and src not in seen_urls:
                        # Filter out small UI icons if any (checking size usually better but src filter helps)
                        seen_urls.add(src)
                        media_count += 1
                        self._download_media(src, save_dir, f"media_{media_count}.jpg")
                
                # Videos
                vids = page.query_selector_all("article video")
                for vid in vids:
                    src = vid.get_attribute('src')
                    poster = vid.get_attribute('poster')
                    target = src if src else poster # Fallback
                    if target and target not in seen_urls:
                        seen_urls.add(target)
                        media_count += 1
                        ext = "mp4" if src else "jpg"
                        self._download_media(target, save_dir, f"media_{media_count}.{ext}")

            # Initial scrape
            scrape_current_view()

            # If carousel, click next
            if carousel_arrow:
                UI.info("Carousel detected. navigating...")
                while True:
                    next_btn = page.query_selector("button[aria-label='Next']")
                    if not next_btn:
                        break
                    
                    try:
                        next_btn.click()
                        time.sleep(1.0) # wait for animation
                        scrape_current_view()
                    except:
                        break
            
            if media_count == 0:
                UI.warning("No specific media found (possibly private or protected).")
            else:
                UI.success(f"Extracted {media_count} media files.")

        except Exception as e:
            LOG.error(f"Media extraction error: {e}")
            UI.error(f"Failed to extract post media: {e}")

    def _download_media(self, url, folder, filename):
        if not url: return None
        try:
            # Add strict timeout and user-agent
            resp = requests.get(url, stream=True, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            path = os.path.join(folder, filename)
            with open(path, 'wb') as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            print(f"    {Fore.GREEN}+ Captured:{Style.RESET_ALL} {filename}")
            return path
        except Exception as e:
            return None

    def extract_post_media(self, page: Page, save_dir: str):
        """Extracts media (images/videos) from the main post in parallel."""
        if not CONFIG.DOWNLOAD_MEDIA: return
            
        UI.section("POST MEDIA EXTRACTION")
        os.makedirs(save_dir, exist_ok=True)
        
        try:
            try:
                page.wait_for_selector('article', timeout=5000)
            except:
                UI.warning("Could not find post article.")
                return

            carousel_arrow = page.query_selector("button[aria-label='Next']")
            seen_urls = set()
            media_queue = [] # (url, filename)
            
            def queue_current_view():
                # Images
                imgs = page.query_selector_all("article img")
                for img in imgs:
                    src = img.get_attribute('src')
                    if src and "instagram" in src and src not in seen_urls:
                        seen_urls.add(src)
                        idx = len(media_queue) + 1
                        media_queue.append((src, f"media_{idx}.jpg"))
                
                # Videos
                vids = page.query_selector_all("article video")
                for vid in vids:
                    src = vid.get_attribute('src')
                    poster = vid.get_attribute('poster')
                    target = src if src else poster
                    if target and target not in seen_urls:
                        seen_urls.add(target)
                        idx = len(media_queue) + 1
                        ext = "mp4" if src else "jpg"
                        media_queue.append((target, f"media_{idx}.{ext}"))

            UI.info("Scanning post for media...")
            queue_current_view()

            if carousel_arrow:
                UI.info("Carousel detected. navigating...")
                for _ in range(10): 
                    next_btn = page.query_selector("button[aria-label='Next']")
                    if not next_btn: break
                    try:
                        next_btn.click()
                        time.sleep(1.0)
                        queue_current_view()
                    except: break
            
            if not media_queue:
                UI.warning("No media found.")
                return

            UI.info(f"Downloading {len(media_queue)} media files in parallel...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=CONFIG.MAX_WORKERS) as executor:
                futures = [executor.submit(self._download_media, url, save_dir, fname) for url, fname in media_queue]
                count = 0
                for future in concurrent.futures.as_completed(futures):
                    count += 1
                    UI.progress_bar(count, len(media_queue), prefix="Media: ")
            print()
            UI.success(f"Downloaded {len(media_queue)} media files.")

        except Exception as e:
            LOG.error(f"Media extraction error: {e}")
            UI.error(f"Failed to extract post media: {e}")

    def ensure_authentication(self, page: Page, target_url: str) -> bool:
        """Navigates to post and ensures we are logged in to see comments."""
        try:
            UI.step(1, 3, "Navigating to post & verifying access...")
            page.goto(target_url, wait_until="load", timeout=60000)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(3)
            
            # Check if login is required (look for login input or specific text)
            is_login_page = page.query_selector('input[name="username"]') or "login" in page.url.lower()
            # Check if comments are blocked by a overlay
            is_blocked = page.query_selector('div[role="dialog"] button:has-text("Log In")')
            
            if not is_login_page and not is_blocked:
                # Basic check: can we see common post elements?
                if page.query_selector('section') or page.query_selector('article'):
                    UI.success("Post accessible.")
                    return True

            UI.warning("Login required to view comments.")
            UI.section("MANUAL LOGIN REQUIRED")
            print(f"""
    {Fore.WHITE}The browser is at: {page.url}
    
    {Fore.YELLOW}Action Required:
    {Style.RESET_ALL}  1. Log in manually in the browser window
       2. Once you see the post and comments, come back here
       3. Press ENTER to continue
""")
            UI.wait_for_enter("Press ENTER after you have logged in...")
            
            # Final check - go back to the target post to be sure
            UI.info("Re-verifying access...")
            page.goto(target_url, wait_until="load", timeout=60000)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(2)
            
            if not page.query_selector('input[name="username"]'):
                UI.success("Access verified!")
                return True
            else:
                UI.error("Still unable to access the post. Please try logging in again.")
                return False
        except Exception as e:
            LOG.error(f"Auth verification error: {e}")
            return False
    def scan_comments(self, page: Page) -> dict:
        """Scanning comments for GIF stickers and textual content."""
        UI.step(2, 3, "Scanning comments (Stickers & Text)...")
        
        found_urls: Set[str] = set()
        found_comments: List[dict] = []
        last_count = 0
        no_change_count = 0
        
        CONTAINER_SEL = "div.x5yr21d.xw2csxc.x1odjw0f.x1n2onr6"
        PLUS_ICON_SEL = "svg[aria-label='Load more comments']"
        VIEW_REPLIES_SEL = "span:has-text('View all'), span:has-text('replies')"
        
        # JS to extract both stickers and text
        EXTRACT_JS = '''
            (containerSel) => {
                const container = document.querySelector(containerSel);
                if (!container) return { stickers: [], comments: [] };
                
                const stickers = [];
                const comments = [];
                
                // 1. Stickers
                container.querySelectorAll('img[src*="giphy.com"], img.x12ol6y4').forEach(img => {
                    if (img.src) stickers.push(img.src);
                });
                
                // 2. Comments (Best effort text extraction)
                container.querySelectorAll('span[dir="auto"]').forEach(span => {
                    const text = span.innerText;
                    if (text && text.length > 1) {
                         let parent = span.parentElement;
                         let foundUser = null;
                         for(let i=0; i<5; i++) {
                             if(!parent) break;
                             const userLink = parent.querySelector('h3 a, div a[href^="/"]');
                             if(userLink && userLink.innerText) {
                                 foundUser = userLink.innerText;
                                 break;
                             }
                             parent = parent.parentElement;
                         }
                         comments.push({user: foundUser || "Unknown", text: text});
                    }
                });
                
                return { stickers: stickers, comments: comments };
            }
        '''

        for scroll_num in range(CONFIG.MAX_SCROLLS):
            # 1. Navigation Check
            if page.url.split('?')[0].rstrip('/') != target_url.rstrip('/'):
                LOG.warning("Navigation drift detected, auto-recovering...")
                page.goto(target_url, wait_until="load")
                time.sleep(2)

            # 2. Extract
            try:
                data = page.evaluate(EXTRACT_JS, CONTAINER_SEL)
                
                # Merge Data
                for u in data.get('stickers', []): found_urls.add(u)
                
                # Simple dedup for comments
                current_sigs = {f"{c['user']}:{c['text']}" for c in found_comments}
                for c in data.get('comments', []):
                    sig = f"{c['user']}:{c['text']}"
                    if sig not in current_sigs:
                        found_comments.append(c)
            except Exception as e:
                pass # Continue scan even if JS fails
            
            # Print status
            num_comments = len(found_comments)
            print(f"\r    {Fore.CYAN}➤ {Style.BRIGHT}Scanning:{Style.RESET_ALL} {scroll_num+1:<3} scrolls | {len(found_urls):<3} stickers | {num_comments:<3} comments", end='', flush=True)

            # 3. Smart Completion Detection
            has_load_more = page.query_selector(f"{CONTAINER_SEL} {PLUS_ICON_SEL}") is not None
            
            if len(found_urls) == last_count:
                no_change_count += 1
                if no_change_count >= 8 and not has_load_more:
                    UI.info("\n    No more new content detected.")
                    break
            else:
                no_change_count = 0
            
            last_count = len(found_urls)

            # 4. Interaction
            try:
                container = page.query_selector(CONTAINER_SEL)
                if container:
                    plus = container.query_selector(PLUS_ICON_SEL)
                    if plus: 
                        plus.click()
                        time.sleep(random.uniform(1.0, 1.5))
                    
                    reply = container.query_selector(VIEW_REPLIES_SEL)
                    if reply: 
                        reply.click()
                        time.sleep(random.uniform(0.5, 0.8))
            except: pass

            # 5. Smooth Scroll
            page.evaluate(f'''
                (sel) => {{
                    const el = document.querySelector(sel);
                    if (el) {{
                        el.scrollTop += 600;
                    }}
                }}
            ''', CONTAINER_SEL)
            
            time.sleep(CONFIG.SCROLL_PAUSE + random.uniform(0.2, 0.5))
        
        print()
        return {"stickers": found_urls, "comments": found_comments}
    
    def download_sticker(self, url: str, index: int, save_dir: str) -> str:
        try:
            direct_url = extract_giphy_url(url)
            headers = {"User-Agent": "Mozilla/5.0 Chrome/120.0.0.0"}
            resp = requests.get(direct_url, headers=headers, timeout=30, stream=True)
            resp.raise_for_status()
            
            ext = ".gif"
            if ".webp" in url.lower(): ext = ".webp"
            elif ".mp4" in url.lower(): ext = ".mp4"
            
            filepath = os.path.join(save_dir, f"sticker_{index:04d}{ext}")
            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            return filepath
        except:
            return None

    def convert_stickers_parallel(self, sticker_paths: List[str], converted_dir: str):
        """v6.0: Convert multiple GIFs to MP4 in parallel."""
        UI.section("CONVERTING TO MP4 (Turbo)")
        total = len(sticker_paths)
        converted_count = 0
        
        def _task(path):
            fname = os.path.basename(path)
            name_no_ext = os.path.splitext(fname)[0]
            out_path = os.path.join(converted_dir, f"{name_no_ext}.mp4")
            if MediaConverter.convert_gif_to_mp4(path, out_path):
                return True
            return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=CONFIG.MAX_WORKERS) as executor:
            futures = [executor.submit(_task, p) for p in sticker_paths]
            for future in concurrent.futures.as_completed(futures):
                if future.result():
                    converted_count += 1
                UI.progress_bar(converted_count, total, prefix="Converting: ")
        print()
        UI.success(f"Converted {converted_count} files.")
        return converted_count

    def download_stickers_parallel(self, urls: List[str], save_dir: str) -> List[str]:
        """v6.0: Download multiple stickers simultaneously."""
        downloaded = []
        total = len(urls)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=CONFIG.MAX_WORKERS) as executor:
            # Map URLs to futures
            future_to_idx = {executor.submit(self.download_sticker, url, i+1, save_dir): i for i, url in enumerate(urls)}
            
            for future in concurrent.futures.as_completed(future_to_idx):
                path = future.result()
                if path:
                    downloaded.append(path)
                
                # Dynamic progress bar
                UI.progress_bar(len(downloaded), total)
        
        print() # Newline
        return downloaded

    def process_local_input(self, input_path: str):
        """Process a local folder or zip file containing stickers."""
        UI.section("LOCAL FILE PROCESSING")
        
        # Setup session folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = os.path.splitext(os.path.basename(input_path))[0]
        session_folder = os.path.join(CONFIG.BASE_OUTPUT_DIR, f"{name}_{timestamp}")
        stickers_dir = os.path.join(session_folder, "stickers")
        converted_dir = os.path.join(session_folder, "converted")
        
        os.makedirs(session_folder, exist_ok=True)
        os.makedirs(stickers_dir, exist_ok=True)
        if CONFIG.CONVERT_TO_MP4: os.makedirs(converted_dir, exist_ok=True)
        
        # Extract/Copy Logic
        sticker_files = []
        
        if zipfile.is_zipfile(input_path):
            UI.info(f"Extracting Zip: {input_path}")
            try:
                with zipfile.ZipFile(input_path, 'r') as zf:
                    for member in zf.namelist():
                        if member.lower().endswith(('.gif', '.webp', '.mp4')):
                            # Extract to stickers dir, flattening structure
                            target_name = os.path.basename(member)
                            target_path = os.path.join(stickers_dir, target_name)
                            with open(target_path, 'wb') as f:
                                f.write(zf.read(member))
                            sticker_files.append(target_path)
            except Exception as e:
                UI.error(f"Zip extraction failed: {e}")
                return
        elif os.path.isdir(input_path):
            UI.info(f"Scanning Folder: {input_path}")
            for root, _, files in os.walk(input_path):
                for file in files:
                    if file.lower().endswith(('.gif', '.webp', '.mp4')):
                        src = os.path.join(root, file)
                        dst = os.path.join(stickers_dir, file)
                        shutil.copy2(src, dst)
                        sticker_files.append(dst)
        else:
            UI.error("Invalid input. Must be a Zip file or Directory.")
            return

        if not sticker_files:
            UI.warning("No GIF/WebP/MP4 files found in input.")
            return

        UI.success(f"Found {len(sticker_files)} stickers.")

        # Conversion Phase
        if CONFIG.CONVERT_TO_MP4:
            self.convert_stickers_parallel(sticker_files, converted_dir)

        # Archive Result
        UI.section("FULL ARCHIVE")
        zip_path = shutil.make_archive(session_folder, 'zip', CONFIG.BASE_OUTPUT_DIR, f"{name}_{timestamp}")
        UI.success(f"Archive: {zip_path}")
        
    def extract_profile_pic(self, page: Page, username: str, save_dir: str):
        """Extracts the HD profile picture."""
        UI.section("PROFILE PICTURE")
        os.makedirs(save_dir, exist_ok=True)
        try:
            # 1. Try generic profile image selector
            valid_img = None
            
            # Often the profile pic has alt containing the username
            img = page.query_selector(f"img[alt*='{username}']")
            if img:
                valid_img = img.get_attribute("src")
            else:
                # Fallback: check standard metadata
                meta = page.query_selector("meta[property='og:image']")
                if meta:
                    valid_img = meta.get_attribute("content")
            
            if valid_img:
                self._download_media(valid_img, save_dir, f"{username}_profile.jpg")
                UI.success("Profile picture downloaded.")
            else:
                UI.warning("Could not find profile picture.")
                
        except Exception as e:
            LOG.error(f"Profile pic error: {e}")
            UI.error(f"Profile pic failed: {e}")

    def extract_stories(self, page: Page, username: str, save_dir: str):
        """Extracts 24h Stories."""
        UI.section("STORIES")
        os.makedirs(save_dir, exist_ok=True)
        
        story_url = f"https://www.instagram.com/stories/{username}/"
        UI.info(f"Navigating to stories: {story_url}")
        
        try:
            page.goto(story_url, wait_until="networkidle")
            time.sleep(3)
            
            # Check if stories exist (sometimes redirects to feed if none)
            if "stories" not in page.url:
                UI.warning("No active stories found (or private).")
                return

            # Click "View Story" if present (sometimes large button)
            try:
                view_btn = page.query_selector("text=View story")
                if view_btn: view_btn.click()
            except: pass

            seen_urls = set()
            story_count = 0
            
            # Loop through story slides
            # We determine end by checking URL changes or if we are kicked back to feed
            # Safety limit: 100 slides
            for _ in range(100):
                # 1. Grab Media
                # Video
                vid = page.query_selector("video source")
                if vid:
                    src = vid.get_attribute("src")
                    if src and src not in seen_urls:
                        seen_urls.add(src)
                        story_count += 1
                        self._download_media(src, save_dir, f"story_{story_count}.mp4")
                
                # Image (look for largest img that isn't UI)
                try:
                    imgs = page.query_selector_all("section img")
                    if not imgs: imgs = page.query_selector_all("img") # Fallback
                    
                    for img in imgs:
                        src = img.get_attribute("src")
                        if src and "instagram" in src and src not in seen_urls:
                             # Filter out tiny icons
                            rect = img.bounding_box()
                            if rect and rect['width'] > 300:
                                seen_urls.add(src)
                                story_count += 1
                                self._download_media(src, save_dir, f"story_{story_count}.jpg")
                except: pass
                
                # 2. Next Slide
                # Try finding the "Next" hidden button (right side of screen)
                try:
                    next_arrow = page.query_selector("button[aria-label='Next']")
                    if not next_arrow:
                        # Sometimes it's simpler to click the right side of the page
                        if page.viewport_size:
                            page.mouse.click(x=page.viewport_size['width'] - 50, y=page.viewport_size['height'] // 2)
                    else:
                        next_arrow.click()
                    
                    time.sleep(1.5) # Wait for next slide
                except:
                    break
                    
                # Break if URL changes completely (left story viewer)
                if "stories" not in page.url:
                    break
            
            UI.success(f"Downloaded {story_count} story items.")

        except Exception as e:
            LOG.error(f"Story error: {e}")
            UI.error(f"Failed to extract stories: {e}")

    def extract_highlights(self, page: Page, username: str, save_dir: str):
        """Extracts Highlights (Permanent Stories)."""
        UI.section("HIGHLIGHTS")
        # Go to profile first
        page.goto(f"https://www.instagram.com/{username}/", wait_until="networkidle")
        time.sleep(3)
        
        try:
            hl_links = page.evaluate('''() => {
                const links = Array.from(document.querySelectorAll('a[href*="/stories/highlights/"]'));
                return links.map(a => a.href);
            }''')
            
            # Unique highlights
            hl_links = list(set(hl_links))
            
            if not hl_links:
                UI.warning("No highlights found.")
                return
            
            UI.info(f"Found {len(hl_links)} highlight albums.")
            
            for i, link in enumerate(hl_links):
                hl_name = f"highlight_{i+1}"
                hl_dir = os.path.join(save_dir, hl_name)
                os.makedirs(hl_dir, exist_ok=True)
                
                UI.info(f"Processing Highlight {i+1}...")
                
                # Navigate to the highlight
                page.goto(link, wait_until="networkidle")
                time.sleep(2)
                
                # Similar loop to stories
                seen = set()
                count = 0
                for _ in range(100):
                    # Grab content (Video/Image)
                    vid = page.query_selector("video source")
                    if vid:
                        src = vid.get_attribute("src")
                        if src and src not in seen:
                            seen.add(src)
                            count += 1
                            self._download_media(src, hl_dir, f"hl_{count}.mp4")
                    else:
                        # Image
                        imgs = page.query_selector_all("img")
                        for img in imgs:
                            src = img.get_attribute("src")
                            rect = img.bounding_box()
                            # Rough heuristic for main image
                            if src and "instagram" in src and rect and rect['width'] > 300 and src not in seen:
                                seen.add(src)
                                count += 1
                                self._download_media(src, hl_dir, f"hl_{count}.jpg")

                    # Next
                    try:
                        if page.viewport_size:
                            page.mouse.click(x=page.viewport_size['width'] - 50, y=page.viewport_size['height'] // 2)
                        time.sleep(1.0)
                    except: break
                    
                    # Check if we moved to next highlight or closed
                    # Highlights URLs often look like /stories/highlights/12345/
                    # If ID changes, we are in next highlight.
                    if link.split('/')[-2] not in page.url:
                        break
                        
                UI.info(f"  > Saved {count} items.")

        except Exception as e:
            LOG.error(f"Highlight error: {e}")
            UI.error(f"Detailed highlight extraction failed: {e}")
        UI.info(f"Output Directory: {session_folder}")

    def run(self):
        # Startup Sequence
        UI.clear()
        print(f"\n{Fore.CYAN}    Initializing Enterprise Core...{Style.RESET_ALL}")
        time.sleep(1)
        
        start_time = time.time()
        UI.clear()
        UI.banner()
        
        UI.section("PERSIAPAN (SETUP)")
        print(f"    {Fore.WHITE}Cara penggunaan tool ini:{Style.RESET_ALL}")
        print(f"    1. {Fore.CYAN}Paste Link Instagram{Style.RESET_ALL} (Post/Reel/Profile)")
        print(f"    2. {Fore.CYAN}Geser & Lepas Folder/Zip{Style.RESET_ALL} (Untuk convert GIF lokal ke MP4)")
        print()
        
        user_input = UI.prompt("Masukkan Input")
        
        # Clean input
        user_input = user_input.strip()
        if user_input.startswith('& '): # PowerShell drag-and-drop handling
            user_input = user_input[2:].strip()
        user_input = user_input.strip('"\'')
        
        # Detect Mode: Local
        if os.path.exists(user_input):
            mode_desc = "Folder" if os.path.isdir(user_input) else "Zip Archive"
            UI.info(f"Detected {Fore.GREEN}{mode_desc}{Style.RESET_ALL} input.")
            UI.info(f"Path: {user_input}")
            if UI.confirm("Proceed with local processing?"):
                self.process_local_input(user_input)
            return

        # URL Logic
        is_profile = False
        target_id = self.extract_shortcode(user_input) # Try as post first
        
        if not target_id:
            # Check if profile
            parsed = urllib.parse.urlparse(user_input)
            path_parts = [p for p in parsed.path.split('/') if p]
            if len(path_parts) == 1:
                target_id = path_parts[0]
                is_profile = True
        
        if not target_id:
            UI.error("Could not understand that input.")
            UI.info("Expected: Instagram URL (Post or Profile) or valid Local Path.")
            return
        
        target_url = user_input if is_profile else f"https://www.instagram.com/p/{target_id}/"
        if is_profile:
             target_url = f"https://www.instagram.com/{target_id}/"

        mode_label = "PROFILE" if is_profile else "POST"
        UI.info(f"Detected {Fore.GREEN}Instagram {mode_label}{Style.RESET_ALL}: {target_id}")
        
        if not UI.confirm("Start browser session?"):
            UI.warning("Operation cancelled.")
            return
        
        # Output Directory Structure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = "profile" if is_profile else "post"
        session_folder = os.path.join(CONFIG.BASE_OUTPUT_DIR, f"{target_id}_{timestamp}")
        
        media_dir = os.path.join(session_folder, "media")
        stickers_dir = os.path.join(session_folder, "stickers") # For post comments
        converted_dir = os.path.join(session_folder, "converted")
        stories_dir = os.path.join(session_folder, "stories")
        highlights_dir = os.path.join(session_folder, "highlights")
        
        os.makedirs(session_folder, exist_ok=True)
        if not is_profile and CONFIG.DOWNLOAD_MEDIA: os.makedirs(media_dir, exist_ok=True)
        if not is_profile: os.makedirs(stickers_dir, exist_ok=True)
        if CONFIG.CONVERT_TO_MP4: os.makedirs(converted_dir, exist_ok=True) # General use

        UI.section("BROWSER SESSION")
        
        sticker_urls = set()
        comments = []
        
        with sync_playwright() as pw:
            UI.info(f"Session: {CONFIG.USER_DATA_DIR}")
            
            ctx = pw.chromium.launch_persistent_context(
                user_data_dir=CONFIG.USER_DATA_DIR,
                headless=CONFIG.HEADLESS,
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                args=['--disable-blink-features=AutomationControlled']
            )
            
            try:
                page = ctx.new_page()
                page.set_default_timeout(60000)
                
                # Check auth on target
                if not self.ensure_authentication(page, target_url):
                    UI.error("Could not access target. Exiting.")
                    ctx.close()
                    return
                
                if is_profile:
                    # PROFILE MODE
                    self.extract_profile_pic(page, target_id, session_folder)
                    self.extract_stories(page, target_id, stories_dir)
                    self.extract_highlights(page, target_id, highlights_dir)
                else:
                    # POST MODE
                    # 1. Post Media
                    if CONFIG.DOWNLOAD_MEDIA:
                        self.extract_post_media(page, media_dir)

                    # 2. Comments & Stickers
                    scan_res = self.scan_comments(page)
                    sticker_urls = scan_res.get("stickers", set())
                    comments = scan_res.get("comments", [])
                
                page.close()
                
            finally:
                ctx.close()
        
        # Post-Processing
        if not is_profile:
            # Save Comments
            if comments:
                with open(os.path.join(session_folder, "comments.json"), 'w', encoding='utf-8') as f:
                    json.dump(comments, f, indent=2, ensure_ascii=False)
                UI.success(f"Saved {len(comments)} comments.")
                
            if not sticker_urls:
                UI.warning("No GIF stickers found in comments.")
            else:
                # Download Stickers
                UI.section(f"DOWNLOAD ({len(sticker_urls)} stickers)")
                downloaded = self.download_stickers_parallel(list(sticker_urls), stickers_dir)
                
                if not downloaded:
                    UI.error("No stickers downloaded.")
                else:
                    # Convert
                    if CONFIG.CONVERT_TO_MP4:
                        self.convert_stickers_parallel(downloaded, converted_dir)
        
        # Archive
        UI.section("FULL ARCHIVE")
        zip_path = shutil.make_archive(session_folder, 'zip', CONFIG.BASE_OUTPUT_DIR, f"{target_id}_{timestamp}")
        UI.success(f"Archive: {zip_path}")
        
        # Final Report
        duration = time.time() - start_time
        count_report = len(sticker_urls) if not is_profile else "N/A"
        UI.final_report(count_report, duration, zip_path)
        print(f"\n    {Fore.YELLOW}LOKASI HASIL (OUTPUT):{Style.RESET_ALL}")
        print(f"    - Folder: {Fore.GREEN}{session_folder}{Style.RESET_ALL}")
        print(f"    - File ZIP: {Fore.GREEN}{zip_path}.zip{Style.RESET_ALL}")
        print(f"    {Style.DIM}Semua hasil download ada di dalam folder '{CONFIG.BASE_OUTPUT_DIR}'{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        grabber = BrowserGifGrabber()
        grabber.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}  Aborted by user.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        LOG.critical(f"Fatal: {e}", exc_info=True)
        print(f"\n{Fore.RED}  [FATAL] {e}{Style.RESET_ALL}")
        sys.exit(1)
