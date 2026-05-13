# Dashboard Deployment

Use this guide when you want the dashboard to be visible online through a public URL.

## Recommended Option: Streamlit Community Cloud

GitHub can store the repository, but GitHub Pages cannot run this dashboard because the dashboard is a Python Streamlit app, not a static HTML site. The simplest public deployment is Streamlit Community Cloud.

Official docs:

- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/file-organization
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies

## Deployment Settings

Use these settings in Streamlit Community Cloud:

```text
Repository: whotfisartcode/market_shifts_thesis
Branch: reproducible-deliverables-20260513
Main file path: app/dashboard.py
Python version: 3.12
```

Choose a clear app URL if Streamlit gives you the option, for example:

```text
market-shifts-thesis-dashboard
```

The repository includes `app/requirements.txt` for the deployed dashboard. Streamlit Community Cloud checks the app directory before the repository root, so the online app installs only the packages needed by `app/dashboard.py`.

## Step-By-Step

1. Make sure the GitHub repository is public, or that Streamlit has access to it through your GitHub account.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click `Create app`.
4. Choose `Yup, I have an app`.
5. Fill in the repository, branch, and main file path shown above.
6. Open advanced settings and select Python `3.12`.
7. Leave secrets empty. The dashboard does not need API keys.
8. Click `Deploy`.
9. Wait for the app to build, then copy the generated `streamlit.app` URL.
10. Put that URL in the thesis defense materials and in the GitHub repository description.

## What The Online Dashboard Uses

The deployed app reads the same committed files as a local clone:

```text
data/github/firm_panel_v2.csv.gz
reports/modeling/
reports/target_lab/
reports/target_tweak_experiments/
```

The deployed app does not download raw SEC ZIPs and does not train models. That keeps the public app fast and stable.

## If The Cloud Build Fails

Check these items first:

- The main file path must be `app/dashboard.py`.
- The branch must be `reproducible-deliverables-20260513`.
- Python should be `3.12`.
- The app should use `app/requirements.txt`.
- No secrets are required.

If Streamlit says a file is missing, run this locally:

```bash
python3 scripts/project_audit/github_package_smoke_check.py
```

The expected final line is:

```text
GitHub package smoke check complete; failures=0
```

## What To Send The Committee

Send both links:

```text
GitHub repository:
https://github.com/whotfisartcode/market_shifts_thesis

Online dashboard:
https://<your-chosen-subdomain>.streamlit.app
```

The GitHub repo is the reproducible source package. The Streamlit URL is the public live dashboard.
