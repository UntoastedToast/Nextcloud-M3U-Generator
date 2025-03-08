import re
import os
import sys
import urllib.parse
import asyncio
import time
import shutil
from urllib.parse import urlparse, parse_qs
from typing import List, Optional


class Colors:
    """Terminal color codes"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class TerminalUI:
    """Handles all terminal UI elements and user interaction"""
    
    LOGO = f"""
{Colors.CYAN}+-----------------------------+
|  Nextcloud M3U Generator    |
+-----------------------------+{Colors.RESET}

{Colors.GREEN}🎬 Create video playlists from Nextcloud shared folders 🎬{Colors.RESET}
"""
    
    def __init__(self):
        self.term_width = shutil.get_terminal_size(fallback=(80, 24)).columns
        self.box_width = min(70, max(50, self.term_width - 10))
    
    def show_logo(self):
        """Display the application logo"""
        print(self.LOGO)
    
    def _strip_ansi_codes(self, text: str) -> str:
        """Remove ANSI color codes for length calculations"""
        return re.sub(r'\033\[[0-9;]*m', '', text)
    
    def draw_box(self, lines: List[str], border_color: str = Colors.CYAN, 
                 text_color: str = Colors.WHITE, style: str = "simple") -> None:
        """Draw a box with text using ASCII characters"""
        content_width = max(len(self._strip_ansi_codes(line)) for line in lines) if lines else 0
        box_width = min(self.box_width, content_width + 4)
        
        # Box characters
        h_char, v_char = "-", "|"
        tl, tr, bl, br = "+", "+", "+", "+"
            
        # Top border
        print(f"{border_color}{tl}{h_char * (box_width - 2)}{tr}{Colors.RESET}")
        
        # Content with padding
        for line in lines:
            clean_line = self._strip_ansi_codes(line)
            padding = box_width - 2 - len(clean_line)
            formatted_line = line if "\033[" in line else f"{text_color}{line}{Colors.RESET}"
            print(f"{border_color}{v_char}{Colors.RESET} {formatted_line}{' ' * padding}{border_color}{v_char}{Colors.RESET}")
        
        # Bottom border
        print(f"{border_color}{bl}{h_char * (box_width - 2)}{br}{Colors.RESET}")
    
    def draw_header(self, title: str, color: str = Colors.MAGENTA) -> None:
        """Draw a section header that adapts to terminal width"""
        width = min(self.term_width - 2, 60)
        clean_title = self._strip_ansi_codes(title)
        side_width = (width - len(clean_title) - 5) // 2
        print(f"\n{color}+{'-' * side_width} 📌 {title} {'-' * side_width}+{Colors.RESET}")
    
    def draw_subheader(self, title: str, color: str = Colors.CYAN) -> None:
        """Draw a subsection header"""
        print(f"\n{color}🔹 {title} {Colors.RESET}")
        print(f"{color}{'-' * min(self.term_width - 2, 60)}{Colors.RESET}")
    
    def print_message(self, message: str, message_type: str = "info") -> None:
        """Print a formatted message based on type"""
        prefixes = {
            "success": f"{Colors.GREEN}✅ ",
            "info": f"{Colors.BLUE}ℹ️ ",
            "warning": f"{Colors.YELLOW}⚠️ ",
            "error": f"{Colors.RED}❌ "
        }
        colors = {
            "success": Colors.GREEN,
            "info": Colors.BLUE,
            "warning": Colors.YELLOW,
            "error": Colors.RED
        }
        
        prefix = prefixes.get(message_type, prefixes["info"])
        color = colors.get(message_type, colors["info"])
        
        print(f"{prefix}{message}{Colors.RESET}")
    
    def print_section(self, title: str) -> None:
        """Print a section title"""
        self.draw_header(title)
    
    def print_subsection(self, title: str) -> None:
        """Print a subsection title"""
        self.draw_subheader(title)
    
    def print_loading(self, message: str, duration: int = 3) -> None:
        """Display a loading animation for the specified duration"""
        symbols = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        end_time = time.time() + duration
        i = 0
        
        print("", end="", flush=True)
        while time.time() < end_time:
            print(f"\r{Colors.BLUE}{symbols[i % len(symbols)]} {message}{Colors.RESET}", end="", flush=True)
            time.sleep(0.1)
            i += 1
        print(f"\r{Colors.GREEN}✓ {message} - Completed!{Colors.RESET}", flush=True)
        print("")
    
    def get_user_input(self, prompt: str, default: str = "", password: bool = False) -> str:
        """Get input from the user with colored prompt"""
        full_prompt = f"{Colors.GREEN}{prompt}{Colors.RESET}"
        if default:
            full_prompt = f"{Colors.GREEN}{prompt} [{default}]: {Colors.RESET}"
            
        response = input(full_prompt)
        return response if response else default
    
    def display_file_list(self, files: List[str], max_display: int = 10) -> None:
        """Display a formatted list of files"""
        if not files:
            return
            
        padding = 2 if len(files) < 100 else 3
        
        for i, filename in enumerate(files[:max_display]):
            num = f"{i+1}".zfill(padding)
            
            # Select emoji based on file extension
            if filename.lower().endswith('.mkv'):
                emoji = "🎬"
            elif filename.lower().endswith('.mp4'):
                emoji = "📹"
            else:
                emoji = "🎞️"
                
            print(f"  {Colors.GREEN}{num}.{Colors.RESET} {emoji} {Colors.CYAN}{filename}{Colors.RESET}")
            
        if len(files) > max_display:
            remain = len(files) - max_display
            print(f"\n  {Colors.YELLOW}... and {remain} more files{Colors.RESET}")
            
        print(f"\n  {Colors.GREEN}📊 Total: {len(files)} video files{Colors.RESET}")


class NextcloudURLParser:
    """Parse and extract information from Nextcloud URLs"""
    
    @staticmethod
    def extract_token_from_url(url: str) -> Optional[str]:
        """Extract the share token from a Nextcloud URL"""
        # Pattern 1: /s/TOKEN format
        s_match = re.search(r'/s/([a-zA-Z0-9]+)', url)
        if s_match:
            return s_match.group(1)
        
        # Pattern 2: ?token=TOKEN format
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        if 'token' in query_params:
            return query_params['token'][0]
        
        # Pattern 3: /index.php/s/TOKEN format
        index_match = re.search(r'/index\.php/s/([a-zA-Z0-9]+)', url)
        if index_match:
            return index_match.group(1)
        
        return None
    
    @staticmethod
    def extract_base_url(url: str) -> str:
        """Extract the base URL from a complete URL"""
        parsed_url = urlparse(url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}"


class HTMLParser:
    """Parse HTML content to extract video files"""
    
    def __init__(self, ui: TerminalUI, debug_dir: str):
        self.ui = ui
        self.debug_dir = debug_dir
    
    def extract_video_files(self, html_content: str) -> List[str]:
        """Extract video files from HTML content"""
        self.ui.print_subsection("Searching for Video Files")
        video_files = set()  # Use a set to avoid duplicates
        
        self.ui.print_message("🔍 Searching for videos with video MIME type...", "info")
        # Method 1: Files with video MIME type
        pattern1 = r'data-type="file"[^>]*data-file="([^"]*)"[^>]*data-mime="video/[^"]*"'
        matches1 = re.findall(pattern1, html_content)
        for filename in matches1:
            video_files.add(filename)
        
        if matches1:
            self.ui.print_message(f"📽️ {len(matches1)} videos found with video MIME type", "success")
            
        # Method 2: Files with video extensions
        self.ui.print_message("🔍 Searching for videos by file extensions...", "info")
        video_extensions = r'\.(mkv|mp4|avi|mov|wmv|flv|webm)'
        pattern2 = r'data-file="([^"]*' + video_extensions + ')"'
        matches2 = re.findall(pattern2, html_content, re.IGNORECASE)
        
        before_count = len(video_files)
        for match in matches2:
            if isinstance(match, tuple):
                filename = match[0]  # Get the full filename
            else:
                filename = match
            video_files.add(filename)
            
        new_count = len(video_files) - before_count
        if new_count > 0:
            self.ui.print_message(f"🎞️ {new_count} additional videos found by file extensions", "success")
        
        result = sorted(list(video_files))
        self.ui.print_message(f"🎥 Total of {len(result)} unique video files found", "success")
        
        # Save the found files to debug directory
        self._save_file_list(result)
        
        # Show example of found files
        if result:
            self.ui.print_subsection("Found Videos")
            self.ui.display_file_list(result)
        
        return result
    
    def _save_file_list(self, files: List[str]) -> None:
        """Save the list of found files to a debug file"""
        found_files_path = os.path.join(self.debug_dir, "found_files.txt")
        try:
            with open(found_files_path, "w", encoding="utf-8") as f:
                f.write(f"Found video files: {len(files)}\n\n")
                for i, filename in enumerate(files):
                    f.write(f"{i+1}. {filename}\n")
            self.ui.print_message(f"📋 List of found files saved to {found_files_path}", "info")
        except Exception as e:
            self.ui.print_message(f"Could not save found files to debug file: {str(e)}", "warning")


class HTMLContentFetcher:
    """Fetch HTML content from Nextcloud shared folders"""
    
    def __init__(self, ui: TerminalUI, debug_dir: str):
        self.ui = ui
        self.debug_dir = debug_dir
    
    async def fetch_html_content(self, url: str, wait_time: int = 3) -> Optional[str]:
        """Fetch HTML content with Playwright for JavaScript rendering"""
        try:
            from playwright.async_api import async_playwright
            
            self.ui.print_message(f"🌐 Accessing URL: {url}", "info")
            self.ui.print_loading("Starting browser", 1)
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(viewport={"width": 1280, "height": 800})
                page = await context.new_page()
                
                self.ui.print_message(f"🔄 Loading page, please wait...", "info")
                await page.goto(url, wait_until="networkidle")
                self.ui.print_message(f"⏱️ Waiting {wait_time} seconds for page to load...", "info")
                await asyncio.sleep(wait_time)
                
                try:
                    # Wait for the file table
                    self.ui.print_message("🔍 Looking for file table...", "info")
                    await page.wait_for_selector('.files-filestable', timeout=10000)
                    self.ui.print_message("📋 File table found!", "success")
                    
                    # Load all files by scrolling
                    self.ui.print_message("📜 Scrolling to load all files...", "info")
                    await self._scroll_to_load_all_files(page)
                    
                except Exception as e:
                    self.ui.print_message(f"Problem while scrolling: {str(e)}", "warning")
                
                # Get HTML content
                self.ui.print_message("📥 Capturing HTML content...", "info")
                html_content = await page.content()
                
                # Save HTML to debug directory
                self._save_html_content(html_content)
                
                await browser.close()
                self.ui.print_message("🌐 HTML content successfully loaded", "success")
                return html_content
                
        except Exception as e:
            self.ui.print_message(f"Problem with Playwright: {str(e)}", "error")
            
            # Fallback to simple HTTP request
            self.ui.print_message("🔄 Trying fallback with simple HTTP request...", "warning")
            try:
                import requests
                response = requests.get(url)
                response.raise_for_status()
                self.ui.print_message("📄 Fallback was successful", "success")
                return response.text
            except Exception as req_e:
                self.ui.print_message(f"Error fetching URL: {str(req_e)}", "error")
                return None
    
    async def _scroll_to_load_all_files(self, page) -> None:
        """Scroll the page to load all files"""
        # Count initial video files
        initial_files = await page.query_selector_all('tr[data-file$=".mkv"], tr[data-file$=".mp4"]')
        self.ui.print_message(f"🎬 Visible video files before scrolling: {len(initial_files)}", "info")
        
        # Try to scroll to summary or footer first
        if await self._try_scroll_to_element(page):
            return
            
        # Continuous scrolling as a last resort
        await self._continuous_scroll(page)
    
    async def _try_scroll_to_element(self, page) -> bool:
        """Try to scroll to summary or footer elements"""
        self.ui.print_message("🔍 Attempting to scroll to the end of the table...", "info")
        
        # Try with summary
        summary = await page.query_selector('tr.summary')
        if summary:
            await summary.scroll_into_view_if_needed()
            await asyncio.sleep(2)
            self.ui.print_message("📌 Scrolled to table summary", "success")
            return True
            
        # Try with tfoot
        tfoot = await page.query_selector('tfoot')
        if tfoot:
            await tfoot.scroll_into_view_if_needed()
            await asyncio.sleep(2)
            self.ui.print_message("📌 Scrolled to table footer", "success")
            return True
            
        return False
    
    async def _continuous_scroll(self, page) -> None:
        """Continuously scroll the page to load all files"""
        self.ui.print_message("📜 Starting continuous scrolling...", "info")
        last_file_count = 0
        progress_symbols = ["🔄", "⏳", "📊", "🔎"]
        
        for i in range(10):
            symbol = progress_symbols[i % len(progress_symbols)]
            await page.evaluate('window.scrollBy(0, 500)')
            await asyncio.sleep(0.5)
            
            current_files = await page.query_selector_all('tr[data-file$=".mkv"], tr[data-file$=".mp4"]')
            current_file_count = len(current_files)
            
            if i % 3 == 0 or current_file_count > last_file_count:
                self.ui.print_message(f"{symbol} Scroll progress: {current_file_count} video files found", "info")
            
            if current_file_count == last_file_count:
                # Try larger scroll
                self.ui.print_message("🔽 Trying larger scroll...", "info")
                await page.evaluate('window.scrollBy(0, 1000)')
                await asyncio.sleep(1)
                
                current_files = await page.query_selector_all('tr[data-file$=".mkv"], tr[data-file$=".mp4"]')
                current_file_count = len(current_files)
                
                if current_file_count == last_file_count:
                    self.ui.print_message("🛑 No new files found, ending scrolling", "info")
                    break
                    
            last_file_count = current_file_count
        
        # Final scroll to the end of the page
        self.ui.print_message("⬇️ Final scroll to the bottom of the page...", "info")
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(2)
        
        final_files = await page.query_selector_all('tr[data-file$=".mkv"], tr[data-file$=".mp4"]')
        self.ui.print_message(f"🎬 Total of {len(final_files)} video files found", "success")
    
    def _save_html_content(self, html_content: str) -> None:
        """Save HTML content to a debug file"""
        debug_html_path = os.path.join(self.debug_dir, "debug_content.html")
        try:
            with open(debug_html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            self.ui.print_message(f"🔍 HTML content saved to {debug_html_path}", "info")
            self.ui.print_message("💡 You can open this HTML file in a browser for inspection", "info")
        except Exception as e:
            self.ui.print_message(f"Could not save HTML to debug file: {str(e)}", "warning")
    
    @staticmethod
    def check_playwright_installation(ui: TerminalUI) -> bool:
        """Check if Playwright is installed and install it if needed"""
        try:
            import playwright
            ui.print_message("🎭 Playwright is installed and ready", "success")
            return True
        except ImportError:
            ui.print_message("🎭 Playwright is not installed", "warning")
            
            print()
            # Show Playwright installation info
            ui.draw_box([
                "Playwright is needed to load JavaScript content",
                "from Nextcloud. The installation will also download",
                "browser components (~150MB)."
            ], Colors.YELLOW)
            print()
            
            install = ui.get_user_input("Would you like to install Playwright now? (Y/n)")
            if install.lower() in ["", "y", "yes"]:
                try:
                    ui.print_loading("Installing Playwright", 1)
                    import subprocess
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
                    
                    ui.print_loading("Installing Playwright browsers (Chromium)", 2)
                    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
                    
                    ui.print_message("🎭 Playwright was successfully installed!", "success")
                    return True
                except Exception as e:
                    ui.print_message(f"Error installing Playwright: {str(e)}", "error")
                    print()
                    # Show manual installation instructions
                    ui.draw_box([
                        "Please install Playwright manually with:",
                        "  pip install playwright",
                        "  python -m playwright install"
                    ], Colors.YELLOW, Colors.CYAN)
                    return False
            else:
                ui.print_message("🎭 Playwright installation cancelled", "warning")
                return False


class PlaylistGenerator:
    """Generate M3U playlists from video files"""
    
    def __init__(self, ui: TerminalUI, base_url: str, share_token: str, path: str = ""):
        self.ui = ui
        self.base_url = base_url
        self.share_token = share_token
        self.path = path
    
    def create_direct_link(self, filename: str) -> str:
        """Create a direct download link for a file"""
        # Normalize path
        path = self.path or ""
        if path and not path.startswith('/'):
            path = '/' + path
        if path and not path.endswith('/'):
            path = path + '/'
        
        # URL encoding
        encoded_filename = urllib.parse.quote(filename)
        encoded_path = urllib.parse.quote(path.rstrip('/'))
        
        # Create direct link
        if encoded_path == '/' or encoded_path == '':
            return f"{self.base_url}/public.php/dav/files/{self.share_token}/{encoded_filename}"
        else:
            return f"{self.base_url}/public.php/dav/files/{self.share_token}{encoded_path}/{encoded_filename}"
    
    def create_playlist(self, video_files: List[str], output_file: str = "nextcloud_playlist.m3u") -> None:
        """Create an M3U playlist with direct download links"""
        self.ui.print_section("Playlist Creation")
        
        if not video_files:
            self.ui.print_message("No video files to add to the playlist!", "error")
            return
            
        self.ui.print_message(f"🎬 Creating playlist '{output_file}' with {len(video_files)} videos...", "info")
        
        # Show progress bar for larger playlists
        self._show_progress_bar(video_files)
        
        # Write the playlist file
        self._write_playlist_file(video_files, output_file)
            
        self.ui.print_message(f"🎬 Playlist created: {Colors.BOLD}{output_file}{Colors.RESET}", "success")
        self.ui.print_message(f"📊 Total of {Colors.BOLD}{len(video_files)}{Colors.RESET} video files in the playlist.", "success")
        
        # Show example of playlist
        self._show_playlist_preview(video_files, output_file)
    
    def _write_playlist_file(self, video_files: List[str], output_file: str) -> None:
        """Write playlist content to file"""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for filename in video_files:
                direct_link = self.create_direct_link(filename)
                display_name = os.path.splitext(filename)[0]
                
                f.write(f"#EXTINF:-1,{display_name}\n")
                f.write(f"{direct_link}\n")
    
    def _show_progress_bar(self, video_files: List[str]) -> None:
        """Show a progress bar for playlist creation"""
        if len(video_files) > 20:
            total = len(video_files)
            step = max(1, total // 20)  # Show maximum 20 progress steps
            
            self.ui.print_message(f"⏳ Generating links for {total} files...", "info")
            print(f"{Colors.BLUE}[", end="")
            
            for i in range(0, total, step):
                print(f"{Colors.GREEN}█", end="", flush=True)
                time.sleep(0.05)  # Small delay for visual effect
                
            print(f"{Colors.BLUE}]{Colors.RESET}")
    
    def _show_playlist_preview(self, video_files: List[str], output_file: str) -> None:
        """Show a preview of the playlist entries"""
        if not video_files:
            return
            
        self.ui.print_subsection("Sample Playlist Entries")
        
        for i, filename in enumerate(video_files[:5]):
            direct_link = self.create_direct_link(filename)
            
            # Different emojis for different file types
            if filename.lower().endswith('.mkv'):
                emoji = "🎬"
            elif filename.lower().endswith('.mp4'):
                emoji = "📹"
            else:
                emoji = "🎞️"
            
            # Formatted output
            print(f"  {Colors.GREEN}{i+1}.{Colors.RESET} {emoji} {Colors.CYAN}{filename}{Colors.RESET}")
            print(f"     {Colors.BLUE}🔗 {direct_link}{Colors.RESET}")
            print()
        
        if len(video_files) > 5:
            remain = len(video_files) - 5
            print(f"  {Colors.YELLOW}... and {remain} more entries in the playlist{Colors.RESET}")


class NextcloudPlaylistApp:
    """Main application class for Nextcloud Playlist Generator"""
    
    def __init__(self):
        self.ui = TerminalUI()
        self.debug_dir = self._ensure_debug_dir()
        self.html_fetcher = HTMLContentFetcher(self.ui, self.debug_dir)
        self.html_parser = HTMLParser(self.ui, self.debug_dir)
        
        # Configuration
        self.base_url = None
        self.share_token = None
        self.path = None
        self.video_files = []
    
    def _ensure_debug_dir(self) -> str:
        """Ensure that the debug directory exists"""
        debug_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_files")
        if not os.path.exists(debug_dir):
            try:
                os.makedirs(debug_dir)
                self.ui.print_message(f"Created debug directory: {debug_dir}", "info")
            except Exception as e:
                self.ui.print_message(f"Could not create debug directory: {str(e)}", "warning")
                # Fallback to current directory
                debug_dir = "."
        return debug_dir
    
    async def setup_configuration(self) -> bool:
        """Configure the application with user input"""
        self.ui.print_section("Configuration")
        
        # Show configuration info box
        self.ui.draw_box([
            "Enter the complete Nextcloud share URL",
            "Example: https://cloud.example.com/s/abcdefg123456"
        ])
        print()
        
        share_url = self.ui.get_user_input("🌐 Nextcloud share URL: ")
        if not share_url:
            self.ui.print_message("Share URL is required.", "error")
            return False
        
        # Extract token
        self.ui.print_message("🔑 Extracting share token from URL...", "info")
        self.share_token = NextcloudURLParser.extract_token_from_url(share_url)
        if not self.share_token:
            self.ui.print_message("Could not extract a valid share token from URL.", "error")
            manual_token = self.ui.get_user_input("🔑 Please enter the share token manually")
            if not manual_token:
                self.ui.print_message("Share token is required.", "error")
                return False
            self.share_token = manual_token
        else:
            self.ui.print_message(f"Share token: {Colors.BOLD}{self.share_token}{Colors.RESET}", "success")
        
        # Extract base URL
        self.base_url = NextcloudURLParser.extract_base_url(share_url)
        self.ui.print_message(f"🌐 Base URL: {Colors.CYAN}{self.base_url}{Colors.RESET}", "info")
        
        # Get path
        print()
        self.path = self.ui.get_user_input("📁 Path to folder (e.g. 'Season 1' or leave empty)")
        if self.path:
            self.ui.print_message(f"📁 Using path: {Colors.CYAN}{self.path}{Colors.RESET}", "info")
        else:
            self.ui.print_message("📁 Using root directory", "info")
            
        return True
    
    async def get_html_content(self, share_url: str) -> Optional[str]:
        """Get HTML content either automatically or manually"""
        print()
        crawl_html = self.ui.get_user_input("🔄 Automatically fetch HTML? (Y/n)", "Y")
        
        self.ui.print_section("Processing")
        html_content = ""
        
        if crawl_html.lower() in ["", "y", "yes"] and HTMLContentFetcher.check_playwright_installation(self.ui):
            self.ui.print_loading("Preparing HTML retrieval", 1)
            html_content = await self.html_fetcher.fetch_html_content(share_url, wait_time=5)
        else:
            # Manual HTML input methods
            html_content = await self._get_manual_html_input()
        
        return html_content
    
    async def _get_manual_html_input(self) -> str:
        """Get HTML content manually from file or input"""
        self.ui.print_subsection("Manual HTML Input")
        html_source = self.ui.get_user_input("Load HTML from a file (f) or paste directly (p)?", "p")
        
        if html_source.lower() == 'f':
            html_file = self.ui.get_user_input("📄 Path to HTML file")
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                self.ui.print_message(f"📄 HTML loaded from file '{html_file}'", "success")
                return html_content
            except Exception as e:
                self.ui.print_message(f"Error reading file: {str(e)}", "error")
                return ""
        else:
            print()
            # Display HTML input instructions
            self.ui.draw_box([
                "Paste the HTML code and finish with:",
                "- Ctrl+D (on Unix/Linux/macOS)",
                "- Ctrl+Z followed by Enter (on Windows)"
            ])
            print()
            
            try:
                html_lines = []
                try:
                    while True:
                        line = input()
                        html_lines.append(line)
                except EOFError:
                    pass
                html_content = '\n'.join(html_lines)
                self.ui.print_message("📄 HTML code successfully read", "success")
                return html_content
            except Exception as e:
                self.ui.print_message(f"Error reading input: {str(e)}", "error")
                return ""
    
    async def get_video_files(self, html_content: str) -> List[str]:
        """Extract video files from HTML content or manual input"""
        if not html_content:
            self.ui.print_message("Could not obtain HTML content", "error")
            return []
            
        # Extract video files
        video_files = self.html_parser.extract_video_files(html_content)
        
        if not video_files:
            self.ui.print_message("No video files found in HTML", "error")
            video_files = await self._get_manual_video_files()
        
        return video_files
    
    async def _get_manual_video_files(self) -> List[str]:
        """Get video files through manual input"""
        print()
        manual_input = self.ui.get_user_input("Would you like to enter the files manually? (Y/n)", "Y")
        
        if manual_input.lower() in ["", "y", "yes"]:
            manual_files = []
            
            self.ui.print_subsection("Manual File Entry")
            self.ui.print_message("Enter the names of video files (press Enter without input to finish)", "info")
            
            i = 1
            while True:
                filename = self.ui.get_user_input(f"🎬 File {i}")
                if not filename:
                    break
                    
                # Add .mkv extension if no video extension is present
                if not any(filename.lower().endswith(ext) for ext in ['.mkv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']):
                    filename += '.mkv'
                    self.ui.print_message(f"Added .mkv extension: {Colors.CYAN}{filename}{Colors.RESET}", "info")
                
                manual_files.append(filename)
                i += 1
            
            return manual_files
        
        return []
    
    async def create_playlist(self, video_files: List[str]) -> None:
        """Create a playlist file with the found video files"""
        if not video_files:
            self.ui.print_message("No video files found or entered. Exiting program.", "error")
            return
        
        # Create playlist generator
        playlist_gen = PlaylistGenerator(self.ui, self.base_url, self.share_token, self.path)
        
        # Get output file name
        self.ui.print_section("Playlist Creation")
        output_file = self.ui.get_user_input("📝 Playlist filename", "nextcloud_playlist.m3u")
        if not output_file.strip():
            output_file = "nextcloud_playlist.m3u"
        elif not output_file.lower().endswith('.m3u'):
            output_file += '.m3u'
            self.ui.print_message(f"Added .m3u extension: {Colors.CYAN}{output_file}{Colors.RESET}", "info")
        
        # Create the playlist
        playlist_gen.create_playlist(video_files, output_file)
        
        # Show test link
        self.show_final_info(playlist_gen, video_files[0] if video_files else "")
    
    def show_final_info(self, playlist_gen: PlaylistGenerator, sample_file: str) -> None:
        """Show final information and instructions"""
        self.ui.print_section("Finished")
        
        # Instructions
        instructions = [
            f"{Colors.BOLD}✅ Done! The video playlist can now be opened in VLC.{Colors.RESET}",
            "",
            "📝 Notes for playing videos in VLC Media Player:",
            "",
            "1. If VLC asks for credentials:",
            f"{Colors.CYAN}   - Username: {self.share_token}{Colors.RESET}",
            f"{Colors.CYAN}   - Password: [Your share password, if any]{Colors.RESET}",
            "",
            "2. You can save these credentials in VLC under:",
            f"{Colors.CYAN}   Tools → Preferences → Input/Codecs → Save credentials{Colors.RESET}"
        ]
        
        self.ui.draw_box(instructions, Colors.GREEN)
    
    async def run(self) -> None:
        """Run the main application"""
        # Show logo
        self.ui.show_logo()
        
        # Check dependencies
        self.ui.print_section("System Check")
        HTMLContentFetcher.check_playwright_installation(self.ui)
        
        # Configure the application
        if not await self.setup_configuration():
            return
        
        # Get HTML content
        html_content = await self.get_html_content(f"{self.base_url}/s/{self.share_token}")
        
        # Get video files
        self.video_files = await self.get_video_files(html_content)
        
        # Create playlist
        await self.create_playlist(self.video_files)


async def main() -> None:
    """Main entry point for the application"""
    app = NextcloudPlaylistApp()
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())