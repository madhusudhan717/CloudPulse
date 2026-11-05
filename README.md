# CloudPulse – Cloud Monitoring Project (CodeNova Task 4)

CloudPulse is a lightweight website health-monitoring project. A Python script checks configured HTTP/HTTPS endpoints, records response latency and HTTP status codes, calculates historical availability, and raises alerts when an endpoint is unavailable or slower than the configured threshold. A responsive HTML/CSS/JavaScript dashboard displays the generated monitoring report.

## Technologies used

| Technology | Purpose |
|---|---|
| Python 3 | Monitoring engine and report generation |
| Requests | HTTP health checks and optional webhook delivery |
| GitHub Actions | Scheduled monitoring using a cron workflow |
| CSV and JSON | Historical records and dashboard data |
| HTML, CSS, JavaScript | Lightweight reporting dashboard |

The dashboard uses browser-native JavaScript and Canvas drawing; no frontend framework or chart package is required. The local preview server uses Python's built-in HTTP server.

## Features

- Configurable list of website endpoints.
- HTTP status code and response latency measured in milliseconds.
- UP, DOWN, and SLOW status classification.
- Request timeout and configurable latency threshold.
- CSV history and a generated uptime summary report.
- Overall and per-endpoint uptime calculations.
- Console alerts and optional webhook notifications.
- Responsive dashboard with metric cards, charts, endpoint table, and activity feed.
- GitHub Actions schedule every five minutes, manual workflow trigger, repository history update, and downloadable workflow artifacts.

## Project structure

```text
CloudPulse-Task4/
├── monitor.py
├── config/
│   └── config.json
├── requirements.txt
├── index.html
├── assets/
│   ├── style.css
│   └── dashboard.js
├── logs/
│   └── uptime_log.csv
├── reports/
│   ├── dashboard-data.json
│   └── uptime_report.txt
├── .github/
│   └── workflows/
│       └── monitoring.yml
├── .gitignore
└── README.md
```

## Run locally in VS Code (Windows)

1. Extract the ZIP file.
2. Open the extracted `CloudPulse-Task4` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell prevents environment activation, use the environment's Python executable directly in the commands below.

5. Install the only third-party Python dependency:

   ```powershell
   python -m pip install -r requirements.txt
   ```

6. Run a monitoring cycle:

   ```powershell
   python monitor.py
   ```

7. Start the dashboard's local static preview server in a second terminal:

   ```powershell
   python -m http.server 8000
   ```

8. Open `http://localhost:8000` in your browser. After each monitoring cycle, click **Refresh data** in the dashboard.

The local preview server is provided by Python's standard library. It is not a paid or hosted server.

## Configure endpoints and thresholds

Edit `config/config.json`:

```json
{
  "request_timeout_seconds": 10,
  "latency_threshold_ms": 2000,
  "targets": [
    {"name": "My Website", "url": "https://example.com"}
  ]
}
```

- `request_timeout_seconds`: maximum wait for a response.
- `latency_threshold_ms`: a successful response slower than this is classified as `SLOW`.
- `targets`: endpoints that you are authorized to monitor.

Classification: final HTTP responses from 200 through 399 are reachable. A response above the latency threshold is `SLOW`; HTTP 400 or higher and request/network/timeout failures are `DOWN`. `SLOW` is counted as reachable when calculating uptime.

## Alerts

Every `DOWN` or `SLOW` result creates a console alert. To send an additional generic JSON webhook notification, set the `ALERT_WEBHOOK_URL` environment variable.

PowerShell example:

```powershell
$env:ALERT_WEBHOOK_URL="YOUR_WEBHOOK_ENDPOINT"
python monitor.py
```

For GitHub Actions, add a repository secret named `ALERT_WEBHOOK_URL` under **Settings → Secrets and variables → Actions**. Do not put webhook URLs or credentials in source files or commit them to Git.

## Automated monitoring with GitHub Actions

The workflow is `.github/workflows/monitoring.yml`.

1. Create a GitHub repository and push this project to its default branch.
2. In the repository, open **Settings → Actions → General**.
3. Under Workflow permissions, allow read and write permissions if the repository's organization policy permits it. The workflow also requests `contents: write` in YAML so it can save CSV/report history.
4. Open the **Actions** tab.
5. Select **CloudPulse Scheduled Monitoring** and use **Run workflow** to test it manually.
6. The scheduled workflow uses `*/5 * * * *` and checks endpoints approximately every five minutes. GitHub may delay scheduled runs during busy periods.
7. Each run saves the updated CSV and reports back to the repository and uploads an artifact. Open a workflow run to download its artifact.

The Actions runner is temporary and separate from your local machine. Committing the log/report files is what preserves scheduled history in the repository. Scheduled workflows must be enabled, and GitHub can automatically disable schedules in some inactive repositories. Keep the repository active and check the Actions tab for run results.

## Simulate downtime safely

Do not take down a real third-party website. Instead, temporarily add an unreachable local test endpoint to `config/config.json`, for example:

```json
{"name": "Local Failure Test", "url": "http://127.0.0.1:9"}
```

Run `python monitor.py`. The request should fail and be recorded as `DOWN`, with a console alert. Remove the test endpoint after verification. The local failure URL is intended only for a local test, not for the scheduled GitHub workflow.

## Uptime calculation

Per-endpoint uptime is:

`(UP checks + SLOW checks) / total checks × 100`

Overall uptime uses all endpoint check records. This is a project-level measurement based on recorded checks, not a third-party certified SLA. With no historical checks, the dashboard shows no measured uptime rather than claiming 100%.

## Evidence for submission

Capture screenshots of:

1. The dashboard after successful endpoint checks.
2. The endpoint table showing HTTP codes and latency in milliseconds.
3. The console alert and dashboard DOWN state from the safe local failure test.
4. `logs/uptime_log.csv` containing multiple monitoring cycles.
5. A successful GitHub Actions workflow run and its uploaded artifact.
6. The `README.md` configuration and alert threshold sections.

## Troubleshooting

- **`ModuleNotFoundError: requests`:** run `python -m pip install -r requirements.txt` in the active environment.
- **Dashboard says no report data:** run `python monitor.py` first, then refresh the dashboard. Use `python -m http.server 8000` rather than opening the HTML file directly.
- **GitHub Actions cannot push:** check repository workflow permissions and any organization policy restricting `GITHUB_TOKEN` write access.
- **Webhook fails:** check the secret name and webhook endpoint; the monitor still records the health check even when webhook delivery fails.

## Task 4 acceptance checklist

- [ ] Health checks run against configured endpoints.
- [ ] Response latency is recorded in milliseconds.
- [ ] HTTP status codes and UP/DOWN/SLOW states are recorded.
- [ ] Uptime is calculated from historical checks.
- [ ] DOWN and threshold-breach alerts are generated.
- [ ] CSV uptime logs contain multiple monitoring cycles.
- [ ] GitHub Actions scheduled and manual workflows execute.
- [ ] README includes alert threshold configuration and evidence screenshots.
