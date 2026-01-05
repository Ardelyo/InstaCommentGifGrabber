# 📸 Instagram Asset Grabber v6.0 (Enterprise)
> **Master the Art of Instagram Asset Extraction with the Turbo Parallel Engine.**

A high-performance, intelligent CLI tool designed for maximum speed. Extract **high-res images**, **Reels**, **Carousels**, **GIF stickers**, and **Comments** in parallel. Optimized for creators who need all assets *now*.

---

## 🚀 Key Features

*   **Turbo Parallel Engine**: 
    *   **Multitasked Scraping**: Downloads images and videos across multiple threads simultaneously.
    *   **Parallel Conversion**: Converts entire batches of GIFs to MP4 in seconds using all available CPU cores.
*   **Smart Input**: Drag-and-drop a URL, a Folder, or a Zip file directly into the terminal.
*   **Complete Asset Extraction**:
    *   **Media**: Downloads full-quality images, videos, and multi-slide carousels.
    *   **Stickers**: Extracts Giphy/Instagram stickers from comments.
    *   **Comments**: Saves text comments into a structured `comments.json`.
*   **Batch Conversion**: Automatically converts all GIFs to **MP4 (h.264)** for easier use in video editors.
*   **Enterprise UI**: A beautiful, responsive terminal interface with progress bars and status reports (Bahasa Indonesia & English).
*   **Secure & Robust**: Persistent browser sessions with automated login handling.

---

## 🚦 How to Use

### 1. One-Click Setup
Double-click `setup_and_run.bat`. This automatically:
# 📸 Instagram Asset Grabber v6.0 (Enterprise Edition)
> The ultimate high-performance tool for archiving Instagram content: Posts, Reels, Stories, Highlights, Comments, and Stickers.

---

## 🚀 Key Features (v6.0)

| Feature | Description |
| :--- | :--- |
| **Full Asset Extraction** | Downloads Images, Videos, Carousels, and HD Profile Pictures. |
| **Story & Highlights** | Archive 24h Stories and permanent Highlight albums automatically. |
| **Comment Scraper** | Extracts text comments and lists of usernames to `comments.json`. |
| **GIF Sticker Hub** | Finds and downloads GIF stickers used in comments. |
| **Turbo Parallel Engine** | Concurrent downloading and processing for up to 10x speed. |
| **GIF to MP4 Converter** | Auto-converts animated stickers to high-quality MP4 using MoviePy. |
| **Local Processing** | Drag-and-drop local GIF folders/zips for batch conversion. |

---

## 🇮🇩 Panduan Untuk Pemula (Bahasa Indonesia)

Tool ini dirancang agar sangat mudah digunakan oleh siapa saja:

1.  **Persiapan**: Klik 2x file `setup_and_run.bat`. Ikuti instruksi di layar (bot akan menginstall semua yang dibutuhkan secara otomatis).
2.  **Mode Download**:
    -   **Postingan**: Paste link Post/Reel untuk ambil foto, video, dan komentar.
    -   **Profil User**: Paste link profil (contoh: `instagram.com/ardel.yo`) untuk ambil **Story**, **Highlights**, dan **Foto Profil HD**.
3.  **Mode Konversi**: Punya folder penuh GIF? Tarik (Drag) folder tersebut ke dalam terminal untuk mengubah semuanya jadi MP4 secara otomatis.
4.  **Menu Interaktif**: Sekarang Anda bisa memilih folder penyimpanan, mengatur kedalaman scan, dan memilih jenis file apa saja yang ingin didownload.
5.  **Hasil**: Cek folder **`downloads`**. Semua sudah rapi dalam folder masing-masing dan tersedia dalam format `.zip`.

---

## 🛠️ Advanced Usage (CLI)

### Options at Runtime
When you start a session, the tool will prompt for:
-   **Output Directory**: Specify a custom path (e.g., `D:/Archive/IG`).
-   **Scan Depth**: How many "scrolls" to perform (depth of comments).
-   **Content Filters**: Selectively enable/disable Media, Comments, or Stickers.

### Requirements
-   Python 3.8+
-   Playwright (Automated browser)
-   MoviePy (Media processing)

---

## 📜 Roadmap & Future UX
- [ ] **Phase 4**: Desktop GUI for a full windowed experience.
- [ ] **Phase 5**: Google Colab / Cloud version for Mobile users.
- [ ] **Phase 6**: Smart background monitoring (Auto-grab new stories).

---

## 👨‍💻 Credits
Developed by **@ardel.yo** (IG/TikTok) | **@ardelyo** (GitHub)
*Built for the community. Use responsibly.*
*Version 6.0.0 (Enterprise Edition)*
