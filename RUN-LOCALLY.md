# Run Data Quality Analyzer on Your Computer

This guide is for anyone who wants to run the upload website on their own
Windows, macOS, or Linux computer. You do not need VS Code or a hosting account.

## 1. Install Python

Install **Python 3.11** from [python.org/downloads](https://www.python.org/downloads/).
On Windows, select **Add Python to PATH** in the installer.

## 2. Download the project

On the project's GitHub page, choose **Code → Download ZIP**, then extract the
ZIP file. Alternatively, if you have Git installed, run:

```text
git clone https://github.com/joseluisbn/Data-Quality-Analyzer.git
```

```
  git clone https://github.com/joseluisbn/Data-Quality-Analyzer.git
cd Data-Quality-Analyzer
code . -r

````

Open a terminal in the extracted `Data-Quality-Analyzer` folder. On Windows,
open that folder in File Explorer, type `powershell` in the address bar, and
press Enter.

## 3. Install the app

Run the commands for your operating system from the project folder.

### Windows (PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### macOS or Linux

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

Installing the dependencies can take a few minutes.

## 4. Start the website

### Windows (PowerShell)

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### macOS or Linux

```bash
.venv/bin/python -m streamlit run app.py
```

When the app starts, open **http://localhost:8501** in your browser. Choose a
CSV, XLSX, XLS, or ODS file, select the report language, and click **Analyze
file**. Download an individual HTML report or all reports as a ZIP.

To stop the app, return to the terminal and press **Ctrl+C**.

## Privacy

When run this way, the app processes your upload on the computer running it; the
file is not sent to Streamlit Community Cloud. The uploaded file and reports may
stay in the active app session's memory until that session ends. Only upload
files you are authorized to analyze.

## Troubleshooting

- **`py` or `python3.11` not found:** Install Python 3.11, close and reopen the
  terminal, and try again.
- **The browser cannot connect:** Check that Streamlit is still running in the
  terminal and open `http://localhost:8501` on the same computer.
- **Port 8501 is already in use:** Stop the other Streamlit app, or run
  `.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502`
  on Windows, or `.venv/bin/python -m streamlit run app.py --server.port 8502`
  on macOS/Linux. Then open `http://localhost:8502`.
- **Upload is too large:** The maximum upload size is 50 MB.
