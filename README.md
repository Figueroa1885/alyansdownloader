# 🎮 Alyan's FitGirl Downloader

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge&logo=windows)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A fast, interactive, and easy-to-use Command Line Interface (CLI) tool to extract and download FitGirl Repack multi-part files directly from their webpage. 

Say goodbye to manually clicking through dozens of links! This tool fetches `fuckingfast.co` links automatically and downloads them with a beautiful progress bar.

---

## ✨ Features

- **🚀 Automated Link Extraction:** Just paste the FitGirl repack page URL. The tool finds all the direct download links for you.
- **📦 Smart Part Selection:** Download `all` parts, specific parts (like `1,3,5`), or a range of parts (like `1-10`).
- **resume Resumable Downloads:** Skips automatically if the file already exists in your destination folder.
- **🎨 Beautiful UI:** Powered by [Rich](https://github.com/Textualize/rich), featuring progress bars, colored tables, and transfer speeds.

---

## 📥 How to Download (Easy Way)

You **do not** need Python installed to run this program! 

1. Go to the [Releases page](../../releases) on this repository.
2. Under the latest release, download the `alyans_fitgirl_downloader.exe` file from the **Assets** section.
3. Double-click the `.exe` file to run it. 

*(Note: Windows SmartScreen might show a warning since the `.exe` isn't digitally signed by a publisher. Click "More info" -> "Run anyway").*

---

## 🛠️ How to Use

1. **Launch the app** (`fitgirl_downloader.exe`).
2. **Step 1:** Paste the URL of the FitGirl repack page you want to download from and press Enter.
3. **Step 2:** The app will parse the page and list all available parts. Choose what you want to download:
   - Type `all` to grab everything.
   - Type `1,2,3` for individual parts.
   - Type `1-5` for a range of parts.
4. **Step 3:** Enter the folder name where you want to save the files (default is the `downloads` folder next to the `.exe`).
5. **Confirm:** Type `y` to confirm and watch your game parts download automatically!

---

## 💻 For Developers (Run from source)

If you want to run the script or build it yourself:

1. Clone this repository:
   ```cmd
   git clone https://github.com/Mohd-Alyan/alyansdownloader.git
   cd FitGirl-Downloader
   ```
2. Install the required dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
   *(Dependencies include `requests` and `rich`)*
3. Run the script:
   ```cmd
   python fitgirl_downloader.py
   ```

### 🔨 Building the `.exe` yourself
To compile the script into a standalone Windows executable:
```cmd
pip install pyinstaller
python -m PyInstaller --onefile fitgirl_downloader.py
```
The generated `.exe` will be located in the `dist` folder.

---

## ⚠️ Disclaimer

This project is intended strictly for educational and research purposes only. It was developed to demonstrate and practice concepts related to scripting, automation, and web data extraction.

I do **not** promote, support, or encourage piracy or the unauthorized distribution of copyrighted content in any form. This tool does not host, distribute, or provide any copyrighted material.

Users are solely responsible for how they choose to use this software. Any misuse of this project, including but not limited to downloading or distributing copyrighted content without proper authorization, is entirely at the user's own risk.

The developer assumes **no responsibility or liability** for any misuse of this project or for any legal consequences that may arise from its use.

By using this project, you agree to comply with all applicable laws and regulations in your jurisdiction.

