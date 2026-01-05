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
- Installs Python dependencies.
- Sets up the browser environment.
- Launches the tool.

### 2. Enter Input
When prompted, you have two smart options:
- **Option A (URL)**: Paste an Instagram post link to scrape live data.
- **Option B (Local)**: Drag a folder/zip of GIFs onto the window to convert them.

### 3. Review & Export
All results are organized in the `downloads/` directory and zipped into a single archive for you automatically.

---

## 🇮🇩 Panduan Untuk Pemula (Bahasa Indonesia)

Tool ini sangat mudah digunakan untuk mengambil **semua aset** (foto, video, stiker, komentar) dari Instagram:

1.  **Cara Buka**: Klik 2x file `setup_and_run.bat`. Tunggu sampai muncul tulisan "Masukkan Input".
2.  **Cara Download**: 
    -   **Postingan**: Copy link postingan (Post/Reel), lalu Paste di terminal.
    -   **Profil (BARU)**: Copy link profil (contoh: `instagram.com/jokowi`), lalu Paste untuk download **Story**, **Highlight**, dan **Foto Profil**.
    -   **File Lokal**: Geser (drag) folder/zip berisi GIF ke dalam layar hitam terminal.
3.  **Di Mana Hasilnya?**: 
    -   Semua hasil download masuk ke folder baru bernama **`downloads`**.
    -   Di dalamnya ada folder khusus sesuai link/nama file yang Anda masukkan.
    -   Isinya: Foto/Video aslinya, Stiker GIF-nya, dan versi MP4-nya.

---

## 🛠 Prerequisites

- **Python 3.8+**
- **Windows System** (Optimized for PowerShell/CMD).

---

## 💎 Author
Developed with ❤️ by **@ardel.yo** (TikTok/IG) | **@ardelyo** (GitHub).
*Version 6.0.0 (Enterprise Edition)*
