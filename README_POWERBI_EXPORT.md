Power BI: theme, logo, and export instructions

Files added here:
- `bluestock_theme.json` — sample Bluestock theme you can import into Power BI Desktop.
- `scripts\validate_csv_schema.py` — validates headers of `data/processed` and writes `data_schema_report.json`.
- `scripts\export_ppt_to_png.ps1` — Windows PowerShell helper to convert an exported PPTX into PNG images (requires PowerPoint installed).

Quick workflow (recommended for local Windows desktop):

1) Apply theme
- In Power BI Desktop: View > Themes > Browse for themes -> select `bluestock_theme.json`.

2) Add logo
- In Power BI Desktop: Insert > Image -> choose your logo file, position on report pages.

3) Export PDF (manual)
- In Power BI Desktop: File > Export > Export to PDF -> save as `Dashboard.pdf`.

4) Export PNGs (per page)
- In Power BI Desktop: File > Export > Export to PowerPoint -> save `dashboard.pptx`.
- On a Windows machine with PowerPoint installed, run the PowerShell script to save slides as PNGs:

```powershell
# from repo root
.
scripts\export_ppt_to_png.ps1 -PptxPath "C:\path\to\dashboard.pptx" -OutDir "C:\path\to\output_pngs"
```

The script will create one subfolder per slide and place PNGs there.

Automated export via Power BI Service (optional)
- If you use Power BI Service and have a Power BI Pro account you can publish the `.pbix` to a workspace and use the Power BI REST API to export to PDF or PNG programmatically. That requires `Connect-PowerBIServiceAccount` and `Invoke-PowerBIRestMethod` calls; tell me if you want a ready-to-run script for that and I'll prepare it.

CSV schema validation
- Run the validator to recreate the header check I ran earlier:

```bash
python scripts/validate_csv_schema.py
```

Outputs: `data_schema_report.json` in `data/`.

Notes & prerequisites
- Power BI Desktop: manual steps require Power BI Desktop installed.
- PowerPoint: the PNG exporter requires Microsoft PowerPoint installed (COM automation).
- Theme/logo: place your official Bluestock logo in the repo (e.g., `assets/logo.png`) and then use Insert > Image.
