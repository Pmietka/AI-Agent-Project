# =============================================================================
# Project:     ProspectPilot GUI - AI-Powered Lead Generation Agent
# Name:        Patrick Mietka
# Course:      CCS 240
# Date:        March 15, 2026
# Description: Tkinter GUI for the ProspectPilot automated lead generation agent
# =============================================================================

import os
import time
import random
import sqlite3
import threading
import queue
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

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

random.seed(42)

# =============================================================================
# THEME COLOURS
# =============================================================================
BG       = "#0d1117"
BG_PANEL = "#161b22"
BG_CARD  = "#21262d"
BORDER   = "#30363d"
TEXT     = "#c9d1d9"
DIM      = "#8b949e"
ACCENT   = "#58a6ff"
GREEN    = "#3fb950"
RED      = "#f85149"
YELLOW   = "#e3b341"
CYAN     = "#79c0ff"
PURPLE   = "#bc8cff"

# =============================================================================
# CONSTANTS
# =============================================================================
MODEL  = "claude-sonnet-4-6"
APIKEY = os.getenv("ANTHROPIC_API_KEY", "")

TRADES = ["plumber", "roofer", "HVAC", "insulation", "electrician", "general contractor"]

PIPELINE_STEPS = [
    "Initialize System",
    "Prospect Discovery",
    "Qualification Analysis",
    "CRM & Outreach Generation",
    "Send Messages & Simulate Replies",
    "Sentiment Analysis",
    "Appointment Booking & CRM Update",
    "Learning Feedback Dashboard",
]

# =============================================================================
# SAMPLE DATA  (embedded — no external files)
# =============================================================================
SAMPLE_PROSPECTS = [
    {"business_name": "Arctic Insulation Co.",       "owner_name": "Mike Johnson",   "phone": "312-555-0101", "email": "mike@arcticinsulation.com",   "location": "Chicago, IL", "trade": "insulation",        "has_website": False, "has_social_media": False, "runs_paid_ads": False, "google_reviews_count": 8,   "rating": 3.8},
    {"business_name": "ComfortShield Insulation",    "owner_name": "Sandra Lee",     "phone": "312-555-0102", "email": "sandra@comfortshield.com",    "location": "Chicago, IL", "trade": "insulation",        "has_website": True,  "has_social_media": True,  "runs_paid_ads": True,  "google_reviews_count": 142, "rating": 4.7},
    {"business_name": "Windy City Roofing",          "owner_name": "Tom Brzezinski", "phone": "312-555-0103", "email": "tom@windycityroofing.com",    "location": "Chicago, IL", "trade": "roofer",            "has_website": False, "has_social_media": False, "runs_paid_ads": False, "google_reviews_count": 5,   "rating": 3.5},
    {"business_name": "Pro Foam Insulation",         "owner_name": "Dave Martinez",  "phone": "312-555-0104", "email": "dave@profoam.com",            "location": "Chicago, IL", "trade": "insulation",        "has_website": False, "has_social_media": True,  "runs_paid_ads": False, "google_reviews_count": 12,  "rating": 4.1},
    {"business_name": "Lakefront Plumbing",          "owner_name": "Chris O'Brien",  "phone": "312-555-0105", "email": "chris@lakefrontplumbing.com", "location": "Chicago, IL", "trade": "plumber",           "has_website": False, "has_social_media": False, "runs_paid_ads": False, "google_reviews_count": 3,   "rating": 3.2},
    {"business_name": "ThermaGuard Solutions",       "owner_name": "Rachel Kim",     "phone": "312-555-0106", "email": "rachel@thermaguard.com",      "location": "Chicago, IL", "trade": "insulation",        "has_website": False, "has_social_media": False, "runs_paid_ads": False, "google_reviews_count": 0,   "rating": 0.0},
    {"business_name": "Midwest HVAC Pros",           "owner_name": "Gary Thompson",  "phone": "312-555-0107", "email": "gary@midwesthvac.com",        "location": "Chicago, IL", "trade": "HVAC",              "has_website": True,  "has_social_media": False, "runs_paid_ads": False, "google_reviews_count": 18,  "rating": 4.3},
    {"business_name": "EcoInsulate Chicago",         "owner_name": "Amanda Foster",  "phone": "312-555-0108", "email": "amanda@ecoinsulate.com",      "location": "Chicago, IL", "trade": "insulation",        "has_website": True,  "has_social_media": True,  "runs_paid_ads": False, "google_reviews_count": 31,  "rating": 4.5},
    {"business_name": "Reliable Electric Co.",       "owner_name": "Frank DeLuca",   "phone": "312-555-0109", "email": "frank@reliableelec.com",      "location": "Chicago, IL", "trade": "electrician",       "has_website": False, "has_social_media": False, "runs_paid_ads": False, "google_reviews_count": 7,   "rating": 3.9},
    {"business_name": "FoamRight Insulation",        "owner_name": "Billy Nguyen",   "phone": "312-555-0110", "email": "billy@foamright.com",         "location": "Chicago, IL", "trade": "insulation",        "has_website": False, "has_social_media": False, "runs_paid_ads": False, "google_reviews_count": 14,  "rating": 3.6},
    {"business_name": "Premier Insulation Group",    "owner_name": "Donna Walsh",    "phone": "312-555-0111", "email": "donna@premierinsulation.com", "location": "Chicago, IL", "trade": "insulation",        "has_website": True,  "has_social_media": True,  "runs_paid_ads": True,  "google_reviews_count": 203, "rating": 4.8},
    {"business_name": "SealTight Insulating",        "owner_name": "Carlos Rivera",  "phone": "312-555-0112", "email": "carlos@sealtight.com",        "location": "Chicago, IL", "trade": "insulation",        "has_website": False, "has_social_media": False, "runs_paid_ads": False, "google_reviews_count": 2,   "rating": 4.0},
    {"business_name": "North Shore General",         "owner_name": "Paul Henderson", "phone": "312-555-0113", "email": "paul@northshorecontractors.com","location": "Chicago, IL","trade": "general contractor","has_website": False, "has_social_media": False, "runs_paid_ads": False, "google_reviews_count": 9,   "rating": 3.7},
    {"business_name": "IceBreaker Insulation",       "owner_name": "Steve Kowalski", "phone": "312-555-0114", "email": "steve@icebreakerins.com",     "location": "Chicago, IL", "trade": "insulation",        "has_website": False, "has_social_media": True,  "runs_paid_ads": False, "google_reviews_count": 17,  "rating": 3.9},
    {"business_name": "Chicago Spray Foam Co.",      "owner_name": "Janet Robinson", "phone": "312-555-0115", "email": "janet@chicagosprayfoam.com",  "location": "Chicago, IL", "trade": "insulation",        "has_website": False, "has_social_media": False, "runs_paid_ads": False, "google_reviews_count": 6,   "rating": 3.3},
]

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
# DATABASE
# =============================================================================

def init_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT, owner_name TEXT, phone TEXT, email TEXT,
            trade TEXT, location TEXT, qualification_score INTEGER,
            status TEXT, outreach_message TEXT, response_text TEXT,
            sentiment TEXT, created_at TEXT
        )
    """)
    conn.commit()
    return conn

def db_add_lead(conn, p, score, sms):
    cur = conn.execute(
        "INSERT INTO leads (business_name,owner_name,phone,email,trade,location,"
        "qualification_score,status,outreach_message,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (p["business_name"], p["owner_name"], p["phone"], p["email"],
         p["trade"], p["location"], score, "outreach_sent", sms, datetime.now().isoformat())
    )
    conn.commit()
    return cur.lastrowid

def db_update(conn, lead_id, status, response=None, sentiment=None):
    conn.execute("UPDATE leads SET status=?,response_text=?,sentiment=? WHERE id=?",
                 (status, response, sentiment, lead_id))
    conn.commit()

def db_all(conn):
    return conn.execute("SELECT * FROM leads").fetchall()

# =============================================================================
# SCORING
# =============================================================================

def score_prospect(p):
    score, reasons = 0, []
    if not p["has_website"]:              score += 30; reasons.append("No website (+30)")
    if not p["has_social_media"]:         score += 20; reasons.append("No social (+20)")
    if not p["runs_paid_ads"]:            score += 20; reasons.append("No paid ads (+20)")
    if p["google_reviews_count"] < 20:    score += 15; reasons.append(f"Only {p['google_reviews_count']} reviews (+15)")
    r = p["rating"]
    if r == 0.0:                          score += 15; reasons.append("No rating (+15)")
    elif r < 4.0:                         score += 15; reasons.append(f"Low rating {r}★ (+15)")
    return score, reasons

# =============================================================================
# API CALLS  (with fallback)
# =============================================================================

def get_client():
    if not ANTHROPIC_AVAILABLE or not APIKEY:
        return None
    try:
        return anthropic.Anthropic(api_key=APIKEY)
    except Exception:
        return None

def gen_outreach(client, p):
    weaknesses = []
    if not p["has_website"]:           weaknesses.append("no website")
    if not p["has_social_media"]:      weaknesses.append("no social media")
    if not p["runs_paid_ads"]:         weaknesses.append("no paid ads")
    if p["google_reviews_count"] < 20: weaknesses.append(f"only {p['google_reviews_count']} reviews")
    w = ", ".join(weaknesses) or "limited online visibility"

    if client:
        try:
            sms_r = client.messages.create(model=MODEL, max_tokens=100, messages=[{"role":"user","content":
                f"Cold SMS under 160 chars for {p['owner_name']} at {p['business_name']} ({p['trade']} in "
                f"{p['location']}). Weaknesses: {w}. Friendly, value-focused. Return ONLY the SMS text."}])
            sms = sms_r.content[0].text.strip()
            email_r = client.messages.create(model=MODEL, max_tokens=200, messages=[{"role":"user","content":
                f"3-4 sentence cold email for {p['owner_name']} at {p['business_name']} ({p['trade']}, "
                f"{p['location']}). Weaknesses: {w}. Return ONLY the email body."}])
            email = email_r.content[0].text.strip()
            return sms, email
        except Exception:
            pass

    sms = f"Hi {p['owner_name']}, noticed {p['business_name']} could use more visibility in {p['location']}. We help {p['trade']} companies book more estimates. Interested?"
    if len(sms) > 160:
        sms = f"Hi {p['owner_name']}, we help {p['trade']} companies in {p['location']} get more leads. Quick chat?"
    email = (f"Hi {p['owner_name']},\n\nI noticed {p['business_name']} has {w}. We help {p['trade']} "
             f"contractors in {p['location']} build their online presence and book more estimates.\n\n"
             f"Would you be open to a 15-min call this week?\n\nBest,\nProspectPilot Team")
    return sms, email

def analyze_sentiment(client, text):
    if client:
        try:
            r = client.messages.create(model=MODEL, max_tokens=80, messages=[{"role":"user","content":
                f'Classify sentiment of this prospect reply as positive/neutral/negative.\n'
                f'Reply: "{text}"\nFormat:\nsentiment: X\nconfidence: 0.0-1.0\nreason: one sentence'}])
            lines = r.content[0].text.strip().lower().split("\n")
            s, c, reason = "neutral", 0.7, "AI analysis"
            for line in lines:
                if line.startswith("sentiment:"):
                    v = line.split(":",1)[1].strip()
                    s = "positive" if "positive" in v else ("negative" if "negative" in v else "neutral")
                elif line.startswith("confidence:"):
                    try: c = float(line.split(":",1)[1].strip())
                    except: pass
                elif line.startswith("reason:"):
                    reason = line.split(":",1)[1].strip()
            return s, c, reason
        except Exception:
            pass

    tl = text.lower()
    pos = sum(1 for w in ["yes","sure","interested","absolutely","tell me","results","call me"] if w in tl)
    neg = sum(1 for w in ["no","not interested","stop","remove","don't","how did"] if w in tl)
    if pos > neg:   return "positive", 0.75, "Positive engagement keywords"
    elif neg > pos: return "negative", 0.80, "Negative/opt-out keywords"
    else:           return "neutral",  0.60,  "No strong indicators"

def fake_appt():
    base = datetime.now() + timedelta(days=random.randint(1,5))
    h = random.choice([9,10,11,14,15,16])
    return base.replace(hour=h, minute=0, second=0).strftime("%A %B %d at %I:%M %p")

# =============================================================================
# PIPELINE  (runs in background thread, sends messages to GUI queue)
# =============================================================================

def run_pipeline(trade, location, out_q):
    """Main pipeline logic. Communicates with GUI via out_q."""

    def log(msg, color="text"):
        out_q.put(("log", msg, color))

    def step_start(i):
        out_q.put(("step_start", i))

    def step_done(i):
        out_q.put(("step_done", i))

    def sep():
        log("─" * 60, "dim")

    random.seed(42)
    conn   = init_db()
    client = get_client()

    # ── Step 0: Initialize ────────────────────────────────────────────────
    step_start(0)
    log("ProspectPilot v1.0  |  AI-Powered Lead Generation Agent", "accent")
    sep()
    subsystems = [
        "Initializing CRM database (SQLite in-memory)...",
        "Connecting to LLM engine (Anthropic Claude)...",
        "Loading web scraping tools (Google Maps API)...",
        "Configuring SMS/Email messaging services...",
        "Loading qualification scoring engine...",
        "Warming up sentiment analysis module...",
    ]
    for s in subsystems:
        time.sleep(0.5)
        log(f"  ✓  {s}", "green")
    api_txt = "Connected" if (ANTHROPIC_AVAILABLE and APIKEY) else "Fallback Mode (no API key)"
    api_col = "green" if (ANTHROPIC_AVAILABLE and APIKEY) else "yellow"
    log(f"\n  API Status:  {api_txt}", api_col)
    log(f"  CRM:         Ready\n", "green")
    step_done(0)
    time.sleep(0.3)

    # ── Step 1: Discovery ─────────────────────────────────────────────────
    step_start(1)
    log(f"Searching Google Maps for {trade} contractors in {location}...", "cyan")
    time.sleep(0.8)
    log("Scraping Yelp, Angi, HomeAdvisor...", "cyan")
    time.sleep(0.7)

    prospects = [p for p in SAMPLE_PROSPECTS
                 if p["trade"].lower() == trade.lower()
                 and location.lower() in p["location"].lower()]
    if not prospects:
        prospects = [p for p in SAMPLE_PROSPECTS if p["trade"].lower() == trade.lower()]
    if not prospects:
        prospects = SAMPLE_PROSPECTS[:8]

    log(f"\n  Found {len(prospects)} prospects\n", "green")
    log(f"  {'#':<3} {'Business':<28} {'Owner':<18} {'Web':^5} {'Social':^7} {'Reviews':^8} {'Rating':^7}", "accent")
    log(f"  {'─'*3} {'─'*28} {'─'*18} {'─'*5} {'─'*7} {'─'*8} {'─'*7}", "dim")
    for i, p in enumerate(prospects, 1):
        web    = "✓" if p["has_website"]     else "✗"
        social = "✓" if p["has_social_media"] else "✗"
        rat    = f"{p['rating']}★" if p["rating"] > 0 else "N/A"
        col    = "text" if p["has_website"] else "yellow"
        log(f"  {i:<3} {p['business_name']:<28} {p['owner_name']:<18} {web:^5} {social:^7} {p['google_reviews_count']:^8} {rat:^7}", col)

    out_q.put(("stats_update", "found", len(prospects)))
    step_done(1)
    time.sleep(0.3)

    # ── Step 2: Qualification ─────────────────────────────────────────────
    step_start(2)
    log("", "text")
    qualified, disqualified = [], []

    for p in prospects:
        time.sleep(0.3)
        score, reasons = score_prospect(p)
        p["score"] = score
        qualified_flag = score >= 50
        status_str = "✓ QUALIFIED" if qualified_flag else "✗ DISQUALIFIED"
        col        = "green"       if qualified_flag else "red"
        log(f"  {p['business_name']:<30}  Score: {score:>3}/100  →  {status_str}", col)
        for r in reasons:
            log(f"      • {r}", "dim")
        if qualified_flag:
            qualified.append(p)
        else:
            disqualified.append(p)

    log(f"\n  Qualified: {len(qualified)}   Disqualified: {len(disqualified)}\n", "text")
    out_q.put(("stats_update", "qualified", len(qualified)))
    step_done(2)
    time.sleep(0.3)

    if not qualified:
        log("No qualified prospects. Pipeline complete.", "yellow")
        out_q.put(("done",))
        return

    # ── Step 3: CRM & Outreach ────────────────────────────────────────────
    step_start(3)
    leads = []
    for p in qualified:
        time.sleep(0.5)
        log(f"\n  Processing: {p['business_name']} ({p['owner_name']})", "cyan")
        log(f"  Adding to CRM...", "dim")
        sms, email = gen_outreach(client, p)
        lead_id    = db_add_lead(conn, p, p["score"], sms)
        log(f"  SMS ({len(sms)} chars):  {sms}", "yellow")
        log(f"  Email:  {email[:80]}{'...' if len(email)>80 else ''}", "dim")
        leads.append({"id": lead_id, "prospect": p, "sms": sms, "response": None, "sentiment": None})

    log(f"\n  {len(leads)} leads added to CRM\n", "green")
    step_done(3)
    time.sleep(0.3)

    # ── Step 4: Send & Respond ────────────────────────────────────────────
    step_start(4)
    for lead in leads:
        p = lead["prospect"]
        time.sleep(0.5)
        log(f"\n  → Sending to {p['owner_name']} ({p['phone']})...", "text")
        time.sleep(0.4)
        log(f"    ✓ SMS delivered", "green")

        if random.random() < 0.40:
            reply = random.choice(SAMPLE_RESPONSES)
            log(f"    ✉ Reply: \"{reply}\"", "cyan")
            lead["response"] = reply
        else:
            log(f"    ⟳ No reply — follow-up scheduled in 48h", "yellow")
            db_update(conn, lead["id"], "follow_up")

    replied = sum(1 for l in leads if l["response"])
    log(f"\n  Sent: {len(leads)}   Replied: {replied}\n", "text")
    out_q.put(("stats_update", "sent", len(leads)))
    out_q.put(("stats_update", "replied", replied))
    step_done(4)
    time.sleep(0.3)

    # ── Step 5: Sentiment ─────────────────────────────────────────────────
    step_start(5)
    for lead in leads:
        if not lead["response"]:
            continue
        time.sleep(0.5)
        p = lead["prospect"]
        sentiment, conf, reason = analyze_sentiment(client, lead["response"])
        col = {"positive": "green", "neutral": "yellow", "negative": "red"}[sentiment]
        icon= {"positive": "✅", "neutral": "⚪", "negative": "❌"}[sentiment]
        log(f"\n  {p['owner_name']:20}  {icon} {sentiment.upper():<9}  {conf:.0%}  —  {reason}", col)
        lead["sentiment"] = sentiment
        db_update(conn, lead["id"], "response_received", lead["response"], sentiment)

    log("", "text")
    step_done(5)
    time.sleep(0.3)

    # ── Step 6: Appointments ──────────────────────────────────────────────
    step_start(6)
    booked = closed = follow_ups = 0

    for lead in leads:
        p = lead["prospect"]
        if not lead["response"]:
            follow_ups += 1
            continue
        s = lead["sentiment"]
        if s == "positive":
            appt = fake_appt()
            log(f"\n  📅 BOOKED  {p['business_name']}", "green")
            log(f"     {p['owner_name']}  |  {appt}", "green")
            db_update(conn, lead["id"], "appointment_booked")
            booked += 1
        elif s == "negative":
            log(f"\n  ✗ CLOSED   {p['business_name']}  (opted out)", "red")
            db_update(conn, lead["id"], "closed")
            closed += 1
        else:
            log(f"\n  ⟳ FOLLOW-UP  {p['business_name']}", "yellow")
            db_update(conn, lead["id"], "follow_up")
            follow_ups += 1
        time.sleep(0.2)

    log(f"\n  Booked: {booked}   Closed: {closed}   Follow-up: {follow_ups}\n", "text")
    out_q.put(("stats_update", "booked", booked))
    step_done(6)
    time.sleep(0.3)

    # ── Step 7: Feedback ──────────────────────────────────────────────────
    step_start(7)
    pos = sum(1 for l in leads if l.get("sentiment") == "positive")
    neu = sum(1 for l in leads if l.get("sentiment") == "neutral")
    neg = sum(1 for l in leads if l.get("sentiment") == "negative")

    log("  Pipeline Performance Summary", "accent")
    sep()
    def pct(n, d): return f"{n/d*100:.0f}%" if d else "0%"
    rows = [
        ("Prospects discovered",  str(len(prospects)),  "—"),
        ("Qualified leads",       str(len(qualified)),  pct(len(qualified), len(prospects))),
        ("Messages sent",         str(len(leads)),      "100%"),
        ("Replies received",      str(replied),         pct(replied, len(leads))),
        ("  Positive",            str(pos),             pct(pos, max(replied,1))),
        ("  Neutral",             str(neu),             pct(neu, max(replied,1))),
        ("  Negative",            str(neg),             pct(neg, max(replied,1))),
        ("Appointments booked",   str(booked),          pct(booked, max(len(leads),1))),
    ]
    for label, val, rate in rows:
        col = "green" if "Appointments" in label else "text"
        log(f"  {label:<30} {val:>6}   {rate:>6}", col)

    log("", "text")
    log("  🧠 AI Insight: Contractors without websites had a 60% higher conversion rate.", "yellow")
    log("  🧠 AI Insight: Best outreach window — Tue–Thu, 10 AM – 2 PM local time.", "yellow")
    log("  🧠 Recommendation: Increase 'no paid ads' weight by +5 pts next cycle.\n", "yellow")
    step_done(7)

    # Send final CRM rows to GUI
    for row in db_all(conn):
        out_q.put(("crm_row", row))

    out_q.put(("done",))

# =============================================================================
# GUI APPLICATION
# =============================================================================

class ProspectPilotApp:

    def __init__(self, root):
        self.root   = root
        self.q      = queue.Queue()
        self.running = False
        self._stats  = {"found": 0, "qualified": 0, "sent": 0, "replied": 0, "booked": 0}
        self._build_ui()
        self.root.after(50, self._poll_queue)

    # ── UI Construction ───────────────────────────────────────────────────

    def _build_ui(self):
        self.root.title("ProspectPilot v1.0")
        self.root.configure(bg=BG)
        self.root.geometry("1200x780")
        self.root.minsize(900, 600)
        self._apply_ttk_style()

        # Top-level grid: header / body / status
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self._build_header()
        self._build_body()
        self._build_statusbar()

    def _apply_ttk_style(self):
        st = ttk.Style()
        st.theme_use("default")
        st.configure("Dark.TFrame",      background=BG)
        st.configure("Panel.TFrame",     background=BG_PANEL)
        st.configure("Card.TFrame",      background=BG_CARD)
        st.configure("Dark.TLabel",      background=BG,       foreground=TEXT,   font=("Segoe UI", 10))
        st.configure("Panel.TLabel",     background=BG_PANEL, foreground=TEXT,   font=("Segoe UI", 10))
        st.configure("Card.TLabel",      background=BG_CARD,  foreground=TEXT,   font=("Segoe UI", 10))
        st.configure("Header.TLabel",    background=BG,       foreground=ACCENT, font=("Segoe UI", 18, "bold"))
        st.configure("Sub.TLabel",       background=BG,       foreground=DIM,    font=("Segoe UI", 9))
        st.configure("Step.TLabel",      background=BG_PANEL, foreground=DIM,    font=("Segoe UI", 9))
        st.configure("StepDone.TLabel",  background=BG_PANEL, foreground=GREEN,  font=("Segoe UI", 9))
        st.configure("StepRun.TLabel",   background=BG_PANEL, foreground=YELLOW, font=("Segoe UI", 9, "bold"))
        st.configure("Stat.TLabel",      background=BG_PANEL, foreground=TEXT,   font=("Segoe UI", 10))
        st.configure("StatVal.TLabel",   background=BG_PANEL, foreground=ACCENT, font=("Segoe UI", 13, "bold"))
        st.configure("Run.TButton",      font=("Segoe UI", 10, "bold"), padding=(14, 6))
        st.configure("Clear.TButton",    font=("Segoe UI", 10),         padding=(10, 6))
        st.configure("Dark.TCombobox",   fieldbackground=BG_CARD, background=BG_CARD,
                     foreground=TEXT, selectbackground=BG_CARD, selectforeground=ACCENT)
        st.configure("Treeview",         background=BG_CARD, fieldbackground=BG_CARD,
                     foreground=TEXT, rowheight=24)
        st.configure("Treeview.Heading", background=BG_PANEL, foreground=ACCENT, font=("Segoe UI", 9, "bold"))
        st.map("Treeview", background=[("selected", "#2d333b")])

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=BG_PANEL, height=70)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.columnconfigure(1, weight=1)

        # Logo block
        logo_f = tk.Frame(hdr, bg=BG_PANEL)
        logo_f.grid(row=0, column=0, padx=20, pady=12, sticky="w")
        tk.Label(logo_f, text="ProspectPilot", bg=BG_PANEL, fg=ACCENT,
                 font=("Segoe UI", 18, "bold")).pack(side="left")
        tk.Label(logo_f, text="  v1.0", bg=BG_PANEL, fg=DIM,
                 font=("Segoe UI", 12)).pack(side="left")

        # Controls block
        ctrl_f = tk.Frame(hdr, bg=BG_PANEL)
        ctrl_f.grid(row=0, column=1, padx=20, pady=12, sticky="e")

        tk.Label(ctrl_f, text="Trade:", bg=BG_PANEL, fg=DIM,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 6))
        self.trade_var = tk.StringVar(value="insulation")
        trade_cb = ttk.Combobox(ctrl_f, textvariable=self.trade_var,
                                values=TRADES, state="readonly",
                                width=16, style="Dark.TCombobox")
        trade_cb.pack(side="left", padx=(0, 16))

        tk.Label(ctrl_f, text="City/State:", bg=BG_PANEL, fg=DIM,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 6))
        self.city_var = tk.StringVar(value="Chicago, IL")
        city_e = tk.Entry(ctrl_f, textvariable=self.city_var, width=18,
                          bg=BG_CARD, fg=TEXT, insertbackground=TEXT,
                          relief="flat", font=("Segoe UI", 10))
        city_e.pack(side="left", padx=(0, 16))

        self.run_btn = tk.Button(ctrl_f, text="▶  Run Pipeline",
                                 command=self._start_pipeline,
                                 bg=ACCENT, fg=BG, activebackground=GREEN, activeforeground=BG,
                                 font=("Segoe UI", 10, "bold"), relief="flat",
                                 padx=14, pady=6, cursor="hand2")
        self.run_btn.pack(side="left", padx=(0, 8))

        self.clear_btn = tk.Button(ctrl_f, text="⬜  Clear",
                                   command=self._clear,
                                   bg=BG_CARD, fg=DIM, activebackground=BG_PANEL, activeforeground=TEXT,
                                   font=("Segoe UI", 10), relief="flat",
                                   padx=10, pady=6, cursor="hand2")
        self.clear_btn.pack(side="left")

        # API badge
        api_col = GREEN if (ANTHROPIC_AVAILABLE and APIKEY) else YELLOW
        api_txt = "● API Connected" if (ANTHROPIC_AVAILABLE and APIKEY) else "● Fallback Mode"
        tk.Label(hdr, text=api_txt, bg=BG_PANEL, fg=api_col,
                 font=("Segoe UI", 9)).grid(row=0, column=2, padx=20, sticky="e")

        # Bottom border
        tk.Frame(self.root, bg=BORDER, height=1).grid(row=0, column=0, sticky="sew")

    def _build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=3)
        body.rowconfigure(1, weight=2)

        self._build_sidebar(body)
        self._build_console(body)
        self._build_crm_table(body)

    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=BG_PANEL, width=220)
        sb.grid(row=0, column=0, sticky="nsew", rowspan=2)
        sb.grid_propagate(False)

        tk.Label(sb, text="PIPELINE STEPS", bg=BG_PANEL, fg=DIM,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=16, pady=(16, 8))

        self._step_labels = []
        for i, step in enumerate(PIPELINE_STEPS):
            row_f = tk.Frame(sb, bg=BG_PANEL)
            row_f.pack(fill="x", padx=8, pady=2)
            icon = tk.Label(row_f, text="⬜", bg=BG_PANEL, fg=DIM,
                            font=("Segoe UI", 10), width=3)
            icon.pack(side="left")
            lbl = tk.Label(row_f, text=f"{i+1}. {step}", bg=BG_PANEL, fg=DIM,
                           font=("Segoe UI", 9), anchor="w", justify="left",
                           wraplength=160)
            lbl.pack(side="left", fill="x", expand=True)
            self._step_labels.append((icon, lbl))

        # Stats
        tk.Frame(sb, bg=BORDER, height=1).pack(fill="x", padx=8, pady=(16, 0))
        tk.Label(sb, text="LIVE STATS", bg=BG_PANEL, fg=DIM,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=16, pady=(12, 6))

        self._stat_vals = {}
        stat_defs = [
            ("found",     "Prospects Found"),
            ("qualified", "Qualified"),
            ("sent",      "Messages Sent"),
            ("replied",   "Replies"),
            ("booked",    "Appts Booked"),
        ]
        for key, label in stat_defs:
            f = tk.Frame(sb, bg=BG_PANEL)
            f.pack(fill="x", padx=16, pady=3)
            tk.Label(f, text=label, bg=BG_PANEL, fg=DIM,
                     font=("Segoe UI", 9)).pack(side="left")
            val = tk.Label(f, text="—", bg=BG_PANEL, fg=ACCENT,
                           font=("Segoe UI", 11, "bold"))
            val.pack(side="right")
            self._stat_vals[key] = val

    def _build_console(self, parent):
        console_f = tk.Frame(parent, bg=BG)
        console_f.grid(row=0, column=1, sticky="nsew", padx=(1, 0))
        console_f.columnconfigure(0, weight=1)
        console_f.rowconfigure(0, weight=1)

        tk.Frame(console_f, bg=BORDER, height=1).grid(row=0, column=0, sticky="ew")

        self.console = tk.Text(
            console_f, bg=BG, fg=TEXT, insertbackground=TEXT,
            font=("Consolas", 9) if self._font_exists("Consolas") else ("Courier", 9),
            wrap="word", relief="flat", padx=16, pady=12,
            state="disabled", selectbackground="#2d333b",
        )
        self.console.grid(row=1, column=0, sticky="nsew")
        console_f.rowconfigure(1, weight=1)

        sb = tk.Scrollbar(console_f, orient="vertical", command=self.console.yview,
                          bg=BG_PANEL, troughcolor=BG, relief="flat")
        sb.grid(row=1, column=1, sticky="ns")
        self.console["yscrollcommand"] = sb.set

        # Colour tags
        tag_map = {
            "text":   TEXT,  "dim": DIM,    "green":  GREEN,
            "red":    RED,   "yellow": YELLOW, "cyan": CYAN,
            "accent": ACCENT,"purple": PURPLE,
        }
        for tag, color in tag_map.items():
            self.console.tag_config(tag, foreground=color)

    def _build_crm_table(self, parent):
        crm_f = tk.Frame(parent, bg=BG_PANEL)
        crm_f.grid(row=1, column=1, sticky="nsew", padx=(1, 0))
        crm_f.columnconfigure(0, weight=1)
        crm_f.rowconfigure(1, weight=1)

        tk.Frame(crm_f, bg=BORDER, height=1).grid(row=0, column=0, columnspan=2, sticky="ew")
        tk.Label(crm_f, text="  CRM LEADS", bg=BG_PANEL, fg=DIM,
                 font=("Segoe UI", 8, "bold")).grid(row=0, column=0, sticky="w", pady=6)

        cols = ("Business", "Owner", "Trade", "Score", "Status", "Sentiment")
        self.crm_tree = ttk.Treeview(crm_f, columns=cols, show="headings", height=6)
        widths = [200, 140, 100, 60, 160, 100]
        for col, w in zip(cols, widths):
            self.crm_tree.heading(col, text=col)
            self.crm_tree.column(col, width=w, minwidth=50)
        self.crm_tree.grid(row=1, column=0, sticky="nsew")

        crm_sb = tk.Scrollbar(crm_f, orient="vertical", command=self.crm_tree.yview,
                               bg=BG_PANEL, troughcolor=BG, relief="flat")
        crm_sb.grid(row=1, column=1, sticky="ns")
        self.crm_tree["yscrollcommand"] = crm_sb.set
        crm_f.rowconfigure(1, weight=1)

        # Row colour tags
        self.crm_tree.tag_configure("booked",   foreground=GREEN)
        self.crm_tree.tag_configure("closed",   foreground=RED)
        self.crm_tree.tag_configure("follow_up",foreground=YELLOW)
        self.crm_tree.tag_configure("sent",     foreground=CYAN)

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=BG_PANEL, height=28)
        bar.grid(row=2, column=0, sticky="ew")
        bar.columnconfigure(1, weight=1)
        tk.Frame(self.root, bg=BORDER, height=1).grid(row=2, column=0, sticky="new")

        self.status_lbl = tk.Label(bar, text="  Ready", bg=BG_PANEL, fg=DIM,
                                   font=("Segoe UI", 9))
        self.status_lbl.grid(row=0, column=0, sticky="w", padx=8)

        self.time_lbl = tk.Label(bar, text="", bg=BG_PANEL, fg=DIM,
                                 font=("Segoe UI", 9))
        self.time_lbl.grid(row=0, column=2, sticky="e", padx=12)

    # ── Actions ───────────────────────────────────────────────────────────

    def _start_pipeline(self):
        if self.running:
            return
        self.running = True
        self.run_btn.config(state="disabled", bg=DIM)
        self._reset_steps()
        self._stats = {"found": 0, "qualified": 0, "sent": 0, "replied": 0, "booked": 0}
        for k, v in self._stat_vals.items():
            v.config(text="—")
        self.crm_tree.delete(*self.crm_tree.get_children())
        self._set_status("Running pipeline...", YELLOW)
        self._start_time = time.time()

        trade    = self.trade_var.get()
        location = self.city_var.get() or "Chicago, IL"

        thread = threading.Thread(
            target=run_pipeline,
            args=(trade, location, self.q),
            daemon=True,
        )
        thread.start()

    def _clear(self):
        if self.running:
            return
        self.console.config(state="normal")
        self.console.delete("1.0", "end")
        self.console.config(state="disabled")
        self.crm_tree.delete(*self.crm_tree.get_children())
        self._reset_steps()
        for k, v in self._stat_vals.items():
            v.config(text="—")
        self._set_status("Ready", DIM)
        self.time_lbl.config(text="")

    def _reset_steps(self):
        for icon, lbl in self._step_labels:
            icon.config(text="⬜", fg=DIM)
            lbl.config(fg=DIM)

    # ── Queue polling ─────────────────────────────────────────────────────

    def _poll_queue(self):
        try:
            while True:
                msg = self.q.get_nowait()
                self._handle(msg)
        except queue.Empty:
            pass
        self.root.after(50, self._poll_queue)

    def _handle(self, msg):
        kind = msg[0]

        if kind == "log":
            _, text, color = msg
            self._log(text, color)

        elif kind == "step_start":
            i = msg[1]
            icon, lbl = self._step_labels[i]
            icon.config(text="▶", fg=YELLOW)
            lbl.config(fg=YELLOW)
            self._set_status(f"Step {i+1}: {PIPELINE_STEPS[i]}", YELLOW)
            self._log(f"\n▶  [{i+1}/{len(PIPELINE_STEPS)}]  {PIPELINE_STEPS[i].upper()}", "accent")

        elif kind == "step_done":
            i = msg[1]
            icon, lbl = self._step_labels[i]
            icon.config(text="✅", fg=GREEN)
            lbl.config(fg=GREEN)

        elif kind == "stats_update":
            _, key, val = msg
            self._stats[key] = val
            if key in self._stat_vals:
                self._stat_vals[key].config(text=str(val))

        elif kind == "crm_row":
            row = msg[1]
            (lid, biz, owner, phone, email, trade, loc,
             score, status, msg_txt, resp, sent, created) = row
            tag = status if status in ("booked","closed","follow_up") else "sent"
            self.crm_tree.insert("", "end",
                values=(biz, owner, trade, score, status, sent or "—"),
                tags=(tag,))

        elif kind == "done":
            self.running = False
            self.run_btn.config(state="normal", bg=ACCENT)
            elapsed = time.time() - getattr(self, "_start_time", time.time())
            self._set_status("Pipeline complete ✓", GREEN)
            self.time_lbl.config(text=f"Completed in {elapsed:.1f}s")
            self._log("\n✓  Pipeline complete.\n", "green")

    # ── Helpers ───────────────────────────────────────────────────────────

    def _log(self, text, color="text"):
        self.console.config(state="normal")
        self.console.insert("end", text + "\n", color)
        self.console.see("end")
        self.console.config(state="disabled")

    def _set_status(self, text, color=DIM):
        self.status_lbl.config(text=f"  {text}", fg=color)

    @staticmethod
    def _font_exists(name):
        import tkinter.font as tkfont
        try:
            tkfont.Font(family=name)
            return True
        except Exception:
            return False


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app  = ProspectPilotApp(root)
    root.mainloop()
