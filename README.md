🛰️ Monitor Global Cloud Status Notifier

Monitor Global Cloud Status Notifier is an automated tool developed in Python that monitors the status of major cloud services (such as AWS, Azure, Microsoft 365, Google Cloud, and Google Workspace) and notifies any changes or interruptions in real time via Telegram.

The system periodically checks the official status pages, detects incidents, degradations, or outages, and sends customized alerts with local time (Colombia) to the configured chat. In addition, it is deployed on Render, which allows the monitor to remain active 24/7 without the need for local servers.

🚀 Main features

✅ Automatic monitoring of the most widely used cloud services.

🔔 Instant notifications via Telegram Bot.

🌎 Automatic conversion of time to Colombia time zone (America/Bogota).

💾 Historical log of detected statuses.

☁️ Deployment on Render with Flask support to keep the service online.

🛠️ Technologies used

Python 3.13

Flask (for web service)

Requests and HTTPAdapter (for secure queries)

dotenv (environment variable management)

pytz (time zone adjustment)

Render (deployment platform)

📩 Example notification 🚨 Change detected in AWS Previous: ✅ Operational Current: ⚠️ Problems detected 🕒 2025-10-29 18:30:42 (Colombia time) 🔗 See more: https://status.aws.amazon.com/
