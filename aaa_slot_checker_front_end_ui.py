import streamlit as st
import requests
from datetime import datetime
from time import sleep

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
    .slot-count {
        background: #ebf4ff;
        color: #4c51bf;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
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

# === Locations ===
locations = {
    "AAA Quincy": 3714482, "AAA Boston": 3697037, "AAA Westwood": 3720293,
    "AAA Rockland": 3714492, "AAA Newton": 3701021, "AAA Saugus": 3716284,
    "AAA Waltham": 3720288, "AAA Burlington": 3697053, "AAA Framingham": 3697096,
    "AAA Franklin": 3697104, "AAA Acton": 3696926, "AAA Auburn": 3697026,
    "AAA Fairhaven": 3697064, "AAA Hadley": 5213046, "AAA Haverhill": 3697140,
    "AAA Leominster": 3697159, "AAA Lowell": 3697182, "AAA Marlborough": 3701015,
    "AAA Newburyport": 3701020, "AAA North Andover": 3701023, "AAA North Reading": 3701024,
    "AAA Peabody": 3701031, "AAA Pittsfield": 3706864, "AAA Plymouth": 3706872,
    "AAA Raynham": 3714489, "AAA Somerset": 3720214, "AAA South Attleboro": 3696961,
    "AAA South Dennis": 3720244, "AAA Springfield": 5361913, "AAA Tewksbury": 3720249,
    "AAA Webster": 3720290, "AAA West Springfield": 5365483, "AAA Worcester": 3720298,
}

base_url = "https://app.acuityscheduling.com/api/scheduling/v1/availability/times"
appointment_type_id = 13578181
owner_id = "d0ad1034"
timezone = "America/New_York"

# === Initialize session state ===
if "raw_results" not in st.session_state:
    st.session_state.raw_results = None
if "search_timestamp" not in st.session_state:
    st.session_state.search_timestamp = None
if "searched_days" not in st.session_state:
    st.session_state.searched_days = None

# === Search function ===
def fetch_all_slots(days_to_check):
    """Fetch ALL slots for ALL locations — no filtering, just raw data."""
    start_date = datetime.now().strftime("%Y-%m-%d")
    results = {}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    location_items = list(locations.items())
    for i, (location, calendar_id) in enumerate(location_items):
        status_text.caption(f"Fetching {location}... ({i+1}/{len(location_items)})")
        progress_bar.progress((i + 1) / len(location_items))
        
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
        except Exception as e:
            results[location] = []
        sleep(0.5)
    
    progress_bar.empty()
    status_text.empty()
    return results

# === Sidebar: SEARCH controls ===
with st.sidebar:
    st.markdown("### 🔎 Search")
    days_to_check = st.slider("Days ahead to fetch", 1, 60, 30, 
                               help="Larger ranges take longer. Re-run search if you change this.")
    
    search_clicked = st.button("🔄 Run Search", use_container_width=True, type="primary")
    
    if st.session_state.raw_results is not None:
        st.caption(f"✓ Cached at {st.session_state.search_timestamp.strftime('%I:%M %p')} • {st.session_state.searched_days}d window")
    
    st.markdown("---")
    st.markdown("### 🎛️ Filters")
    st.caption("Adjust these freely — no re-search needed.")
    
    # Location preset
    preset = st.selectbox(
        "Quick select",
        ["All locations", "Greater Boston", "North Shore", "South Shore", "Western MA", "Custom"],
        index=0
    )
    presets_map = {
        "All locations": list(locations.keys()),
        "Greater Boston": ["AAA Boston", "AAA Newton", "AAA Waltham", "AAA Quincy", "AAA Westwood"],
        "North Shore": ["AAA Saugus", "AAA Peabody", "AAA Newburyport", "AAA North Andover", "AAA North Reading", "AAA Haverhill"],
        "South Shore": ["AAA Quincy", "AAA Rockland", "AAA Plymouth", "AAA Raynham", "AAA South Attleboro"],
        "Western MA": ["AAA Hadley", "AAA Springfield", "AAA West Springfield", "AAA Pittsfield"],
        "Custom": [],
    }
    default_locs = presets_map[preset] if preset != "Custom" else []
    selected_locations = st.multiselect(
        "Locations",
        options=list(locations.keys()),
        default=default_locs,
    )
    
    days_of_week = st.multiselect(
        "Day of week",
        options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    )
    
    col_a, col_b = st.columns(2)
    with col_a:
        start_hour = st.selectbox("From", list(range(7, 20)), index=1, 
                                   format_func=lambda h: f"{h%12 or 12} {'AM' if h<12 else 'PM'}")
    with col_b:
        end_hour = st.selectbox("To", list(range(8, 21)), index=10, 
                                 format_func=lambda h: f"{h%12 or 12} {'AM' if h<12 else 'PM'}")
    
    hide_empty = st.checkbox("Hide locations with no slots", value=True)
    sort_by = st.radio("Sort by", ["Most slots first", "Alphabetical"])

# === Handle search ===
if search_clicked:
    with st.spinner("Fetching all locations..."):
        st.session_state.raw_results = fetch_all_slots(days_to_check)
        st.session_state.search_timestamp = datetime.now()
        st.session_state.searched_days = days_to_check
    st.rerun()

# === Filter function (applied to cached data) ===
def slot_matches_filters(dt):
    if dt.strftime("%A") not in days_of_week:
        return False
    if dt.hour < start_hour or dt.hour >= end_hour:
        return False
    return True

# === Display ===
if st.session_state.raw_results is None:
    st.info("👈 Click **Run Search** in the sidebar to fetch appointment data. Once fetched, you can adjust filters instantly without re-searching.")
else:
    # Apply filters to cached raw data
    filtered = []
    for location in selected_locations:
        raw_slots = st.session_state.raw_results.get(location, [])
        filtered_slots = [dt for dt in raw_slots if slot_matches_filters(dt)]
        filtered.append({"location": location, "slots": filtered_slots})
    
    # Sort
    if sort_by == "Most slots first":
        filtered.sort(key=lambda x: -len(x["slots"]))
    else:
        filtered.sort(key=lambda x: x["location"])
    
    # Cache notice
    st.markdown(
        f'<div class="cache-info">⚡ Showing cached results from {st.session_state.search_timestamp.strftime("%I:%M %p")}. '
        f'Filters apply instantly. Run a new search to refresh data.</div>',
        unsafe_allow_html=True
    )
    
    if not selected_locations:
        st.warning("Select at least one location in the sidebar.")
    else:
        # Summary
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
                            <span>{location}</span>
                            <span class="slot-count">{len(slots)} slots</span>
                        </div>
                        {slots_html}
                    </div>
                """, unsafe_allow_html=True)
            elif not hide_empty:
                st.markdown(
                    f'<div class="location-card-empty">— {location}</div>',
                    unsafe_allow_html=True
                )
        
        if total_slots == 0:
            st.info("No slots match your current filters. Try widening the time window, adding more days of the week, or selecting more locations.")
