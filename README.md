# Neo Portfolio

[www.phlpneo.com](https://www.phlpneo.com) is my personal portfolio and notes website. It presents my software, backend, cloud and data projects, provides longer-form technical writing, and gives visitors a protected contact form.

The site is built with Django and is deployed on an Oracle Cloud virtual machine behind Nginx and Gunicorn.

## Features

- Project portfolio with descriptions, technologies, repository links, demos, thumbnails and optional PDF reports
- Up to three featured projects on the home page
- Project pagination with six projects per page
- Technical notes written in Markdown
- Multiple image and animated GIF attachments for each note
- Privacy-enhanced YouTube embeds using `youtube-nocookie.com`
- Note pagination with nine posts per page
- Contact form with database storage and Resend email notifications
- Cloudflare Turnstile human verification and per-IP submission throttling
- Django administration for projects, notes, attachments and contact messages
- Automatic cleanup of replaced or deleted media files
- Canonical URLs, Open Graph metadata, structured data, `robots.txt` and XML sitemaps
- Dedicated acknowledgements page linked from the copyright notice
- Automated SQLite and media backups to Oracle Cloud Object Storage

## Technology stack

- Python 3.12+
- Django 6
- SQLite
- Bootstrap 5 and custom CSS
- Markdown, nh3 and Pillow
- Resend through Django Anymail
- Cloudflare Turnstile
- Gunicorn and Nginx
- Oracle Cloud Infrastructure (OCI)

## Project structure

```text
personal-website/
├── config/             Django configuration and root URL routing
├── core/               Home, About, Special Thanks, SEO and pagination
├── projects/           Portfolio project models, pages and administration
├── notes/              Markdown notes, attachments and media cleanup
├── contact/            Contact form, Turnstile, throttling and email delivery
├── templates/          Shared and app-specific Django templates
├── static/             Source CSS and images
├── scripts/backup.sh   Local and OCI Object Storage backup script
├── .env.example        Environment variable template
├── manage.py
└── requirements.txt
```

## Local development

### 1. Clone the repository

```bash
git clone https://github.com/PHLP-Neo/personal-website.git
cd personal-website
```

### 2. Create and activate a virtual environment

Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure the environment

Copy `.env.example` to `.env` and replace the example values where required.

Linux or macOS:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Generate a Django secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

For ordinary local development, the console email backend is sufficient. Contact notification emails will be printed in the terminal instead of being sent.

### 5. Prepare the database

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The administration area is available at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

## Environment variables

| Variable | Purpose | Typical local value |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Django cryptographic secret | A newly generated private value |
| `DJANGO_DEBUG` | Enables development error pages | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated permitted hosts | `localhost,127.0.0.1` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins | `http://localhost:8000,http://127.0.0.1:8000` |
| `DJANGO_SECURE_SSL_REDIRECT` | Redirects HTTP to HTTPS in production | `False` locally, `True` in production |
| `SITE_URL` | Canonical public origin used by SEO and pagination | `https://www.phlpneo.com` |
| `DJANGO_EMAIL_BACKEND` | Django email provider | Console backend locally; Anymail in production |
| `RESEND_API_KEY` | Private Resend API key | Empty locally |
| `DEFAULT_FROM_EMAIL` | Verified sender address | `Neo Portfolio <website@send.phlpneo.com>` |
| `CONTACT_NOTIFICATION_EMAIL` | Address that receives contact notifications | Empty locally |
| `CONTACT_RATE_LIMIT` | Allowed contact attempts per client and window | `5` |
| `CONTACT_RATE_LIMIT_WINDOW` | Rate-limit window in seconds | `3600` |
| `TURNSTILE_SITE_KEY` | Public Cloudflare Turnstile site key | Cloudflare-provided value |
| `TURNSTILE_SECRET_KEY` | Private Turnstile verification key | Empty locally |
| `TURNSTILE_EXPECTED_HOSTNAME` | Hostname accepted in verification results | `www.phlpneo.com` |

Never commit `.env`, Django secret keys, Resend API keys or Turnstile secret keys.

For production email delivery, use:

```dotenv
DJANGO_EMAIL_BACKEND=anymail.backends.resend.EmailBackend
```

## Managing content

### Projects

Projects are created and edited in Django Admin. Each project can contain:

- A title, URL slug and short summary
- A full description and personal role
- Comma-separated technologies
- A thumbnail
- Repository, live-site and recorded-demo links
- An optional PDF report of up to 50 MB
- Status, display order and approximate completion date
- A featured flag

The home page intentionally displays only the first three featured projects according to project ordering. The Projects page displays all projects.

Because the application accepts reports up to 50 MB, the production reverse proxy must allow a larger total request. For Nginx, `client_max_body_size 60M;` leaves room for the PDF and the rest of the form.

### Notes

Notes are created in Django Admin and remain private until `Published` is selected. The body supports:

- Headings, paragraphs and emphasis
- Ordered and unordered lists
- Links and block quotes
- Fenced code blocks
- Tables
- Uploaded PNG, JPEG, WebP and animated GIF images
- YouTube videos

Images can be added through the attachment rows beneath a note. Save and reopen the note to obtain each attachment's generated Markdown reference, then paste that reference into the note body.

Embed a supported YouTube URL on its own line:

```markdown
[[youtube:https://www.youtube.com/watch?v=VIDEO_ID]]
```

Raw HTML is escaped and rendered Markdown is sanitised before display. Deleting a note, project or attachment also removes its associated local media when that file is no longer referenced.

### Contact messages

Valid submissions are saved before the notification email is attempted. If email delivery fails, the message remains available in Django Admin along with the most recent delivery error. Administrators can mark messages as read, unread or archived.

## Tests and checks

Run the automated test suite:

```bash
python manage.py test
```

Run Django's configuration check:

```bash
python manage.py check
```

Before a production deployment, also run:

```bash
python manage.py check --deploy
```

The deployment check must use production environment variables; otherwise it will correctly warn about local debug and HTTPS settings.

## Production deployment

The current production layout uses:

- Application directory: `/srv/neo-portfolio`
- Gunicorn systemd service: `neo-portfolio.service`
- Nginx for HTTPS, static files, media files and Gunicorn proxying
- `www.phlpneo.com` as the canonical hostname

A routine deployment is:

```bash
cd /srv/neo-portfolio
git pull --ff-only origin main

./.venv/bin/python manage.py migrate
./.venv/bin/python manage.py collectstatic --noinput
./.venv/bin/python manage.py check

sudo systemctl restart neo-portfolio.service
sudo systemctl status neo-portfolio.service --no-pager
```

After deployment, verify the application and canonical redirect:

```bash
curl -I https://www.phlpneo.com/
curl -I https://phlpneo.com/
curl -fsS https://www.phlpneo.com/health/
```

The bare domain should redirect permanently to `https://www.phlpneo.com/`, and the health endpoint should return `{"status": "ok"}`.

## Backups

`scripts/backup.sh` creates a consistent SQLite backup, copies uploaded media, writes backup metadata, creates a SHA-256 checksum and uploads both files to OCI Object Storage using instance-principal authentication.

Its defaults are:

- Local directory: `/srv/backups/neo-portfolio`
- OCI bucket: `neo-portfolio-backups`
- Object prefix: `daily/`
- Local retention: 14 days

The production systemd timer runs the backup service daily. Check it with:

```bash
systemctl status neo-portfolio-backup.timer --no-pager
systemctl list-timers neo-portfolio-backup.timer --no-pager
```

A backup is only proven useful after a restore test. Periodically download an archive and checksum from Object Storage, verify it with `sha256sum -c`, extract it, run SQLite's `PRAGMA integrity_check`, and confirm the media files are present.

## Security notes

- Production runs with `DJANGO_DEBUG=False` and HTTPS-only cookies.
- Nginx redirects the bare domain and HTTP traffic to the canonical HTTPS URL.
- Cloudflare Turnstile is validated by the Django server, not only in the browser.
- Contact submissions are rate-limited in addition to Turnstile verification.
- Uploaded project reports are restricted to PDF files and 50 MB.
- Note Markdown is sanitised and arbitrary HTML or iframe injection is blocked.
- Administrative content management requires Django authentication.
- Secrets belong only in the untracked `.env` file or another secure secret store.

## Acknowledgements

See the website's [Special Thanks](https://www.phlpneo.com/special-thanks/) page for the people and organisations who supported this project and my development journey.
