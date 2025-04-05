import streamlit as st
import requests
from datetime import datetime
from time import sleep

st.set_page_config(page_title="AAA REAL ID Checker", layout="centered")
st.title("📅 AAA REAL ID Appointment Checker")

# === Location & Calendar IDs ===
locations = {
    "AAA Quincy": 3714482,
    "AAA Boston": 3697037,
    "AAA Westwood": 3720293,
    "AAA Rockland": 3714492,
    "AAA Newton": 3701021,
    "AAA Saugus": 3716284,
    "AAA Waltham": 3720288,
    "AAA Burlington": 3697053,
    "AAA Framingham": 3697096,
    "AAA Franklin": 3697104,
    "AAA Acton": 3696926,
    "AAA Auburn": 3697026,
    "AAA Fairhaven": 3697064,
    "AAA Hadley": 5213046,
    "AAA Haverhill": 3697140,
    "AAA Leominster": 3697159,
    "AAA Lowell": 3697182,
    "AAA Marlborough": 3701015,
    "AAA Newburyport": 3701020,
    "AAA North Andover": 3701023,
    "AAA North Reading": 3701024,
    "AAA Peabody": 3701031,
    "AAA Pittsfield": 3706864,
    "AAA Plymouth": 3706872,
    "AAA Raynham": 3714489,
    "AAA Somerset": 3720214,
    "AAA South Attleboro": 3696961,
    "AAA South Dennis": 3720244,
    "AAA Springfield": 5361913,
    "AAA Tewksbury": 3720249,
    "AAA Webster": 3720290,
    "AAA West Springfield": 5365483,
    "AAA Worcester": 3720298,
}

# === Constants ===
base_url = "https://app.acuityscheduling.com/api/scheduling/v1/availability/times"
appointment_type_id = 13578181
owner_id = "d0ad1034"
timezone = "America/New_York"
days_to_check = 30

# === Run Button ===
if st.button("🔍 Check Appointment Availability"):
    start_date = datetime.now().strftime("%Y-%m-%d")
    with st.spinner("Checking all locations..."):
        for location, calendar_id in locations.items():
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

                slot_times = []

                # The new format is a dict where keys are dates
                if isinstance(data, dict):
                    for date, slots in data.items():
                        for slot in slots:
                            try:
                                dt = datetime.fromisoformat(slot["time"])
                                slot_times.append(f"🕒 {dt.strftime('%A, %B %d at %I:%M %p')}")
                            except:
                                continue

                if slot_times:
                    formatted = "<br>".join(slot_times)
                    st.markdown(
                        f"""
                        <div style='padding: 12px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 8px; background-color: #f9f9f9;'>
                            <h5 style='margin-bottom: 6px;'>✅ {location}</h5>
                            <div style='font-size: 14px; color: #333;'>{formatted}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<div style='padding: 8px; margin-bottom: 6px; color: #888;'>❌ {location}</div>",
                        unsafe_allow_html=True
                    )

            except Exception as e:
                st.warning(f"⚠️ Error checking {location}: {e}")

            sleep(0.5)
