import streamlit as st
import requests
from datetime import datetime, time
from time import sleep

st.set_page_config(page_title="AAA REAL ID Checker", layout="centered", page_icon="📅")

# === Custom CSS ===
st.markdown("""
<style>
    /* Hide Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Header */
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
        margin-bottom: 2rem;
    }
    .subheader a {
        color: #667eea;
        text-decoration: none;
        font-weight: 500;
    }
    .subheader a:hover {
        text-decoration: underline;
    }
    
    /* Location cards */
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
    .date-group {
        margin-top: 10px;
    }
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
    
    /* Sidebar tweaks */
    section[data-testid="stSidebar"] {
        background: #fafbfc;
    }
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

# === Sidebar ===
with st.sidebar:
    st.markdown("### ⚙️ Filters")
    
    days_to_check = st.slider("Days ahead", 1, 60, 30)
    
    st.markdown("---")
    st.markdown("**📍 Locations**")
    
    # Preset location groups
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
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("**📆 Day of week**")
    days_of_week = st.multiselect(
        "Days",
        options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("**🕒 Time window**")
    col_a, col_b = st.columns(2)
    with col_a:
        start_hour = st.selectbox("From", list(range(7, 20)), index=1, format_func=lambda h: f"{h%12 or 12} {'AM' if h<12 else 'PM'}")
    with col_b:
        end_hour = st.selectbox("To", list(range(8, 21)), index=10, format_func=lambda h: f"{h%12 or 12} {'AM' if h<12 else 'PM'}")
    
    st.markdown("---")
    hide_empty = st.checkbox("Hide locations with no slots", value=True)
    sort_by = st.radio("Sort by", ["Most slots first", "Alphabetical"], horizontal=False)

# === Filter ===
def slot_matches_filters(dt):
    if dt.strftime("%A") not in days_of_week:
        return False
    if dt.hour < start_hour or dt.hour >= end_hour:
        return False
    return True

# === Run ===
run = st.button("🔍 Check Availability", use_container_width=True, type="primary")

if run:
    if not selected_locations:
        st.warning("Please select at least one location in the sidebar.")
    else:
        start_date = datetime.now().strftime("%Y-%m-%d")
        results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, location in enumerate(selected_locations):
            calendar_id = locations[location]
            status_text.caption(f"Checking {location}... ({i+1}/{len(selected_locations)})")
            progress_bar.progress((i + 1) / len(selected_locations))
            
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
                                if slot_matches_filters(dt):
                                    slot_datetimes.append(dt)
                            except:
                                continue
                
                results.append({"location": location, "slots": sorted(slot_datetimes)})
            except Exception as e:
                results.append({"location": location, "slots": [], "error": str(e)})
            sleep(0.5)
        
        progress_bar.empty()
        status_text.empty()
        
        if sort_by == "Most slots first":
            results.sort(key=lambda x: -len(x["slots"]))
        else:
            results.sort(key=lambda x: x["location"])
        
        # === Summary ===
        total_slots = sum(len(r["slots"]) for r in results)
        locations_with_slots = sum(1 for r in results if r["slots"])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total slots", total_slots)
        m2.metric("Locations available", f"{locations_with_slots}/{len(results)}")
        m3.metric("Days checked", days_to_check)
        
        st.markdown("")
        
        # === Results ===
        for r in results:
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
            st.info("No slots found matching your filters. Try widening your time window or adding more days.")
