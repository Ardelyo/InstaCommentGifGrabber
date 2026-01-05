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
from playwright.sync_api import sync_playwright, Page

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
    TEMP_DIR: str = f"stickers_{int(time.time())}"
    USER_DATA_DIR: str = "ig_browser_session"
    SCROLL_PAUSE: float = 2.0
    MAX_SCROLLS: int = 150  # Increased for larger posts
    HEADLESS: bool = False
    MAX_WORKERS: int = 5    # For parallel downloads

CONFIG = Config()

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
    │   ██╗███╗   ██╗███████╗████████╗ █████╗                      │
    │   ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗                     │
    │   ██║██╔██╗ ██║███████╗   ██║   ███████║                     │
    │   ██║██║╚██╗██║╚════██║   ██║   ██╔══██║                     │
    │   ██║██║ ╚████║███████║   ██║   ██║  ██║                     │
    │   ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝                     │
    │                                                              │
    │{Fore.WHITE}          GIF Grabber v6.0  │  Enterprise Edition          {Fore.CYAN}│
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
    def scroll_and_extract(self, page: Page, target_url: str) -> Set[str]:
        """v6.0: Smooth scrolling with smart end-of-comment detection."""
        UI.step(2, 3, "Scanning comments for GIF stickers...")
        
        found_urls: Set[str] = set()
        last_count = 0
        no_change_count = 0
        
        CONTAINER_SEL = "div.x5yr21d.xw2csxc.x1odjw0f.x1n2onr6"
        PLUS_ICON_SEL = "svg[aria-label='Load more comments']"
        VIEW_REPLIES_SEL = "span:has-text('View all'), span:has-text('replies')"
        
        for scroll_num in range(CONFIG.MAX_SCROLLS):
            # 1. Navigation Check
            if page.url.split('?')[0].rstrip('/') != target_url.rstrip('/'):
                LOG.warning("Navigation drift detected, auto-recovering...")
                page.goto(target_url, wait_until="load")
                time.sleep(2)

            # 2. Extract (Fast JS execution)
            new_urls = page.evaluate(f'''
                (containerSel) => {{
                    const container = document.querySelector(containerSel);
                    if (!container) return [];
                    const found = [];
                    // Giphy specific
                    container.querySelectorAll('img[src*="giphy.com"]').forEach(img => {{
                        if (img.src) found.push(img.src);
                    }});
                    // Sticker classes
                    container.querySelectorAll('img.x12ol6y4').forEach(img => {{
                        if (img.src) found.push(img.src);
                    }});
                    return found;
                }}
            ''', CONTAINER_SEL)
            
            for u in new_urls: found_urls.add(u)
            
            # Print status
            print(f"\r    {Fore.CYAN}➤ {Style.BRIGHT}Scanning:{Style.RESET_ALL} {scroll_num+1:<3} scrolls | {len(found_urls):<3} stickers found", end='', flush=True)

            # 3. Smart Completion Detection
            container_exists = page.query_selector(CONTAINER_SEL) is not None
            has_load_more = page.query_selector(f"{CONTAINER_SEL} {PLUS_ICON_SEL}") is not None
            
            if len(found_urls) == last_count:
                no_change_count += 1
                # If no new stickers AND no "Load more" buttons, we're likely done
                if no_change_count >= 6 and not has_load_more:
                    UI.info("\n    No more comments detected.")
                    break
            else:
                no_change_count = 0
            
            last_count = len(found_urls)

            # 4. Safe Interactions
            try:
                container = page.query_selector(CONTAINER_SEL)
                if container:
                    # Click Plus icons
                    plus = container.query_selector(PLUS_ICON_SEL)
                    if plus: 
                        plus.click()
                        time.sleep(random.uniform(1.0, 1.5))
                    
                    # Click Reply buttons
                    reply = container.query_selector(VIEW_REPLIES_SEL)
                    if reply: 
                        reply.click()
                        time.sleep(random.uniform(0.5, 0.8))
            except: pass

            # 5. Natural Smooth Scroll
            page.evaluate(f'''
                (sel) => {{
                    const el = document.querySelector(sel);
                    if (el) {{
                        // Smoothly scroll to bottom in 3 steps
                        const target = el.scrollHeight;
                        const chunk = (target - el.scrollTop) / 3;
                        let current = el.scrollTop;
                        const interval = setInterval(() => {{
                            current += chunk;
                            el.scrollTop = current;
                            if (current >= target) clearInterval(interval);
                        }}, 50);
                    }}
                }}
            ''', CONTAINER_SEL)
            
            time.sleep(CONFIG.SCROLL_PAUSE + random.uniform(0.2, 0.5))
        
        print() # Newline
        return found_urls
    
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

    def run(self):
        # Startup Sequence
        UI.clear()
        print(f"\n{Fore.CYAN}    Initializing Enterprise Core...{Style.RESET_ALL}")
        for _ in range(3):
            time.sleep(0.2)
            print(f"{Fore.CYAN}    .{Style.RESET_ALL}", end='', flush=True)
        time.sleep(0.5)
        
        start_time = time.time()
        UI.clear()
        UI.banner()
        
        UI.section("SETUP")
        url_input = UI.prompt("Enter Instagram Post URL")
        shortcode = self.extract_shortcode(url_input)
        
        if not shortcode:
            UI.error("Invalid Instagram URL format.")
            return
        
        target_url = f"https://www.instagram.com/p/{shortcode}/"
        UI.info(f"Target: {shortcode}")
        
        UI.section("BROWSER SESSION")
        
        sticker_urls = set()
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
                
                if not self.ensure_authentication(page, target_url):
                    UI.error("Could not access target post. Exiting.")
                    ctx.close()
                    return
                
                # Scrape
                sticker_urls = self.scroll_and_extract(page, target_url)
                page.close()
                
            finally:
                ctx.close()
        
        if not sticker_urls:
            UI.warning("No GIF stickers found in comments.")
            return
            
        # Scan Summary
        UI.stats_box({
            "Target Found": str(len(sticker_urls)),
            "Scan Duration": f"{time.time() - start_time:.1f}s",
            "Status": "Ready for DL"
        })
        UI.wait_for_enter("Ready to download? Press ENTER")
        
        # Download Phase (Turbo)
        UI.section(f"TURBO DOWNLOAD ({CONFIG.MAX_WORKERS} threads)")
        os.makedirs(CONFIG.TEMP_DIR, exist_ok=True)
        
        downloaded = self.download_stickers_parallel(list(sticker_urls), CONFIG.TEMP_DIR)
        
        if not downloaded:
            UI.error("No stickers downloaded.")
            if os.path.exists(CONFIG.TEMP_DIR): shutil.rmtree(CONFIG.TEMP_DIR)
            return
        
        # Archive
        UI.section("SAVE ARCHIVE")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = filedialog.asksaveasfilename(
            initialfile=f"stickers_{shortcode}_{timestamp}.zip",
            title="Save Sticker Archive",
            filetypes=[("ZIP Archive", "*.zip")],
            defaultextension=".zip"
        )
        
        if save_path:
            with zipfile.ZipFile(save_path, 'w') as zf:
                for f in downloaded:
                    zf.write(f, os.path.basename(f))
            UI.success(f"Saved to: {save_path}")
        else:
            UI.warning("Save cancelled.")
        
        # Cleanup
        shutil.rmtree(CONFIG.TEMP_DIR)
        
        # Final Report
        duration = time.time() - start_time
        UI.final_report(len(downloaded), duration, save_path if save_path else "")
        UI.info(f"Log file: {CONFIG.LOG_FILE}")

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
