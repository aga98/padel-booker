# my-booker-buddy

Automated Selenium bot that books padel courts on [Padel7](https://padel7santmarti.com) (Barcelona). Supports multiple venues, court type preferences with automatic fallback, account balance tracking, dry-run mode, scheduled execution, and Telegram notifications.

## Supported Venues

| Key        | Location                  |
|------------|---------------------------|
| `poblenou` | Padel7 Poblenou (default) |
| `glories`  | Padel7 Glòries            |

## Project Structure

```text
my-booker-buddy/
├── README.md                  # Project documentation
├── Taskfile.yml               # Task runner shortcuts for local and Docker workflows
├── .github/
│   └── workflows/             # Scheduled GitHub Actions for group reminders & polls
└── padel7_booking_bot/
    ├── pyproject.toml         # Project metadata and dependencies (managed with uv)
    ├── uv.lock                # Locked dependency versions
    ├── Dockerfile             # Container definition with headless Chrome
    ├── .env                   # Local credentials and Telegram settings (git-ignored)
    ├── main.py                # CLI entry point and workflow orchestration
    ├── config/
    │   └── settings.py        # Venue URLs, element IDs, court mappings, and timeouts
    ├── bot/
    │   ├── login.py           # Cookie handling and member portal authentication
    │   ├── booking.py         # Date navigation, slot lookup, checkout, and remaining balance extraction
    │   ├── balance.py         # Dashboard credit reader and Euro amount parser
    │   ├── notifications.py   # Telegram notifications for bookings and wallet balance summaries
    │   ├── utils.py           # Chrome driver setup, court selection, logging, screenshots
    │   └── types.py           # TypedDict definitions for booking state and preferences
    ├── logs/                  # Execution logs (bot.log)
    ├── screenshots/           # Final-state screenshots saved after each run
    └── tests/                 # Unit and integration test suites
```

## Setup

**Requirements:** Python 3.12+, [uv](https://github.com/astral-sh/uv), [Task](https://taskfile.dev) (recommended)

From the repository root:

```bash
task setup
```

*(Without `task`, run `cd padel7_booking_bot && mkdir -p screenshots logs && uv sync`.)*

Create a `.env` file inside `padel7_booking_bot/`:

```env
APP_USERNAME=your@email.com
APP_PASSWORD=yourpassword
APP_TELEGRAM_BOT_TOKEN=123456:ABC-DEF...   # optional
APP_TELEGRAM_PROD_CHAT_ID=-100...   # optional (used when --no-dry-run is passed)
APP_TELEGRAM_TEST_CHAT_ID=-100...   # optional (used when --dry-run is active)
```

## Usage

Run tasks from the repository root (pass any CLI flags after `--`), or invoke `uv run python main.py` directly inside `padel7_booking_bot/`:

```bash
task dry-run -- [OPTIONS]
task run -- [OPTIONS]
```

| Flag                         | Default          | Description                                                                                                                                     |
|------------------------------|------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| `--dry-run` / `--no-dry-run` | `--dry-run`      | Simulate without spending balance (also routes Telegram alerts to `APP_TELEGRAM_TEST_CHAT_ID`). `task run` passes `--no-dry-run` automatically. |
| `--date YYYY-MM-DD`          | 10 days from now | Target booking date                                                                                                                             |
| `--time HH:MM`               | `18:00-19:30`    | Time slot to book                                                                                                                               |
| `--court-type`               | `both`           | `indoor`, `outdoor`, or `both` (falls back to any available court if preferred type is full)                                                    |
| `--centre`                   | `poblenou`       | `poblenou` or `glories`                                                                                                                         |
| `--wait-until HH:MM:SS`      | —                | Wait until this exact time (`Europe/Madrid`) before running — useful for midnight booking drops                                                 |
| `--check-balance`            | off              | Check current account credit (`saldo`) and send a Telegram affordability summary without booking                                                |
| `--notifications`            | off              | Send Telegram notification on booking result or balance check                                                                                   |
| `--verbose`                  | off              | Enable debug logging                                                                                                                            |

### Examples

```bash
# Dry run (safe default) — test the booking flow without paying
task dry-run --date 2026-08-17 --time 18:00

# Real booking at Poblenou
task run --date 2026-08-17 --time 18:00 --centre poblenou

# Wait until midnight then book immediately when new slots open
task run --wait-until 00:00:00 --date 2026-08-18 --time 10:00

# Book an indoor court at Glòries with Telegram notifications enabled
task run --date 2026-08-17 --time 18:00 --centre glories --court-type indoor --notifications

# Check current wallet balance and notify the test chat
uv run python main.py --check-balance --notifications
```

## Docker

Build the container image:

```bash
task docker:build
```

Run a dry-run test, balance check, or live booking in Docker (automatically loads `.env` and mounts `screenshots/` and `logs/` to your host):

```bash
# Dry run with debug logging
task docker:dry-run --verbose

# Check current wallet credit and send Telegram summary
task docker:check-balance

# Live booking
task docker:run --date 2026-08-17 --time 18:00 --centre poblenou
```

The container runs Chrome in headless mode automatically (`ENV=docker`).

## GitHub Actions (Group Reminders)

Scheduled workflows in `.github/workflows/` automate weekly group coordination via Telegram:

- **Thursday Sign-Up Reminder & Poll:** Runs every Thursday morning (`+12 days` target date) to post payment instructions and a non-anonymous sign-up poll.
- **Monday Match-Eve Reminder:** Runs every Monday evening with match details and the 18:00 Poblenou weather and wind forecast (Open-Meteo with MET Norway fallback).

Both workflows support manual `workflow_dispatch` runs with a `test_mode` toggle (enabled by default) that routes messages to `TELEGRAM_TEST_CHAT_ID` instead of `TELEGRAM_CHAT_ID`. Configure the following **Repository secrets** in GitHub:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `TELEGRAM_TEST_CHAT_ID`

## Workflow & Output

1. **Login:** Authenticates against the Padel7 portal via `bot/login.py`.
2. **Balance Check (`--check-balance`):** Reads the post-login dashboard credit (`bot/balance.py`), skips the booking calendar completely, and sends a Telegram breakdown of how many indoor/outdoor courts can be booked.
3. **Court Selection & Checkout (`bot/booking.py`):** Finds matching time slots, selects the best court (`bot/utils.py`) with automatic court-type fallback, and captures the remaining wallet balance (*Saldo restant*) from the confirmation screen before completing checkout.
4. **Artifacts & Alerts:**
   - **Screenshots** saved to `padel7_booking_bot/screenshots/` after each run (useful for inspecting errors or dry-run states).
   - **Logs** written to `padel7_booking_bot/logs/bot.log`.
   - **Telegram notifications** dispatched on booking completion (including remaining balance and indoor courts left) or balance checks when `--notifications` is passed.

## Testing & Maintenance

```bash
# Run the pytest suite
task test

# Clear saved screenshots and log files
task clean
```