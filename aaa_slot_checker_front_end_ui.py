import streamlit as st
import requests
from datetime import datetime
from time import sleep
import math

st.set_page_config(page_title="AAA REAL ID Checker", layout="centered", page_icon="📅")

# === Custom CSS ===
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }
    .subheader {
        color: #718096;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .subheader a {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
    }
    .subheader a:hover { text-decoration: underline; }
    
    .location-card {
        padding: 18px 20px;
        margin-bottom: 14px;
        border-radius: 10px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 3px solid #48bb78;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .location-card-empty {
        padding: 12px 20px;
        margin-bottom: 8px;
        border-radius: 8px;
        background: #fafafa;
        color: #a0aec0;
        border: 1px solid #edf2f7;
        font-size: 14px;
    }
    .location-name {
        font-size: 1.05rem;
        font-weight: 600;
        color: #2d3748;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .location-meta {
        font-size: 12px;
        color: #a0aec0;
        font-weight: 400;
        margin-left: 8px;
    }
    .slot-count {
        background: #ebf4ff;
        color: #4c51bf;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        white-space: nowrap;
    }
    .date-group { margin-top: 10px; }
    .date-label {
        color: #4a5568;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .slot-chip {
        display: inline-block;
        padding: 5px 11px;
        margin: 3px 4px 3px 0;
        background: #f7fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        font-size: 13px;
        color: #2d3748;
        font-variant-numeric: tabular-nums;
    }
    .cache-info {
        background: #f0fff4;
        border: 1px solid #c6f6d5;
        color: #22543d;
        padding: 8px 14px;
        border-radius: 6px;
        font-size: 13px;
        margin-bottom: 12px;
    }
    section[data-testid="stSidebar"] { background: #fafbfc; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📅 AAA REAL ID Checker</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subheader">Find available REAL ID appointments across MA. '
    '<a href="https://northeast.aaa.com/automotive/registry-services/schedule-rmv.html" target="_blank">Book on AAA →</a></div>',
    unsafe_allow_html=True
)

# === Locations with coordinates ===
locations = {
    "AAA Quincy":           (3714482, 42.2529, -71.0023),
    "AAA Boston":           (3697037, 42.3601, -71.0589),
    "AAA Westwood":         (3720293, 42.2154, -71.2134),
    "AAA Rockland":         (3714492, 42.1334, -70.9162),
    "AAA Newton":           (3701021, 42.3370, -71.2092),
    "AAA Saugus":           (3716284, 42.4765, -71.0120),
    "AAA Waltham":          (3720288, 42.3765, -71.2356),
    "AAA Burlington":       (3697053, 42.5048, -71.1956),
    "AAA Framingham":       (3697096, 42.2793, -71.4162),
    "AAA Franklin":         (3697104, 42.0834, -71.3967),
    "AAA Acton":            (3696926, 42.4851, -71.4328),
    "AAA Auburn":           (3697026, 42.1945, -71.8354),
    "AAA Fairhaven":        (3697064, 41.6384, -70.9034),
    "AAA Hadley":           (5213046, 42.3626, -72.5712),
    "AAA Haverhill":        (3697140, 42.7762, -71.0773),
    "AAA Leominster":       (3697159, 42.5251, -71.7598),
    "AAA Lowell":           (3697182, 42.6334, -71.3162),
    "AAA Marlborough":      (3701015, 42.3459, -71.5523),
    "AAA Newburyport":      (3701020, 42.8126, -70.8773),
    "AAA North Andover":    (3701023, 42.6987, -71.1320),
    "AAA North Reading":    (3701024, 42.5751, -71.0784),
    "AAA Peabody":          (3701031, 42.5279, -70.9689),
    "AAA Pittsfield":       (3706864, 42.4501, -73.2454),
    "AAA Plymouth":         (3706872, 41.9584, -70.6673),
    "AAA Raynham":          (3714489, 41.9362, -71.0495),
    "AAA Somerset":         (3720214, 41.7418, -71.1523),
    "AAA South Attleboro":  (3696961, 41.9334, -71.5273),
    "AAA South Dennis":     (3720244, 41.6934, -70.1584),
    "AAA Springfield":      (5361913, 42.1015, -72.5898),
    "AAA Tewksbury":        (3720249, 42.6112, -71.2345),
    "AAA Webster":          (3720290, 42.0509, -71.8773),
    "AAA West Springfield": (5365483, 42.1037, -72.6398),
    "AAA Worcester":        (3720298, 42.2626, -71.8023),
}

location_ids   = {k: v[0] for k, v in locations.items()}
location_coords = {k: (v[1], v[2]) for k, v in locations.items()}

base_url = "https://app.acuityscheduling.com/api/scheduling/v1/availability/times"
appointment_type_id = 13578181
owner_id = "d0ad1034"
timezone = "America/New_York"

# === Haversine distance ===
def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8  # miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# === Initialize session state ===
if "raw_results" not in st.session_state:
    st.session_state.raw_results = None
if "search_timestamp" not in st.session_state:
    st.session_state.search_timestamp = None
if "searched_days" not in st.session_state:
    st.session_state.searched_days = None

# === Search function ===
def fetch_all_slots(days_to_check):
    start_date = datetime.now().strftime("%Y-%m-%d")
    results = {}
    progress_bar = st.progress(0)
    status_text = st.empty()
    items = list(location_ids.items())
    for i, (location, calendar_id) in enumerate(items):
        status_text.caption(f"Fetching {location}... ({i+1}/{len(items)})")
        progress_bar.progress((i + 1) / len(items))
        params = {
            "owner": owner_id,
            "appointmentTypeId": appointment_type_id,
            "calendarId": calendar_id,
            "startDate": start_date,
            "maxDays": days_to_check,
            "timezone": timezone,
        }
        try:
            response = requests.get(base_url, params=params)
            data = response.json()
            slot_datetimes = []
            if isinstance(data, dict):
                for date, slots in data.items():
                    for slot in slots:
                        try:
                            dt = datetime.fromisoformat(slot["time"])
                            slot_datetimes.append(dt)
                        except:
                            continue
            results[location] = sorted(slot_datetimes)
        except:
            results[location] = []
        sleep(0.5)
    progress_bar.empty()
    status_text.empty()
    return results

# === Sidebar ===
with st.sidebar:
    st.markdown("### 🔎 Search")
    days_to_check = st.slider("Days ahead to fetch", 1, 60, 30,
                               help="Larger ranges take longer. Re-run search if you change this.")
    search_clicked = st.button("🔄 Run Search", use_container_width=True, type="primary")
    if st.session_state.raw_results is not None:
        st.caption(f"✓ Cached at {st.session_state.search_timestamp.strftime('%I:%M %p')} • {st.session_state.searched_days}d window")

    st.markdown("---")
    st.markdown("### 🎛️ Filters")
    st.caption("Empty = show all. Add filters to narrow down.")

    preset = st.selectbox(
        "Quick select",
        ["All locations", "Greater Boston", "North Shore", "South Shore", "Western MA", "Custom"],
        index=0
    )
    presets_map = {
        "All locations": [],
        "Greater Boston": ["AAA Boston", "AAA Newton", "AAA Waltham", "AAA Quincy", "AAA Westwood"],
        "North Shore": ["AAA Saugus", "AAA Peabody", "AAA Newburyport", "AAA North Andover", "AAA North Reading", "AAA Haverhill"],
        "South Shore": ["AAA Quincy", "AAA Rockland", "AAA Plymouth", "AAA Raynham", "AAA South Attleboro"],
        "Western MA": ["AAA Hadley", "AAA Springfield", "AAA West Springfield", "AAA Pittsfield"],
        "Custom": [],
    }
    selected_locations = st.multiselect(
        "Locations (leave empty for all)",
        options=list(location_ids.keys()),
        default=presets_map[preset],
        placeholder="All locations",
    )

    days_of_week = st.multiselect(
        "Day of week (leave empty for all)",
        options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        default=[],
        placeholder="Any day",
    )

    col_a, col_b = st.columns(2)
    with col_a:
        start_hour = st.selectbox("From", list(range(7, 20)), index=1,
                                   format_func=lambda h: f"{h%12 or 12} {'AM' if h<12 else 'PM'}")
    with col_b:
        end_hour = st.selectbox("To", list(range(8, 21)), index=10,
                                 format_func=lambda h: f"{h%12 or 12} {'AM' if h<12 else 'PM'}")

    hide_empty = st.checkbox("Hide locations with no slots", value=True)

    st.markdown("---")
    st.markdown("### 📊 Sort")
    sort_by = st.radio(
        "Sort by",
        ["Soonest appointment", "Most slots", "Closest to me", "Alphabetical"],
        index=0
    )

    user_zip = None
    user_lat, user_lon = None, None
    if sort_by == "Closest to me":
        user_zip = st.text_input("Your ZIP code", placeholder="e.g. 02101")
        if user_zip and len(user_zip) == 5 and user_zip.isdigit():
            # Rough ZIP → lat/lon using a free API
            try:
                r = requests.get(f"https://api.zippopotam.us/us/{user_zip}", timeout=3)
                if r.status_code == 200:
                    zdata = r.json()
                    user_lat = float(zdata["places"][0]["latitude"])
                    user_lon = float(zdata["places"][0]["longitude"])
                    st.caption(f"📍 {zdata['places'][0]['place name']}, {zdata['places'][0]['state abbreviation']}")
                else:
                    st.caption("⚠️ ZIP not found")
            except:
                st.caption("⚠️ Could not look up ZIP")

# === Handle search ===
if search_clicked:
    with st.spinner("Fetching all locations..."):
        st.session_state.raw_results = fetch_all_slots(days_to_check)
        st.session_state.search_timestamp = datetime.now()
        st.session_state.searched_days = days_to_check
    st.rerun()

# === Filter function ===
def slot_matches_filters(dt):
    if days_of_week and dt.strftime("%A") not in days_of_week:
        return False
    if dt.hour < start_hour or dt.hour >= end_hour:
        return False
    return True

# === Display ===
if st.session_state.raw_results is None:
    st.info("👈 Click **Run Search** in the sidebar to fetch appointment data. Once fetched, you can adjust filters instantly without re-searching.")
else:
    locations_to_show = selected_locations if selected_locations else list(location_ids.keys())

    filtered = []
    for location in locations_to_show:
        raw_slots = st.session_state.raw_results.get(location, [])
        filtered_slots = [dt for dt in raw_slots if slot_matches_filters(dt)]
        lat, lon = location_coords[location]
        dist = haversine(user_lat, user_lon, lat, lon) if (user_lat and user_lon) else None
        filtered.append({
            "location": location,
            "slots": filtered_slots,
            "soonest": filtered_slots[0] if filtered_slots else None,
            "distance": dist,
        })

    # === Sort ===
    if sort_by == "Soonest appointment":
        filtered.sort(key=lambda x: (x["soonest"] is None, x["soonest"] or datetime.max))
    elif sort_by == "Most slots":
        filtered.sort(key=lambda x: -len(x["slots"]))
    elif sort_by == "Closest to me":
        if user_lat and user_lon:
            filtered.sort(key=lambda x: (x["distance"] is None, x["distance"] or 9999))
        else:
            st.warning("Enter your ZIP code above to sort by distance.")
    else:
        filtered.sort(key=lambda x: x["location"])

    # Cache notice
    st.markdown(
        f'<div class="cache-info">⚡ Showing cached results from {st.session_state.search_timestamp.strftime("%I:%M %p")}. '
        f'Filters apply instantly. Run a new search to refresh data.</div>',
        unsafe_allow_html=True
    )

    # Summary metrics
    total_slots = sum(len(r["slots"]) for r in filtered)
    locations_with_slots = sum(1 for r in filtered if r["slots"])
    m1, m2, m3 = st.columns(3)
    m1.metric("Matching slots", total_slots)
    m2.metric("Locations available", f"{locations_with_slots}/{len(filtered)}")
    m3.metric("Days fetched", st.session_state.searched_days)
    st.markdown("")

    # Results
    for r in filtered:
        location = r["location"]
        slots = r["slots"]
        dist = r["distance"]

        dist_str = f" · {dist:.1f} mi away" if dist is not None else ""

        if slots:
            slots_by_date = {}
            for dt in slots:
                date_key = dt.strftime("%a, %b %d")
                slots_by_date.setdefault(date_key, []).append(dt.strftime("%-I:%M %p"))

            slots_html = ""
            for date_key, times in slots_by_date.items():
                chips = "".join(f'<span class="slot-chip">{t}</span>' for t in times)
                slots_html += f'<div class="date-group"><div class="date-label">{date_key}</div>{chips}</div>'

            st.markdown(f"""
                <div class="location-card">
                    <div class="location-name">
                        <span>{location}<span class="location-meta">{dist_str}</span></span>
                        <span class="slot-count">{len(slots)} slots</span>
                    </div>
                    {slots_html}
                </div>
            """, unsafe_allow_html=True)
        elif not hide_empty:
            st.markdown(
                f'<div class="location-card-empty">— {location}{dist_str}</div>',
                unsafe_allow_html=True
            )

    if total_slots == 0:
        st.info("No slots match your current filters. Try widening the time window, adding more days, or clearing the location filter.")
