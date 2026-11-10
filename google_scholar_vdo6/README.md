# Google Scholar — Phuc Do (automatic updates)

Scholar profile: https://scholar.google.com/citations?user=Xa97hl4AAAAJ&hl=en

## Files
- `index.html`: dark theme, red bars, automatic chart rendering from JSON
- `update_scholar.py`: retrieves citations, h-index, i10-index, annual citations
- `.github/workflows/update-scholar.yml`: weekly scheduled updater + manual launch
- `scholar_data.json`: snapshot; intentionally blank until first successful run

## Install (GitHub Pages)
1. Log into GitHub as `vdo6`, create a public repository named `google-scholar-widget`, and upload the **contents** of this extracted folder to the repository root (including the hidden `.github/workflows/` directory). Do not upload the ZIP as a single file.
2. Under **Settings → Pages**, select **Source: GitHub Actions**. Under **Settings → Actions → General**, allow GitHub Actions and read/write workflow permissions where necessary (the workflow requests `contents: write`).
3. Under **Actions → Update Google Scholar statistics**, select **Run workflow** once. Check the run succeeded and `scholar_data.json` has numeric values.
4. Once the workflow finishes successfully, check the deployed page in **Settings → Pages**. The scheduled workflow updates the JSON and deploys the page.
5. Open `https://vdo6.github.io/google-scholar-widget/`.
6. To embed in an institutional page, ask your CMS administrator to permit an iframe for this hosted page. If iframes are forbidden, provide a regular link to the hosted page, or have IT host `index.html` and `scholar_data.json` together on the institutional site.

Data refreshes every Monday at 07:23 UTC if Google Scholar permits access. If Google Scholar blocks automated retrieval, the Action fails and the last valid JSON remains in place. GitHub may disable scheduled workflows in inactive public repos after 60 days; reactivate as needed. Initial display shows placeholders until successful update.

IMPORTANT: Google Scholar has no official public API for this. `scholarly` is unofficial and may be blocked by CAPTCHAs or rate limits. It is not possible to guarantee updates. The public repo discloses only public citation data; do not put credentials into it.

For a private host, run `pip install -r requirements.txt && python update_scholar.py` via a weekly scheduler and serve both HTML and JSON from the same directory.
