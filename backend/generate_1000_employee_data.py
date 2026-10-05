import csv
import random
import uuid
from datetime import datetime, timedelta

# ============================================================
# CONFIGURATION
# ============================================================

NUM_EMPLOYEES = 1000
NUM_DAYS = 5

OUTPUT_FILE = "worker_1000_5day_afternoon_dataset.csv"

# Afternoon session
AFTERNOON_START_HOUR = 13
AFTERNOON_END_HOUR = 16

random.seed(42)

# ============================================================
# MASTER DATA
# ============================================================

departments = [
    "Production",
    "Assembly",
    "Quality",
    "Packaging",
    "Maintenance",
    "Stores",
    "Cutting",
    "Finishing"
]

workstations = [
    "WS-01",
    "WS-02",
    "WS-03",
    "WS-04",
    "WS-05",
    "WS-06",
    "WS-07",
    "WS-08",
    "WS-09",
    "WS-10"
]

feedback_values = [
    "HAPPY",
    "OK",
    "SAD"
]

SHIFT = "AFTERNOON"


# ============================================================
# HELPER
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


# ============================================================
# CREATE 1000 EMPLOYEES
# ============================================================

employees = []

for i in range(1, NUM_EMPLOYEES + 1):

    employee = {
        "employee_id": f"EMP{i:04d}",
        "employee_name": f"Worker_{i:04d}",
        "rfid_uid": f"RFID{i:06d}",

        "department": random.choice(
            departments
        ),

        "workstation": random.choice(
            workstations
        ),

        # Individual physiological baseline
        "base_hr": random.uniform(
            68,
            84
        ),

        "base_temp": random.uniform(
            36.20,
            36.80
        ),

        "base_spo2": random.uniform(
            97.0,
            99.0
        ),

        "base_gsr": random.uniform(
            0.15,
            0.40
        ),

        # Individual mood tendency
        "mood_tendency": random.uniform(
            0.10,
            0.60
        ),

        # Previous day's mood
        "previous_mood": None
    }

    employees.append(employee)


# ============================================================
# GENERATE MOOD
# ============================================================

def generate_mood(employee):

    tendency = employee["mood_tendency"]

    # Daily variation
    day_effect = random.uniform(
        -0.12,
        0.12
    )

    # Historical influence
    previous_effect = 0

    if employee["previous_mood"] == "SAD":
        previous_effect = 0.10

    elif employee["previous_mood"] == "HAPPY":
        previous_effect = -0.05

    negative_tendency = (
        tendency
        + day_effect
        + previous_effect
    )

    negative_tendency = clamp(
        negative_tendency,
        0.05,
        0.85
    )

    # Mood probability
    if negative_tendency < 0.25:

        weights = [
            0.70,   # HAPPY
            0.25,   # OK
            0.05    # SAD
        ]

    elif negative_tendency < 0.45:

        weights = [
            0.40,
            0.45,
            0.15
        ]

    elif negative_tendency < 0.65:

        weights = [
            0.20,
            0.50,
            0.30
        ]

    else:

        weights = [
            0.10,
            0.40,
            0.50
        ]

    return random.choices(
        feedback_values,
        weights=weights,
        k=1
    )[0]


# ============================================================
# GENERATE SENSOR DATA
# ============================================================

def generate_sensor_values(
    employee,
    mood
):

    if mood == "HAPPY":

        hr_effect = random.uniform(
            -4,
            2
        )

        temp_effect = random.uniform(
            -0.10,
            0.05
        )

        gsr_effect = random.uniform(
            -0.08,
            0.02
        )

        spo2_effect = random.uniform(
            -0.2,
            0.5
        )

    elif mood == "OK":

        hr_effect = random.uniform(
            -1,
            7
        )

        temp_effect = random.uniform(
            -0.03,
            0.12
        )

        gsr_effect = random.uniform(
            -0.02,
            0.10
        )

        spo2_effect = random.uniform(
            -0.5,
            0.2
        )

    else:

        hr_effect = random.uniform(
            5,
            18
        )

        temp_effect = random.uniform(
            0.05,
            0.30
        )

        gsr_effect = random.uniform(
            0.08,
            0.35
        )

        spo2_effect = random.uniform(
            -1.0,
            0
        )

    # --------------------------------------------------------
    # Heart Rate
    # --------------------------------------------------------

    heart_rate = (
        employee["base_hr"]
        + hr_effect
        + random.gauss(0, 3)
    )

    heart_rate = round(
        clamp(
            heart_rate,
            55,
            120
        ),
        1
    )

    # --------------------------------------------------------
    # Skin Temperature
    # --------------------------------------------------------

    skin_temperature = (
        employee["base_temp"]
        + temp_effect
        + random.gauss(0, 0.07)
    )

    skin_temperature = round(
        clamp(
            skin_temperature,
            35.7,
            37.8
        ),
        2
    )

    # --------------------------------------------------------
    # SpO2
    # --------------------------------------------------------

    spo2 = (
        employee["base_spo2"]
        + spo2_effect
        + random.gauss(0, 0.4)
    )

    spo2 = round(
        clamp(
            spo2,
            94,
            100
        ),
        1
    )

    # --------------------------------------------------------
    # GSR / EDA
    # --------------------------------------------------------

    gsr = (
        employee["base_gsr"]
        + gsr_effect
        + random.gauss(0, 0.035)
    )

    gsr = round(
        clamp(
            gsr,
            0.05,
            1.50
        ),
        3
    )

    return (
        heart_rate,
        skin_temperature,
        spo2,
        gsr
    )


# ============================================================
# SYNTHETIC RISK SCORE
# ============================================================

def calculate_risk(
    mood,
    heart_rate,
    skin_temperature,
    spo2,
    gsr,
    previous_mood
):

    score = 0

    # Mood
    if mood == "HAPPY":
        score += 10

    elif mood == "OK":
        score += 38

    else:
        score += 72

    # Heart rate
    if heart_rate > 100:
        score += 15

    elif heart_rate > 90:
        score += 8

    elif heart_rate > 85:
        score += 4

    # GSR
    if gsr > 0.80:
        score += 15

    elif gsr > 0.55:
        score += 9

    elif gsr > 0.40:
        score += 4

    # Skin temperature
    if skin_temperature > 37.2:
        score += 7

    elif skin_temperature > 37.0:
        score += 3

    # SpO2
    if spo2 < 95:
        score += 5

    elif spo2 < 96:
        score += 2

    # Historical mood
    if previous_mood == "SAD" and mood == "SAD":
        score += 8

    # Natural variation
    score += random.uniform(
        -5,
        5
    )

    score = round(
        clamp(
            score,
            0,
            100
        ),
        2
    )

    if score < 35:
        risk_level = "LOW"

    elif score < 65:
        risk_level = "MODERATE"

    else:
        risk_level = "HIGH"

    return score, risk_level


# ============================================================
# GENERATE 5 DAYS
# ============================================================

rows = []

start_date = (
    datetime.now().replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )
    - timedelta(days=4)
)


for day_number in range(NUM_DAYS):

    current_date = (
        start_date
        + timedelta(days=day_number)
    )

    print(
        f"Generating Day {day_number + 1}..."
    )

    for employee in employees:

        # ----------------------------------------------------
        # Afternoon timestamp
        # ----------------------------------------------------

        hour = random.randint(
            AFTERNOON_START_HOUR,
            AFTERNOON_END_HOUR
        )

        minute = random.randint(
            0,
            59
        )

        second = random.randint(
            0,
            59
        )

        timestamp = current_date.replace(
            hour=hour,
            minute=minute,
            second=second
        )

        # ----------------------------------------------------
        # Previous mood
        # ----------------------------------------------------

        previous_mood = employee[
            "previous_mood"
        ]

        # ----------------------------------------------------
        # Current mood
        # ----------------------------------------------------

        mood = generate_mood(
            employee
        )

        # ----------------------------------------------------
        # Sensor readings
        # ----------------------------------------------------

        (
            heart_rate,
            skin_temperature,
            spo2,
            gsr
        ) = generate_sensor_values(
            employee,
            mood
        )

        # ----------------------------------------------------
        # Risk
        # ----------------------------------------------------

        risk_score, risk_level = calculate_risk(
            mood,
            heart_rate,
            skin_temperature,
            spo2,
            gsr,
            previous_mood
        )

        # ----------------------------------------------------
        # Event ID
        # ----------------------------------------------------

        event_id = str(
            uuid.uuid4()
        )

        # ----------------------------------------------------
        # Create record
        # ----------------------------------------------------

        row = {

            "event_id":
                event_id,

            "employee_id":
                employee["employee_id"],

            "employee_name":
                employee["employee_name"],

            "rfid_uid":
                employee["rfid_uid"],

            "department":
                employee["department"],

            "workstation":
                employee["workstation"],

            "shift":
                SHIFT,

            "day_number":
                day_number + 1,

            "timestamp":
                timestamp.isoformat(),

            "feedback":
                mood,

            "previous_feedback":
                previous_mood,

            "skin_temperature":
                skin_temperature,

            "heart_rate":
                heart_rate,

            "spo2":
                spo2,

            "gsr":
                gsr,

            "risk_score":
                risk_score,

            "risk_level":
                risk_level
        }

        rows.append(row)

        # ----------------------------------------------------
        # Save current mood for next day
        # ----------------------------------------------------

        employee[
            "previous_mood"
        ] = mood


# ============================================================
# SORT BY TIMESTAMP
# ============================================================

rows.sort(
    key=lambda row:
        row["timestamp"]
)


# ============================================================
# SAVE CSV
# ============================================================

fieldnames = [
    "event_id",
    "employee_id",
    "employee_name",
    "rfid_uid",
    "department",
    "workstation",
    "shift",
    "day_number",
    "timestamp",
    "feedback",
    "previous_feedback",
    "skin_temperature",
    "heart_rate",
    "spo2",
    "gsr",
    "risk_score",
    "risk_level"
]


with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(rows)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 65)
print("1000 EMPLOYEE AIoT SYNTHETIC DATASET")
print("=" * 65)

print(
    f"Employees       : {NUM_EMPLOYEES}"
)

print(
    f"Days            : {NUM_DAYS}"
)

print(
    f"Total records   : {len(rows)}"
)

print(
    "Session         : AFTERNOON"
)

print(
    f"Output          : {OUTPUT_FILE}"
)


# ============================================================
# MOOD DISTRIBUTION
# ============================================================

print()
print("MOOD DISTRIBUTION")
print("-" * 40)

for mood in feedback_values:

    count = sum(
        1
        for row in rows
        if row["feedback"] == mood
    )

    percentage = (
        count / len(rows)
    ) * 100

    print(
        f"{mood:<10} "
        f"{count:>5} "
        f"({percentage:>5.1f}%)"
    )


# ============================================================
# RISK DISTRIBUTION
# ============================================================

print()
print("RISK DISTRIBUTION")
print("-" * 40)

for risk in [
    "LOW",
    "MODERATE",
    "HIGH"
]:

    count = sum(
        1
        for row in rows
        if row["risk_level"] == risk
    )

    percentage = (
        count / len(rows)
    ) * 100

    print(
        f"{risk:<10} "
        f"{count:>5} "
        f"({percentage:>5.1f}%)"
    )


print()
print("=" * 65)
print("GENERATION COMPLETE")
print("=" * 65)
