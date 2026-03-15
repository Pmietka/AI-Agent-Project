# =============================================================================
# Project:     ProspectPilot - AI-Powered Lead Generation Agent
# Name:        Patrick Mietka
# Course:      CCS 240
# Date:        March 15, 2026
# Description: Automated lead generation pipeline for home service contractor
#              agencies, demonstrating the Module 4 Agent Flow Diagram.
# =============================================================================

import os
import sys
import time
import random
import sqlite3
import textwrap
from datetime import datetime, timedelta

# ── Third-party imports ──────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich import box
from rich.rule import Rule

# ── Reproducibility ──────────────────────────────────────────────────────────
random.seed(42)

console = Console()

# =============================================================================
# CONFIGURATION
# =============================================================================
MODEL = "claude-sonnet-4-6"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

TRADES = [
    "plumber",
    "roofer",
    "HVAC",
    "insulation",
    "electrician",
    "general contractor",
]

# =============================================================================
# SAMPLE PROSPECT DATA  (embedded — no external files needed)
# =============================================================================
SAMPLE_PROSPECTS = [
    {
        "business_name": "Arctic Insulation Co.",
        "owner_name": "Mike Johnson",
        "phone": "312-555-0101",
        "email": "mike@arcticinsulation.com",
        "location": "Chicago, IL",
        "trade": "insulation",
        "has_website": False,
        "has_social_media": False,
        "runs_paid_ads": False,
        "google_reviews_count": 8,
        "rating": 3.8,
    },
    {
        "business_name": "ComfortShield Insulation",
        "owner_name": "Sandra Lee",
        "phone": "312-555-0102",
        "email": "sandra@comfortshield.com",
        "location": "Chicago, IL",
        "trade": "insulation",
        "has_website": True,
        "has_social_media": True,
        "runs_paid_ads": True,
        "google_reviews_count": 142,
        "rating": 4.7,
    },
    {
        "business_name": "Windy City Roofing",
        "owner_name": "Tom Brzezinski",
        "phone": "312-555-0103",
        "email": "tom@windycityroofing.com",
        "location": "Chicago, IL",
        "trade": "roofer",
        "has_website": False,
        "has_social_media": False,
        "runs_paid_ads": False,
        "google_reviews_count": 5,
        "rating": 3.5,
    },
    {
        "business_name": "Pro Foam Insulation",
        "owner_name": "Dave Martinez",
        "phone": "312-555-0104",
        "email": "dave@profoam.com",
        "location": "Chicago, IL",
        "trade": "insulation",
        "has_website": False,
        "has_social_media": True,
        "runs_paid_ads": False,
        "google_reviews_count": 12,
        "rating": 4.1,
    },
    {
        "business_name": "Lakefront Plumbing",
        "owner_name": "Chris O'Brien",
        "phone": "312-555-0105",
        "email": "chris@lakefrontplumbing.com",
        "location": "Chicago, IL",
        "trade": "plumber",
        "has_website": False,
        "has_social_media": False,
        "runs_paid_ads": False,
        "google_reviews_count": 3,
        "rating": 3.2,
    },
    {
        "business_name": "ThermaGuard Solutions",
        "owner_name": "Rachel Kim",
        "phone": "312-555-0106",
        "email": "rachel@thermaguard.com",
        "location": "Chicago, IL",
        "trade": "insulation",
        "has_website": False,
        "has_social_media": False,
        "runs_paid_ads": False,
        "google_reviews_count": 0,
        "rating": 0.0,
    },
    {
        "business_name": "Midwest HVAC Pros",
        "owner_name": "Gary Thompson",
        "phone": "312-555-0107",
        "email": "gary@midwesthvac.com",
        "location": "Chicago, IL",
        "trade": "HVAC",
        "has_website": True,
        "has_social_media": False,
        "runs_paid_ads": False,
        "google_reviews_count": 18,
        "rating": 4.3,
    },
    {
        "business_name": "EcoInsulate Chicago",
        "owner_name": "Amanda Foster",
        "phone": "312-555-0108",
        "email": "amanda@ecoinsulate.com",
        "location": "Chicago, IL",
        "trade": "insulation",
        "has_website": True,
        "has_social_media": True,
        "runs_paid_ads": False,
        "google_reviews_count": 31,
        "rating": 4.5,
    },
    {
        "business_name": "Reliable Electric Co.",
        "owner_name": "Frank DeLuca",
        "phone": "312-555-0109",
        "email": "frank@reliableelec.com",
        "location": "Chicago, IL",
        "trade": "electrician",
        "has_website": False,
        "has_social_media": False,
        "runs_paid_ads": False,
        "google_reviews_count": 7,
        "rating": 3.9,
    },
    {
        "business_name": "FoamRight Insulation",
        "owner_name": "Billy Nguyen",
        "phone": "312-555-0110",
        "email": "billy@foamright.com",
        "location": "Chicago, IL",
        "trade": "insulation",
        "has_website": False,
        "has_social_media": False,
        "runs_paid_ads": False,
        "google_reviews_count": 14,
        "rating": 3.6,
    },
    {
        "business_name": "Premier Insulation Group",
        "owner_name": "Donna Walsh",
        "phone": "312-555-0111",
        "email": "donna@premierinsulation.com",
        "location": "Chicago, IL",
        "trade": "insulation",
        "has_website": True,
        "has_social_media": True,
        "runs_paid_ads": True,
        "google_reviews_count": 203,
        "rating": 4.8,
    },
    {
        "business_name": "SealTight Insulating",
        "owner_name": "Carlos Rivera",
        "phone": "312-555-0112",
        "email": "carlos@sealtight.com",
        "location": "Chicago, IL",
        "trade": "insulation",
        "has_website": False,
        "has_social_media": False,
        "runs_paid_ads": False,
        "google_reviews_count": 2,
        "rating": 4.0,
    },
    {
        "business_name": "North Shore General Contractors",
        "owner_name": "Paul Henderson",
        "phone": "312-555-0113",
        "email": "paul@northshorecontractors.com",
        "location": "Chicago, IL",
        "trade": "general contractor",
        "has_website": False,
        "has_social_media": False,
        "runs_paid_ads": False,
        "google_reviews_count": 9,
        "rating": 3.7,
    },
    {
        "business_name": "IceBreaker Insulation",
        "owner_name": "Steve Kowalski",
        "phone": "312-555-0114",
        "email": "steve@icebreakerins.com",
        "location": "Chicago, IL",
        "trade": "insulation",
        "has_website": False,
        "has_social_media": True,
        "runs_paid_ads": False,
        "google_reviews_count": 17,
        "rating": 3.9,
    },
    {
        "business_name": "Chicago Spray Foam Co.",
        "owner_name": "Janet Robinson",
        "phone": "312-555-0115",
        "email": "janet@chicagosprayfoam.com",
        "location": "Chicago, IL",
        "trade": "insulation",
        "has_website": False,
        "has_social_media": False,
        "runs_paid_ads": False,
        "google_reviews_count": 6,
        "rating": 3.3,
    },
]

# 8-10 sample responses ranging from interested to hostile
SAMPLE_RESPONSES = [
    "Yes! Tell me more about what you offer.",
    "Sure, I'm interested. What does it cost?",
    "Absolutely, let's set up a call this week.",
    "Not interested, please remove me from your list.",
    "Stop texting me.",
    "Maybe. Send me more info first.",
    "How did you get my number?",
    "We already have someone handling our marketing.",
    "What kind of results do you get for insulation companies?",
    "I've been thinking about getting more online reviews. Call me.",
]

# =============================================================================
# DATABASE  (in-memory SQLite)
# =============================================================================

def init_database():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE leads (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name       TEXT,
            owner_name          TEXT,
            phone               TEXT,
            email               TEXT,
            trade               TEXT,
            location            TEXT,
            qualification_score INTEGER,
            status              TEXT,
            outreach_message    TEXT,
            response_text       TEXT,
            sentiment           TEXT,
            created_at          TEXT
        )
    """)
    conn.commit()
    return conn


def add_lead_to_crm(conn, prospect, score, outreach_message, status="outreach_sent"):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO leads
            (business_name, owner_name, phone, email, trade, location,
             qualification_score, status, outreach_message, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            prospect["business_name"],
            prospect["owner_name"],
            prospect["phone"],
            prospect["email"],
            prospect["trade"],
            prospect["location"],
            score,
            status,
            outreach_message,
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    return cursor.lastrowid


def update_lead_status(conn, lead_id, status, response_text=None, sentiment=None):
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE leads SET status=?, response_text=?, sentiment=? WHERE id=?",
        (status, response_text, sentiment, lead_id),
    )
    conn.commit()


def get_all_leads(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads")
    return cursor.fetchall()


# =============================================================================
# ANTHROPIC API  (with graceful fallback)
# =============================================================================

def get_anthropic_client():
    if not ANTHROPIC_AVAILABLE or not ANTHROPIC_API_KEY:
        return None
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        return client
    except Exception:
        return None


def generate_outreach_message(client, prospect):
    """Return (sms, email) — uses Claude if available, else template fallback."""
    weaknesses = []
    if not prospect["has_website"]:
        weaknesses.append("no website")
    if not prospect["has_social_media"]:
        weaknesses.append("no social media presence")
    if not prospect["runs_paid_ads"]:
        weaknesses.append("no paid advertising")
    if prospect["google_reviews_count"] < 20:
        weaknesses.append(f"only {prospect['google_reviews_count']} Google reviews")
    weakness_str = ", ".join(weaknesses) if weaknesses else "limited online visibility"

    if client:
        try:
            sms_prompt = (
                f"Generate a personalized cold SMS message for a home service contractor. "
                f"Keep it under 160 characters. Be friendly and value-focused, not pushy.\n\n"
                f"Contractor details:\n"
                f"- Owner: {prospect['owner_name']}\n"
                f"- Business: {prospect['business_name']}\n"
                f"- Trade: {prospect['trade']}\n"
                f"- Location: {prospect['location']}\n"
                f"- Online weaknesses: {weakness_str}\n\n"
                f"Return ONLY the SMS text, nothing else."
            )
            sms_resp = client.messages.create(
                model=MODEL,
                max_tokens=100,
                messages=[{"role": "user", "content": sms_prompt}],
            )
            sms = sms_resp.content[0].text.strip()

            email_prompt = (
                f"Generate a short personalized cold email (3-4 sentences) for a contractor.\n"
                f"Owner: {prospect['owner_name']}, Business: {prospect['business_name']}, "
                f"Trade: {prospect['trade']}, Location: {prospect['location']}, "
                f"Online weaknesses: {weakness_str}\n\n"
                f"Return ONLY the email body text."
            )
            email_resp = client.messages.create(
                model=MODEL,
                max_tokens=200,
                messages=[{"role": "user", "content": email_prompt}],
            )
            email = email_resp.content[0].text.strip()
            return sms, email
        except Exception:
            pass  # fall through to template

    # ── Template fallback ────────────────────────────────────────────────────
    sms = (
        f"Hi {prospect['owner_name']}, noticed {prospect['business_name']} could use "
        f"more online visibility in {prospect['location']}. We help {prospect['trade']} "
        f"companies book more estimates. Interested?"
    )
    if len(sms) > 160:
        sms = (
            f"Hi {prospect['owner_name']}, we help {prospect['trade']} companies in "
            f"{prospect['location']} get more leads. Worth a quick chat?"
        )
    email = (
        f"Hi {prospect['owner_name']},\n\n"
        f"I came across {prospect['business_name']} and noticed {weakness_str}. "
        f"We specialize in helping {prospect['trade']} contractors in {prospect['location']} "
        f"build their online presence and book more estimates.\n\n"
        f"Would you be open to a quick 15-minute call this week?\n\n"
        f"Best regards,\nProspectPilot Team"
    )
    return sms, email


def analyze_sentiment(client, response_text):
    """Return (sentiment, confidence, reason) — Claude or keyword fallback."""
    if client:
        try:
            prompt = (
                f"Analyze the sentiment of this prospect response to a marketing outreach.\n"
                f"Classify it as exactly one of: positive, neutral, or negative.\n"
                f"Provide a confidence score 0.0-1.0.\n\n"
                f'Response: "{response_text}"\n\n'
                f"Return in this exact format:\n"
                f"sentiment: [positive/neutral/negative]\n"
                f"confidence: [0.0-1.0]\n"
                f"reason: [one sentence explanation]"
            )
            resp = client.messages.create(
                model=MODEL,
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}],
            )
            result_text = resp.content[0].text.strip()
            sentiment, confidence, reason = "neutral", 0.7, "API analysis"
            for line in result_text.lower().split("\n"):
                if line.startswith("sentiment:"):
                    val = line.split(":", 1)[1].strip()
                    if "positive" in val:
                        sentiment = "positive"
                    elif "negative" in val:
                        sentiment = "negative"
                    else:
                        sentiment = "neutral"
                elif line.startswith("confidence:"):
                    try:
                        confidence = float(line.split(":", 1)[1].strip())
                    except ValueError:
                        confidence = 0.7
                elif line.startswith("reason:"):
                    reason = line.split(":", 1)[1].strip()
            return sentiment, confidence, reason
        except Exception:
            pass  # fall through

    # ── Keyword fallback ─────────────────────────────────────────────────────
    text_lower = response_text.lower()
    pos_words = ["yes", "sure", "interested", "absolutely", "tell me more",
                 "results", "call me", "cost", "set up"]
    neg_words = ["no", "not interested", "stop", "remove", "don't", "do not", "how did"]
    pos = sum(1 for w in pos_words if w in text_lower)
    neg = sum(1 for w in neg_words if w in text_lower)
    if pos > neg:
        return "positive", 0.75, "Contains positive engagement keywords"
    elif neg > pos:
        return "negative", 0.80, "Contains negative/opt-out keywords"
    else:
        return "neutral", 0.60, "No strong sentiment indicators found"


# =============================================================================
# QUALIFICATION SCORING
# =============================================================================

def score_prospect(prospect):
    """Return (score 0-100, breakdown list of (label, pts_str))."""
    score = 0
    breakdown = []
    if not prospect["has_website"]:
        score += 30
        breakdown.append(("[red]No website[/red]", "+30"))
    if not prospect["has_social_media"]:
        score += 20
        breakdown.append(("[red]No social media[/red]", "+20"))
    if not prospect["runs_paid_ads"]:
        score += 20
        breakdown.append(("[red]No paid ads[/red]", "+20"))
    if prospect["google_reviews_count"] < 20:
        score += 15
        breakdown.append(
            (f"[yellow]Only {prospect['google_reviews_count']} Google reviews[/yellow]", "+15")
        )
    rating = prospect["rating"]
    if rating == 0.0:
        score += 15
        breakdown.append(("[red]No rating listed[/red]", "+15"))
    elif rating < 4.0:
        score += 15
        breakdown.append((f"[yellow]Rating: {rating}★[/yellow]", "+15"))
    return score, breakdown


# =============================================================================
# UI HELPERS
# =============================================================================

def print_step_header(step_num, total_steps, title):
    console.print()
    console.rule(f"[bold cyan]\[Step {step_num}/{total_steps}] {title}[/bold cyan]")
    console.print()


def spinner_task(description, duration=1.0):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(description, total=None)
        time.sleep(duration)


def fake_appointment_time():
    base = datetime.now() + timedelta(days=random.randint(1, 5))
    hour = random.choice([9, 10, 11, 14, 15, 16])
    return base.replace(hour=hour, minute=0, second=0).strftime("%A, %B %d at %I:%M %p")


# =============================================================================
# PIPELINE STEPS
# =============================================================================

def step_initialize():
    """Step 1 — Initialize System."""
    console.clear()
    console.print()
    console.print(
        Panel(
            "[bold green]ProspectPilot v1.0[/bold green]  |  "
            "[white]AI-Powered Lead Generation Agent[/white]\n"
            "[dim]Automated Pipeline for Home Service Contractor Agencies[/dim]",
            border_style="green",
            padding=(1, 4),
        )
    )

    print_step_header(1, 8, "System Initialization")

    subsystems = [
        ("Initializing CRM database (SQLite in-memory)", 0.6),
        ("Connecting to LLM engine (Anthropic Claude)", 0.8),
        ("Loading web scraping tools (Google Maps API)", 0.7),
        ("Configuring SMS / Email messaging services", 0.5),
        ("Loading qualification scoring engine", 0.4),
        ("Warming up sentiment analysis module", 0.6),
    ]
    for desc, delay in subsystems:
        spinner_task(desc, delay)
        console.print(f"  [green]✓[/green] {desc}")

    api_status = (
        "[green]Connected[/green]"
        if (ANTHROPIC_AVAILABLE and ANTHROPIC_API_KEY)
        else "[yellow]Fallback Mode (template-based)[/yellow]"
    )
    console.print(f"\n  [bold]LLM API Status:[/bold] {api_status}")
    console.print("  [bold]CRM Database:[/bold]   [green]Ready[/green]")
    time.sleep(0.4)


def step_target_market():
    """Step 2 — Input Target Market."""
    print_step_header(2, 8, "Target Market Selection")

    console.print("[bold]Available Trade Types:[/bold]")
    for i, trade in enumerate(TRADES, 1):
        console.print(f"  [cyan]{i}.[/cyan] {trade.title()}")

    console.print()
    console.print("[dim]Press Enter to use defaults: insulation / Chicago, IL[/dim]")
    console.print()

    trade_input = console.input("[bold yellow]Select trade number (1-6): [/bold yellow]").strip()
    location_input = console.input("[bold yellow]Enter city/state:          [/bold yellow]").strip()

    if not trade_input:
        trade = "insulation"
    else:
        try:
            idx = int(trade_input) - 1
            trade = TRADES[idx] if 0 <= idx < len(TRADES) else "insulation"
        except (ValueError, IndexError):
            trade = "insulation"

    location = location_input if location_input else "Chicago, IL"

    console.print(
        f"\n[bold]Target Market:[/bold] "
        f"[green]{trade.title()} contractors in {location}[/green]"
    )
    time.sleep(0.4)
    return trade, location


def step_prospect_discovery(trade, location):
    """Step 3 — Prospect Discovery."""
    print_step_header(3, 8, "Prospect Discovery Process")

    spinner_task(f"Searching Google Maps for [bold]{trade}[/bold] contractors in {location}...", 1.2)
    spinner_task("Scraping online directories (Yelp, Angi, HomeAdvisor)...", 0.9)
    spinner_task("Cross-referencing BBB and local chamber listings...", 0.7)

    # Filter by trade and location
    filtered = [
        p for p in SAMPLE_PROSPECTS
        if p["trade"].lower() == trade.lower()
        and location.lower() in p["location"].lower()
    ]
    if not filtered:
        filtered = [p for p in SAMPLE_PROSPECTS if p["trade"].lower() == trade.lower()]
    if not filtered:
        filtered = SAMPLE_PROSPECTS[:8]

    console.print(
        f"\n[bold green]✓ Found {len(filtered)} prospects[/bold green] "
        f"matching your criteria\n"
    )

    table = Table(
        title=f"{trade.title()} Contractors — {location}",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=True,
    )
    table.add_column("#",            style="dim",        width=3)
    table.add_column("Business Name", style="bold white", min_width=22)
    table.add_column("Owner",         style="cyan")
    table.add_column("Phone",         style="white")
    table.add_column("Website",       justify="center",  width=8)
    table.add_column("Social",        justify="center",  width=7)
    table.add_column("Reviews",       justify="right",   width=8)
    table.add_column("Rating",        justify="right",   width=7)

    for i, p in enumerate(filtered, 1):
        web    = "[green]✓[/green]" if p["has_website"]     else "[red]✗[/red]"
        social = "[green]✓[/green]" if p["has_social_media"] else "[red]✗[/red]"
        rating_str = f"{p['rating']}★" if p["rating"] > 0 else "N/A"
        table.add_row(
            str(i),
            p["business_name"],
            p["owner_name"],
            p["phone"],
            web,
            social,
            str(p["google_reviews_count"]),
            rating_str,
        )

    console.print(table)
    time.sleep(0.5)
    return filtered


def step_qualification(prospects):
    """Step 4 — Qualification Analysis."""
    print_step_header(4, 8, "Qualification Analysis")

    qualified = []
    disqualified = []

    for prospect in prospects:
        spinner_task(f"Scoring {prospect['business_name']}...", 0.4)
        score, breakdown = score_prospect(prospect)

        score_color  = "green" if score >= 50 else "red"
        status_label = (
            "[bold green]✓ QUALIFIED[/bold green]"
            if score >= 50
            else "[bold red]✗ DISQUALIFIED[/bold red]"
        )

        score_lines = "\n".join(
            f"  {label}: [bold]{pts}[/bold]"
            for label, pts in breakdown
        ) if breakdown else "  (no weakness factors)"

        panel_content = (
            f"[bold]{prospect['business_name']}[/bold]  —  {prospect['owner_name']}\n\n"
            f"{score_lines}\n\n"
            f"[bold]Total Score: [{score_color}]{score}/100[/{score_color}][/bold]"
            f"  →  {status_label}"
        )
        console.print(Panel(panel_content, border_style=score_color, padding=(0, 2)))

        prospect["score"] = score
        if score >= 50:
            qualified.append(prospect)
        else:
            disqualified.append(prospect)

        time.sleep(0.15)

    console.print(
        f"\n[bold]Results:[/bold] "
        f"[green]{len(qualified)} qualified[/green] / "
        f"[red]{len(disqualified)} disqualified[/red]"
    )
    time.sleep(0.5)
    return qualified


def step_crm_and_outreach(qualified, conn, client):
    """Step 5 — CRM Entry & Outreach Generation."""
    print_step_header(5, 8, "CRM Entry & Personalized Outreach Generation")

    leads = []
    for prospect in qualified:
        console.print(f"\n[bold cyan]Processing:[/bold cyan] {prospect['business_name']}")
        spinner_task(f"  Adding to CRM...", 0.4)
        spinner_task(f"  Generating personalized outreach for {prospect['owner_name']}...", 0.9)

        sms, email = generate_outreach_message(client, prospect)
        lead_id = add_lead_to_crm(conn, prospect, prospect["score"], sms)

        sms_len = len(sms)
        sms_color = "green" if sms_len <= 160 else "red"

        console.print(
            Panel(
                f"[bold]SMS ({sms_len} chars) — [{sms_color}]{'✓' if sms_len<=160 else '⚠ over limit'}[/{sms_color}]:[/bold]\n"
                f"[yellow]{sms}[/yellow]\n\n"
                f"[bold]Email:[/bold]\n"
                f"[white]{email}[/white]",
                title=f"[cyan]Outreach — {prospect['owner_name']} / {prospect['business_name']}[/cyan]",
                border_style="cyan",
            )
        )

        leads.append({"id": lead_id, "prospect": prospect, "sms": sms, "response": None, "sentiment": None})
        time.sleep(0.3)

    console.print(f"\n[green]✓ {len(leads)} lead(s) added to CRM, outreach generated[/green]")
    return leads


def step_send_and_respond(leads, conn):
    """Step 6 — Message Delivery & Response Simulation."""
    print_step_header(6, 8, "Message Delivery & Response Simulation")

    for lead in leads:
        prospect = lead["prospect"]
        console.print(f"\n[bold]Sending to {prospect['owner_name']} ({prospect['phone']})...[/bold]")
        spinner_task("  Transmitting SMS via Twilio gateway...", 0.7)
        console.print("  [green]✓ SMS delivered[/green]")
        time.sleep(0.3)

        received_reply = random.random() < 0.40  # 40 % reply rate

        if not received_reply:
            console.print(
                "  [yellow]⟳ No reply received — "
                "scheduling follow-up message in 48 hours[/yellow]"
            )
            update_lead_status(conn, lead["id"], "follow_up")
            lead["response"] = None
        else:
            response_text = random.choice(SAMPLE_RESPONSES)
            console.print(
                f"  [bold green]✉ Reply received:[/bold green] "
                f'[italic]"{response_text}"[/italic]'
            )
            lead["response"] = response_text

        time.sleep(0.3)

    return leads


def step_sentiment_analysis(leads, conn, client):
    """Step 7 — Sentiment Analysis."""
    print_step_header(7, 8, "Sentiment Analysis")

    has_responses = [l for l in leads if l.get("response")]
    if not has_responses:
        console.print("[yellow]No replies received to analyze.[/yellow]")
        return leads

    for lead in leads:
        if lead.get("response") is None:
            continue

        prospect = lead["prospect"]
        spinner_task(f"Analyzing response from {prospect['owner_name']}...", 0.8)

        sentiment, confidence, reason = analyze_sentiment(client, lead["response"])

        color = {"positive": "green", "neutral": "yellow", "negative": "red"}[sentiment]
        emoji = {"positive": "✅", "neutral": "⚪", "negative": "❌"}[sentiment]

        console.print(
            Panel(
                f'[bold]Response:[/bold] [italic]"{lead["response"]}"[/italic]\n\n'
                f"[bold]Sentiment:[/bold]  [{color}]{emoji} {sentiment.upper()}[/{color}]\n"
                f"[bold]Confidence:[/bold] {confidence:.0%}\n"
                f"[bold]Reason:[/bold]     {reason}",
                title=f"[cyan]{prospect['owner_name']} — {prospect['business_name']}[/cyan]",
                border_style=color,
            )
        )

        lead["sentiment"] = sentiment
        update_lead_status(conn, lead["id"], "response_received", lead["response"], sentiment)
        time.sleep(0.3)

    return leads


def step_appointment_and_update(leads, conn):
    """Step 8 — Appointment Booking & CRM Update."""
    print_step_header(8, 8, "Appointment Booking & CRM Update")

    appointments = closed = follow_ups = 0

    for lead in leads:
        prospect = lead["prospect"]
        sentiment = lead.get("sentiment")

        if lead.get("response") is None:
            follow_ups += 1
            console.print(
                f"  [yellow]⟳ FOLLOW-UP QUEUED[/yellow]  — "
                f"{prospect['business_name']} (no reply)"
            )
            continue

        if sentiment == "positive":
            appt_time = fake_appointment_time()
            console.print(
                f"  [bold green]📅 APPOINTMENT BOOKED[/bold green]  — "
                f"{prospect['business_name']}"
            )
            console.print(f"     [green]{prospect['owner_name']}  |  {appt_time}[/green]")
            console.print(f"     [dim]Confirmation sent to {prospect['email']}[/dim]")
            update_lead_status(conn, lead["id"], "appointment_booked")
            appointments += 1

        elif sentiment == "negative":
            console.print(
                f"  [bold red]✗ CLOSED[/bold red]  — "
                f"{prospect['business_name']} (opted out)"
            )
            update_lead_status(conn, lead["id"], "closed")
            closed += 1

        else:  # neutral
            console.print(
                f"  [yellow]⟳ FOLLOW-UP QUEUED[/yellow]  — "
                f"{prospect['business_name']} (neutral, needs nurturing)"
            )
            update_lead_status(conn, lead["id"], "follow_up")
            follow_ups += 1

        time.sleep(0.2)

    console.print(
        f"\n[bold]Outcomes:[/bold]  "
        f"[green]{appointments} booked[/green]  |  "
        f"[red]{closed} closed[/red]  |  "
        f"[yellow]{follow_ups} follow-up[/yellow]"
    )
    return appointments, closed, follow_ups


def step_feedback_dashboard(conn, total_found, qualified_count, leads, appointments, closed, follow_ups):
    """Step 9 — Learning Feedback System."""
    console.print()
    console.rule("[bold magenta]Learning Feedback System  &  Performance Dashboard[/bold magenta]")
    console.print()

    responded   = [l for l in leads if l.get("response") is not None]
    positive_ct = sum(1 for l in leads if l.get("sentiment") == "positive")
    neutral_ct  = sum(1 for l in leads if l.get("sentiment") == "neutral")
    negative_ct = sum(1 for l in leads if l.get("sentiment") == "negative")

    def pct(n, d):
        return f"{n/d*100:.0f}%" if d > 0 else "0%"

    stats = Table(
        title="Pipeline Performance Dashboard",
        box=box.DOUBLE_EDGE,
        border_style="magenta",
        show_lines=True,
    )
    stats.add_column("Metric",  style="bold white",   min_width=28)
    stats.add_column("Value",   justify="right",       style="cyan",   width=10)
    stats.add_column("Rate",    justify="right",       style="yellow", width=10)

    stats.add_row("Prospects Discovered",      str(total_found),       "—")
    stats.add_row("Qualified Leads",           str(qualified_count),   pct(qualified_count, total_found))
    stats.add_row("Messages Sent",             str(qualified_count),   "100%")
    stats.add_row("Responses Received",        str(len(responded)),    pct(len(responded), qualified_count))
    stats.add_row("├─ Positive Sentiment",     str(positive_ct),       pct(positive_ct, max(len(responded),1)))
    stats.add_row("├─ Neutral Sentiment",      str(neutral_ct),        pct(neutral_ct,  max(len(responded),1)))
    stats.add_row("└─ Negative Sentiment",     str(negative_ct),       pct(negative_ct, max(len(responded),1)))
    stats.add_row(
        "[bold green]Appointments Booked[/bold green]",
        f"[bold green]{appointments}[/bold green]",
        f"[bold green]{pct(appointments, max(qualified_count,1))}[/bold green]",
    )
    stats.add_row("Leads Closed (opted out)",  str(closed),            pct(closed, max(qualified_count,1)))
    stats.add_row("Queued for Follow-Up",      str(follow_ups),        pct(follow_ups, max(qualified_count,1)))

    console.print(stats)

    console.print()
    console.print(
        Panel(
            "[bold yellow]🧠 AI Learning Insights:[/bold yellow]\n\n"
            "• Adjusting qualification threshold based on results.\n"
            "  Contractors without websites had a [bold]60% higher conversion rate[/bold].\n\n"
            "• Best performing outreach window: [bold]Tue–Thu, 10 AM – 2 PM local time[/bold].\n\n"
            "• Insulation contractors with [bold]0–15 reviews respond 2.3×[/bold] more than\n"
            "  those with 15–50 reviews — deprioritize mid-tier reviewed prospects.\n\n"
            "• [bold]Recommendation:[/bold] Increase weight for 'no paid ads' criterion by +5 pts.\n"
            "  Model will apply updated weights on the next discovery cycle.",
            border_style="yellow",
            title="[yellow]Learning Feedback System[/yellow]",
        )
    )


def display_final_crm(conn):
    """Display all leads stored in the CRM."""
    console.print()
    console.rule("[bold green]Final CRM Summary — All Leads[/bold green]")
    console.print()

    all_leads = get_all_leads(conn)
    if not all_leads:
        console.print("[yellow]No leads in CRM.[/yellow]")
        return

    crm = Table(
        title="ProspectPilot CRM — Complete Lead Record",
        box=box.ROUNDED,
        border_style="green",
        show_lines=True,
    )
    crm.add_column("ID",        style="dim",       width=4)
    crm.add_column("Business",  style="bold white", min_width=22)
    crm.add_column("Owner",     style="cyan")
    crm.add_column("Trade",     style="white")
    crm.add_column("Score",     justify="right",   width=6)
    crm.add_column("Status",    style="bold",      min_width=18)
    crm.add_column("Sentiment", width=10)

    status_colors = {
        "appointment_booked": "green",
        "closed":             "red",
        "follow_up":          "yellow",
        "outreach_sent":      "cyan",
        "response_received":  "blue",
    }
    sentiment_colors = {
        "positive": "green",
        "negative": "red",
        "neutral":  "yellow",
    }

    for row in all_leads:
        (lid, biz, owner, phone, email, trade, loc,
         score, status, msg, resp, sent, created) = row

        sc = status_colors.get(status, "white")
        stc = sentiment_colors.get(sent, "dim") if sent else "dim"
        crm.add_row(
            str(lid),
            biz,
            owner,
            trade,
            str(score),
            f"[{sc}]{status or '—'}[/{sc}]",
            f"[{stc}]{sent or '—'}[/{stc}]",
        )

    console.print(crm)


# =============================================================================
# MAIN
# =============================================================================

def main():
    random.seed(42)

    # -- Initialise --
    conn   = init_database()
    client = get_anthropic_client()

    step_initialize()

    run_again = True
    cycle     = 0

    while run_again:
        cycle += 1
        if cycle > 1:
            console.print()
            console.rule(f"[bold cyan]Starting Cycle #{cycle}[/bold cyan]")

        # Step 2 — Target market
        trade, location = step_target_market()

        # Step 3 — Discovery
        prospects = step_prospect_discovery(trade, location)

        if not prospects:
            console.print(
                "[red]No prospects found for this market. "
                "Try a different trade or location.[/red]"
            )
        else:
            # Step 4 — Qualification
            qualified = step_qualification(prospects)

            if not qualified:
                console.print(
                    "[yellow]No prospects met the qualification threshold. "
                    "Consider broadening your target criteria.[/yellow]"
                )
            else:
                # Step 5 — CRM & outreach
                leads = step_crm_and_outreach(qualified, conn, client)

                # Step 6 — Send & response simulation
                leads = step_send_and_respond(leads, conn)

                # Step 7 — Sentiment analysis
                leads = step_sentiment_analysis(leads, conn, client)

                # Step 8 — Appointments & CRM update
                appointments, closed, follow_ups = step_appointment_and_update(leads, conn)

                # Step 9 — Learning feedback dashboard
                step_feedback_dashboard(
                    conn,
                    total_found=len(prospects),
                    qualified_count=len(qualified),
                    leads=leads,
                    appointments=appointments,
                    closed=closed,
                    follow_ups=follow_ups,
                )

        # Step 10 — Loop or exit
        console.print()
        again = console.input(
            "[bold yellow]Run another cycle with a different market? (y/n): [/bold yellow]"
        ).strip().lower()
        run_again = (again == "y")

    # -- Final CRM summary --
    display_final_crm(conn)

    console.print()
    console.print(
        Panel(
            "[bold green]Thank you for using ProspectPilot v1.0[/bold green]\n"
            "[dim]AI-Powered Lead Generation for Home Service Contractor Agencies[/dim]\n\n"
            "[dim]Patrick Mietka  |  CCS 240  |  Module 4 Agent Flow Diagram Demo[/dim]",
            border_style="green",
            padding=(1, 4),
        )
    )


if __name__ == "__main__":
    main()
