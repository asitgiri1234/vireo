"""Policy numbers and reporting conventions.

Sources: support-policy.pdf v3.2 (effective 1 Apr 2025) and the
helpdesk-admin note that the API export is UTC.
"""

from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
UTC = ZoneInfo("UTC")

# First-response targets, minutes from created_at to first_response_at.
SLA_MINUTES = {
    "chat": 15,
    "voice": 120,
    "social": 240,
    "email": 480,
}

# Automatic store credit issued on every first-response miss.
CREDIT_INR = 350

# Shift windows in IST. Night wraps midnight.
SHIFT_HOURS = {
    "Morning": (6, 14),   # 06:00 inclusive, 14:00 exclusive
    "Day": (14, 22),
    "Night": (22, 6),
}

# Last night-roster end date in agents.csv (Indore reshuffle).
NIGHT_COVERAGE_ENDED = "2025-06-29"

# Helpdesk cutover. Used only in the QA notes, not in the SLA calc.
HELPDESK_LIVE = "2025-09-14"

PREFERRED_SOURCE = "helpdesk"
CREDIT_LINE_NOTE = (
    "Every missed first-response target issues a Rs 350 store credit "
    "on resolution, charged to the SLA credit line."
)
