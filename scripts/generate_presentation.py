"""Generate a starter PPTX with key charts and summary slides using python-pptx."""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
OUT = REPORTS / "Presentation.pptx"


def add_title_slide(prs, title, subtitle=None):
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = title
    if subtitle:
        slide.placeholders[1].text = subtitle


def add_image_slide(prs, title, image_path: Path):
    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = title
    left = Inches(0.5)
    top = Inches(1.5)
    width = Inches(9)
    slide.shapes.add_picture(str(image_path), left, top, width=width)


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    prs = Presentation()
    add_title_slide(prs, "Bluestock MF Capstone - Starter Presentation", "Auto-generated")
    # Add a few common charts if they exist
    chart_files = [
        "rolling_sharpe_chart.png",
        "reports/01_nav_trend_analysis.png",
        "reports/03_sip_inflow_timeseries.png",
    ]
    for fname in chart_files:
        fpath = ROOT / fname
        if fpath.exists():
            add_image_slide(prs, fpath.stem.replace('_', ' ').title(), fpath)

    prs.save(OUT)
    print("Saved starter presentation:", OUT)


if __name__ == '__main__':
    main()
