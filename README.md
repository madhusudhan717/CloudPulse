# ☁️ CloudPulse – Cloud Monitoring & Automated Alerting

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/HTTP-Requests-green)
![GitHub Actions](https://img.shields.io/badge/Automation-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)
![Status](https://img.shields.io/badge/Project-Completed-success)

**CloudPulse** is a lightweight cloud monitoring and website uptime tracking application developed as part of **CodeNova Internship – Task 4: Cloud Monitoring Project**.

It automatically checks website availability, measures HTTP response latency, tracks uptime percentages, records historical monitoring data, and generates alerts when monitored endpoints become unavailable or exceed configured response-time thresholds.

The project combines a Python monitoring engine, a stylish web dashboard, and scheduled GitHub Actions automation without requiring paid cloud infrastructure.

---

## 🚀 Project Overview

Websites and online services can experience downtime, connection failures, and slow response times. Manually checking every website is inefficient.

CloudPulse solves this problem by automatically monitoring configured website endpoints and displaying their health information through a centralized dashboard.

### Project Objectives

- Perform automated website health checks.
- Track HTTP status codes and response latency.
- Calculate website uptime percentages.
- Detect simulated website downtime.
- Generate alerts when monitoring thresholds are breached.
- Maintain structured historical monitoring logs.
- Automate monitoring using GitHub Actions.

---

## ✨ Key Features

### 1. Automated Website Health Checks
- Sends HTTP GET requests to configured website endpoints.
- Checks website availability.
- Captures HTTP response status codes.
- Handles connection errors and request timeouts.

### 2. Response Time Monitoring
- Measures response latency in milliseconds.
- Calculates average response time.
- Detects slow website responses using a configurable threshold.

### 3. Uptime Tracking
- Calculates availability percentages from historical monitoring records.
- Maintains monitoring history using CSV files.
- Generates structured uptime reports.

### 4. Automated Alerting
- Detects unavailable websites.
- Generates console alerts when an endpoint goes DOWN.
- Generates warnings when response time crosses the configured threshold.
- Supports optional webhook notifications.

### 5. Monitoring Dashboard
- Modern dark-themed monitoring interface.
- Overall uptime statistics.
- Average response time.
- Total health checks.
- Downtime event statistics.
- Response-time analytics.
- Endpoint health distribution.
- Historical monitoring activity.

### 6. GitHub Actions Automation
- Scheduled monitoring every five minutes.
- Manual workflow execution.
- Automated Python dependency installation.
- Monitoring log and report artifact uploads.
- No paid cloud server required.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.11+ | Monitoring engine |
| Requests | HTTP health checks |
| HTML5 | Dashboard structure |
| CSS3 | Dashboard styling |
| JavaScript | Dashboard functionality |
| Chart.js | Monitoring analytics |
| CSV | Historical monitoring logs |
| JSON | Monitoring configuration and dashboard data |
| Git & GitHub | Version control and code hosting |
| GitHub Actions | Scheduled monitoring automation |
| YAML | Workflow configuration |

---

## 🏗️ Project Architecture

```text
                 TARGET WEBSITES
                        |
                        v
              Python Monitoring Engine
                   monitor.py
                        |
                        v
                 Requests Library
                        |
                        v
              Collect Monitoring Data
              /         |          \
             /          |           \
       HTTP Status   Latency       Errors
             \          |           /
              \         |          /
                        v
                  Status Detection
                 /      |       \
                /       |        \
              UP       SLOW      DOWN
                \       |        /
                 \      |       /
                        v
                Alert Generation
                        |
                        v
                Historical Logging
                   /          \
                  /            \
             CSV Logs      JSON Reports
                  \            /
                   \          /
                        v
               CloudPulse Dashboard
                        |
                        v
                 Visual Analytics

             GitHub Actions Automation
                        |
                        v
               Scheduled Monitoring
                 Every 5 Minutes
```

---

## 📁 Project Structure

```text
CloudPulse/
│
├── .github/
│   └── workflows/
│       └── monitoring.yml
│
├── .venv/
│
├── assets/
│   ├── style.css
│   └── dashboard.js
│
├── config/
│   └── config.json
│
├── logs/
│   └── uptime_log.csv
│
├── reports/
│   ├── dashboard-data.json
│   └── uptime_report.txt
│
├── index.html
├── monitor.py
├── requirements.txt
├── README.md
└── .gitignore
```

**Note:** The `.venv` directory is created locally and excluded from GitHub using `.gitignore`.

---

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.11 or later
- Visual Studio Code
- Git
- Internet connection

### Step 1: Clone the Repository

```bash
git clone https://github.com/madhusudhan717/CloudPulse.git
```

Navigate into the project:

```bash
cd CloudPulse
```

### Step 2: Create a Virtual Environment

On Windows PowerShell:

```powershell
py -3.11 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If Python launcher configuration causes problems, use the direct Python 3.11 executable path:

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe" -m venv .venv
```

### Step 3: Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Run Website Monitoring

Execute the monitoring engine:

```bash
python monitor.py
```

The script checks all configured websites and generates:

- `logs/uptime_log.csv`
- `reports/dashboard-data.json`
- `reports/uptime_report.txt`

### Step 5: Launch the Dashboard

Open another terminal in the project directory.

Run:

```bash
python -m http.server 8000
```

Open your browser:

```text
http://localhost:8000
```

Click **Refresh Data** to load the latest monitoring results.

---

## 🔧 Configuration

Monitoring endpoints and alert thresholds are configured in:

`config/config.json`

Example:

```json
{
  "request_timeout_seconds": 10,
  "latency_threshold_ms": 2000,
  "targets": [
    {
      "name": "Google",
      "url": "https://www.google.com"
    },
    {
      "name": "GitHub",
      "url": "https://github.com"
    },
    {
      "name": "Python.org",
      "url": "https://www.python.org"
    },
    {
      "name": "Cloudflare",
      "url": "https://www.cloudflare.com"
    }
  ]
}
```

### Configuration Parameters

| Parameter | Description |
|---|---|
| request_timeout_seconds | Maximum time to wait for a website response |
| latency_threshold_ms | Maximum acceptable response time |
| targets | List of websites to monitor |

### Monitoring Status Logic

| Status | Meaning |
|---|---|
| UP | Website successfully responds |
| SLOW | Website responds but exceeds latency threshold |
| DOWN | Website is unavailable or returns an unsuccessful HTTP status |

A SLOW website is considered reachable when calculating uptime.

---

## 🚨 Alerting System

CloudPulse generates alerts whenever:

1. A website cannot be reached.
2. A connection error occurs.
3. A request times out.
4. Response time exceeds the configured threshold.

Example console alert:

```text
[DOWN] Test Server HTTP N/A

[ALERT] CloudPulse alert:
Test Server is DOWN

HTTP N/A
ConnectionError
```

### Optional Webhook Notifications

CloudPulse supports optional webhook notifications using the environment variable:

`ALERT_WEBHOOK_URL`

PowerShell example:

```powershell
$env:ALERT_WEBHOOK_URL="YOUR_WEBHOOK_URL"

python monitor.py
```

Do not commit webhook URLs or credentials to GitHub.

---

## 📊 Sample Monitoring Results

The following are actual results from one of the local monitoring runs during project testing.

| Website | HTTP Status | Response Time | Result |
|---|---:|---:|---|
| Google | 200 | 686.31 ms | UP |
| GitHub | 200 | 742.55 ms | UP |
| Python.org | 200 | 367.77 ms | UP |
| Cloudflare | 200 | 1142.28 ms | UP |

### Simulated Downtime Testing

To validate failure detection, a temporary local endpoint was added:

```json
{
  "name": "Test Server",
  "url": "http://127.0.0.1:9"
}
```

The monitoring engine successfully detected the unavailable endpoint.

```text
[UP  ] Google
[UP  ] GitHub
[UP  ] Python.org
[UP  ] Cloudflare
[DOWN] Test Server

[ALERT] CloudPulse alert:
Test Server is DOWN
```

The dashboard displayed the service interruption and updated the uptime statistics.

During this test:

- Total recorded checks: 9
- Successful checks: 8
- Failed checks: 1
- Recorded uptime: 88.89%
- Downtime events: 1

The temporary test endpoint was removed after testing.

---

## ⏱️ GitHub Actions Automation

CloudPulse uses GitHub Actions to execute automated monitoring without requiring a continuously running local computer.

Workflow location:

`.github/workflows/monitoring.yml`

### Automation Schedule

```yaml
on:
  schedule:
    - cron: "*/5 * * * *"

  workflow_dispatch:
```

This configuration enables:

- Scheduled monitoring approximately every five minutes.
- Manual workflow execution.
- Automatic Python environment setup.
- Dependency installation.
- Website health checks.
- Monitoring log and report artifact uploads.

### How to Execute the Workflow

1. Open the GitHub repository.
2. Navigate to the Actions tab.
3. Select CloudPulse Scheduled Monitoring.
4. Click Run workflow.
5. Select the main branch.
6. Start the workflow.

GitHub Actions executes the monitoring script on a hosted runner.

### Successful Workflow Verification

The updated workflow was manually executed successfully.

| Metric | Result |
|---|---|
| Workflow | CloudPulse Scheduled Monitoring |
| Branch | main |
| Execution status | Success |
| Monitoring job | Passed |
| Latest successful run duration | 18 seconds |
| Artifacts | 1 uploaded |

The workflow uploads generated monitoring records and reports as downloadable artifacts.

**Important:** GitHub Actions executes independently of the locally hosted dashboard. Its artifacts can be downloaded from the corresponding workflow run; they are not automatically synchronized to the local dashboard.

---

## 📸 Project Screenshots

Add your actual project screenshots in a `screenshots/` directory and use the following references.

```text
screenshots/
├── dashboard-overview.png
├── monitored-endpoints.png
├── downtime-detection.png
└── github-actions-success.png
```

### Dashboard Overview

![CloudPulse Dashboard](screenshots/dashboard-overview.png)

### Simulated Downtime Detection

![Downtime Detection](screenshots/downtime-detection.png)

### GitHub Actions Successful Execution

![GitHub Actions Success](screenshots/github-actions-success.png)

---

## ✅ Project Acceptance Checklist

| Requirement | Status |
|---|---|
| Automated website health checks | Completed |
| HTTP status code tracking | Completed |
| Response latency measurement | Completed |
| Uptime percentage calculation | Completed |
| Automated alert generation | Completed |
| Simulated downtime detection | Tested successfully |
| Historical uptime logs | Implemented |
| Monitoring dashboard | Implemented |
| Scheduled GitHub Actions workflow | Configured |
| Manual workflow execution | Successful |
| Monitoring artifacts | Uploaded |

---

## 🔮 Future Enhancements

- Email and messaging notifications.
- More detailed historical performance analytics.
- Additional monitoring endpoints.
- Incident history and reporting.
- Database-backed monitoring history.
- Multi-user monitoring management.

---
## Output 
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/a4ddecfd-e69b-4561-9da1-323412dbafd3" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/db1cef5d-ccf0-4c1c-93f3-54a5da9fd0e9" />




## 🎯 Conclusion

CloudPulse demonstrates a practical implementation of website health monitoring, response-time measurement, uptime tracking, automated alerting, and scheduled execution using GitHub Actions.

The project combines Python-based monitoring with an interactive dashboard to provide visibility into website availability and performance.

It demonstrates practical experience with Python scripting, HTTP requests, web technologies, monitoring concepts, GitHub version control, and CI/CD automation.

**Developed as part of CodeNova Internship – Task 4: Cloud Monitoring Project.**

---

## 🔗 Project Links

**GitHub Repository:**  
https://github.com/madhusudhan717/CloudPulse

**Project:** CloudPulse – Cloud Monitoring Platform

**Developer:** Madhusudhan

**Internship:** CodeNova – Task 4
