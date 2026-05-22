import streamlit as st
import requests
from datetime import datetime, time
from time import sleep
import pandas as pd

st.set_page_config(page_title="AAA REAL ID Checker", layout="wide", page_icon="📅")

# === Custom CSS ===
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .location-card {
        padding: 16px;
        margin-bottom: 12px;
        border-radius: 12px;
        background: linear-gradient(135deg, #f5f7fa 0%, #e8edf5 100%);
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .location-card-empty {
        padding: 12px 16px;
        margin-bottom: 8px;
        border-radius: 8px;
        background: #fafafa;
        color: #999;
        border-left: 4px solid #ddd;
    }
    .slot-chip {
        display: inline-block;
        padding: 6px 12px;
        margin: 4px 4px 4px 0;
        background: white;
        border: 1px solid #d0d7e2;
        border-radius: 20px;
        font-size: 13px;
        color: #2d3748;
    }
    .location-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 8px;
    }
    .slot-count {
        background: #667eea;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📅 AAA REAL ID Appointment Checker</div>', unsafe_allow_html=True)
st.markdown(
    "[🔗 Book via official AAA site](https://northeast.aaa.com/automotive/registry-services/schedule-rmv.html)",
    unsafe_allow_html=True
)

# === Location & Calendar IDs ===
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

# === Constants ===
base_url = "https://app.acuityscheduling.com/api/scheduling/v1/availability/times"
appointment_type_id = 13578181
owner_id = "d0ad1034"
timezone = "America/New_York"

# === Sidebar Filters ===
with st.sidebar:
    st.header("🎛️ Filters")
    
    days_to_check = st.slider("Days to check ahead", 1, 60, 30)
    
    st.subheader("📍 Locations")
    select_all = st.checkbox("Select all locations", value=True)
    if select_all:
        selected_locations = st.multiselect(
            "Choose locations",
            options=list(locations.keys()),
            default=list(locations.keys())
        )
    else:
        selected_locations = st.multiselect(
            "Choose locations",
            options=list(locations.keys()),
            default=[]
        )
    
    st.subheader("📆 Day of Week")
    days_of_week = st.multiselect(
        "Filter by day",
        options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    )
    
    st.subheader("🕒 Time of Day")
    time_range = st.slider(
        "Time window",
        min_value=time(7, 0),
        max_value=time(20, 0),
        value=(time(8, 0), time(18, 0)),
        step=pd.Timedelta(minutes=30).to_pytimedelta(),
        format="hh:mm A"
    )
    
    st.subheader("🎯 Display")
    hide_empty = st.checkbox("Hide locations with no slots", value=False)
    sort_by = st.radio("Sort locations by", ["Most slots first", "Alphabetical"])

# === Filter Functions ===
def slot_matches_filters(dt):
    if dt.strftime("%A") not in days_of_week:
        return False
    slot_time = dt.time()
    if slot_time < time_range[0] or slot_time > time_range[1]:
        return False
    return True

# === Run Button ===
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    run = st.button("🔍 Check Appointment Availability", use_container_width=True, type="primary")

if run:
    if not selected_locations:
        st.warning("Please select at least one location.")
    else:
        start_date = datetime.now().strftime("%Y-%m-%d")
        results = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, location in enumerate(selected_locations):
            calendar_id = locations[location]
            status_text.text(f"Checking {location}... ({i+1}/{len(selected_locations)})")
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
        
        # Sort results
        if sort_by == "Most slots first":
            results.sort(key=lambda x: -len(x["slots"]))
        else:
            results.sort(key=lambda x: x["location"])
        
        # === Summary Stats ===
        total_slots = sum(len(r["slots"]) for r in results)
        locations_with_slots = sum(1 for r in results if r["slots"])
        
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Slots Found", total_slots)
        m2.metric("Locations with Availability", f"{locations_with_slots} / {len(results)}")
        m3.metric("Days Checked", days_to_check)
        st.markdown("---")
        
        # === Display Results ===
        for r in results:
            location = r["location"]
            slots = r["slots"]
            
            if slots:
                # Group slots by date for cleaner display
                slots_by_date = {}
                for dt in slots:
                    date_key = dt.strftime("%A, %B %d")
                    slots_by_date.setdefault(date_key, []).append(dt.strftime("%I:%M %p"))
                
                slots_html = ""
                for date_key, times in slots_by_date.items():
                    chips = "".join(f'<span class="slot-chip">{t}</span>' for t in times)
                    slots_html += f'<div style="margin-top:8px;"><strong style="color:#4a5568;font-size:13px;">{date_key}</strong><br>{chips}</div>'
                
                st.markdown(f"""
                    <div class="location-card">
                        <div class="location-name">
                            ✅ {location}
                            <span class="slot-count">{len(slots)} slots</span>
                        </div>
                        {slots_html}
                    </div>
                """, unsafe_allow_html=True)
            elif not hide_empty:
                st.markdown(
                    f'<div class="location-card-empty">❌ {location} — no matching slots</div>',
                    unsafe_allow_html=True
                )
