"""Streamlit web interface for the Data Quality Analyzer."""

import argparse
import io
import tempfile
import zipfile
from pathlib import Path
from typing import List, Protocol, Tuple, TypedDict

import streamlit as st

import data_quality_analyzer as analyzer


MAX_UPLOAD_MB = 50
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1_048_576


class UploadedFile(Protocol):
    name: str
    size: int

    def getvalue(self) -> bytes: ...


class Analysis(TypedDict):
    results: List[analyzer.SheetResult]
    reports: List[Tuple[str, bytes]]


def analyze_upload(
    uploaded_file: UploadedFile, language: str, minimal: bool
) -> Analysis:
    """Analyze one uploaded file and return report bytes and summary metrics."""
    extension = Path(uploaded_file.name).suffix.lower()
    if extension not in analyzer.ALL_EXTENSIONS:
        raise ValueError("Upload a CSV, XLSX, XLS, or ODS file.")
    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise ValueError(f"Files must be {MAX_UPLOAD_MB} MB or smaller.")

    safe_name = Path(uploaded_file.name.replace("\\", "/")).name
    with tempfile.TemporaryDirectory(prefix="data-quality-") as temp_dir:
        temp_path = Path(temp_dir)
        input_path = temp_path / safe_name
        reports_dir = temp_path / "reports"
        reports_dir.mkdir()
        input_path.write_bytes(uploaded_file.getvalue())

        args = argparse.Namespace(
            max_size=MAX_UPLOAD_BYTES,
            sep=None,
            encoding=None,
            sample=None,
            minimal=minimal,
            lang=language,
        )
        translations_loaded = (
            analyzer.load_translations() if language == "es" else False
        )

        if extension in analyzer.CSV_EXTENSIONS:
            results = analyzer.process_csv_file(
                input_path, args, translations_loaded, reports_dir
            )
        else:
            results = analyzer.process_excel_file(
                input_path, args, translations_loaded, reports_dir
            )

        generated_reports: List[Tuple[str, bytes]] = [
            (report, (reports_dir / report).read_bytes())
            for result in results
            for report in result.reports
        ]
        return {
            "results": results,
            "reports": generated_reports,
        }


def build_report_archive(reports: List[Tuple[str, bytes]]) -> bytes:
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zipped:
        for filename, content in reports:
            zipped.writestr(filename, content)
    return archive.getvalue()


def main() -> None:
    st.set_page_config(page_title="Data Quality Analyzer", page_icon="📊")
    st.title("📊 Data Quality Analyzer")
    st.write(
        "Upload a CSV or Excel file to generate a downloadable data quality report."
    )
    st.warning(
        "Your upload is processed by the computer running this app. If you opened "
        "a hosted version, that is the hosting server. Files may remain in the "
        "active app session's memory until it ends. Only upload data you are "
        "authorized to process."
    )

    uploaded_file = st.file_uploader(
        f"Choose a file (up to {MAX_UPLOAD_MB} MB)",
        type=["csv", "xlsx", "xls", "ods"],
    )
    language = st.selectbox(
        "Report language",
        options=["es", "en"],
        format_func=lambda value: "Spanish" if value == "es" else "English",
    )
    minimal = st.checkbox(
        "Fast analysis",
        help="Skip correlation and interaction analysis to reduce processing time.",
    )

    if uploaded_file is None:
        st.session_state.pop("analysis", None)
        st.session_state.pop("analysis_key", None)
        return

    analysis_key = (uploaded_file.name, uploaded_file.size, language, minimal)
    if st.session_state.get("analysis_key") != analysis_key:
        st.session_state.pop("analysis", None)

    if st.button("Analyze file", type="primary"):
        with st.spinner("Analyzing your file and creating the report..."):
            try:
                st.session_state["analysis"] = analyze_upload(
                    uploaded_file, language, minimal
                )
                st.session_state["analysis_key"] = analysis_key
            except (OSError, ValueError) as error:
                st.error(str(error))
                st.session_state.pop("analysis", None)
                st.session_state.pop("analysis_key", None)

    analysis = st.session_state.get("analysis")
    if not analysis:
        return

    rows = []
    for result in analysis["results"]:
        if result.ok:
            rows.append(
                {
                    "File / sheet": result.display_name,
                    "Rows": result.rows,
                    "Columns": result.columns,
                    "Missing values (%)": result.missing_pct,
                    "Duplicate rows": result.duplicates,
                    "Analysis mode": result.analysis_mode,
                }
            )
        else:
            st.error(f"{result.display_name}: {result.error or 'Analysis failed.'}")

    if rows:
        st.subheader("Analysis summary")
        st.dataframe(rows, hide_index=True, use_container_width=True)

    reports = analysis["reports"]
    if reports:
        st.subheader("Download reports")
        st.download_button(
            "Download all reports (.zip)",
            data=build_report_archive(reports),
            file_name="data_quality_reports.zip",
            mime="application/zip",
        )
        for filename, content in reports:
            st.download_button(
                f"Download {filename}",
                data=content,
                file_name=filename,
                mime="text/html",
                key=f"download-{filename}",
            )
    elif not rows:
        st.error("No reports were generated. Check that the file has readable data.")


if __name__ == "__main__":
    main()
