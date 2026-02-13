import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(42)  # For reproducibility

# --- CONFIGURATION ---
NUM_PROJECTS = 5
START_DATE_RANGE = (datetime(2023, 1, 1), datetime(2023, 6, 1))

# HVAC Specific Terminology
hvac_tasks = [
    "Install RTU-1", "Ductwork Rough-in Level 1", "Ductwork Rough-in Level 2",
    "VRF System Piping", "VAV Box Installation", "Diffuser Mounting",
    "Chiller Pad Pour", "Thermostat Wiring", "System Commissioning", "Testing & Balancing"
]

materials = [
    "Galvanized Sheet Metal (lbs)", "Flex Duct (ft)", "Copper Piping 3/4 (ft)",
    "Refrigerant R-410A (lbs)", "VAV Units (ea)", "Hangers & Struts (box)"
]

# --- 1. PROJECTS & BID ASSUMPTIONS ---
projects = []
for i in range(1, NUM_PROJECTS + 1):
    start_date = fake.date_between(start_date=START_DATE_RANGE[0], end_date=START_DATE_RANGE[1])
    duration = random.randint(60, 180)
    end_date = start_date + timedelta(days=duration)
    
    contract_val = random.randint(50000, 2000000)
    margin = random.uniform(0.15, 0.30)
    estimated_cost = contract_val * (1 - margin)
    
    projects.append({
        "Project_ID": f"PROJ-{1000+i}",
        "Project_Name": f"{fake.company()} HQ HVAC Retrofit",
        "Contract_Value": contract_val,
        "Start_Date": start_date,
        "End_Date": end_date,
        "Bid_Margin_Target": round(margin, 2),
        "Bid_Assumption_Labor_Rate": random.choice([85, 95, 110]),
        "Bid_Assumption_Escalation": "3%"
    })

df_projects = pd.DataFrame(projects)

# --- 2. SCHEDULE OF VALUES (SOV) ---
sov_items = []
for proj in projects:
    total_val = proj['Contract_Value']
    # Split contract into chunks
    splits = np.random.dirichlet(np.ones(len(hvac_tasks)), size=1)[0]
    
    for task, split in zip(hvac_tasks, splits):
        sov_items.append({
            "SOV_ID": fake.uuid4()[:8],
            "Project_ID": proj['Project_ID'],
            "Description": task,
            "Scheduled_Value": round(total_val * split, 2),
            "Cost_Code": f"023-{random.randint(100,999)}"
        })

df_sov = pd.DataFrame(sov_items)

# --- 3. LABOR LOGS (Daily Crew Hours) ---
labor_logs = []
crew_types = ["Foreman", "Journeyman", "Apprentice"]

for proj in projects:
    current_date = proj['Start_Date']
    while current_date <= proj['End_Date']:
        if current_date.weekday() < 5: # Mon-Fri only
            for _ in range(random.randint(1, 3)): # 1-3 entries per day
                labor_logs.append({
                    "Log_ID": fake.uuid4()[:8],
                    "Project_ID": proj['Project_ID'],
                    "Date": current_date,
                    "Employee_ID": f"EMP-{random.randint(10, 50)}",
                    "Role": random.choice(crew_types),
                    "Hours_Regular": random.randint(4, 8),
                    "Hours_Overtime": random.choices([0, 2, 4], weights=[80, 15, 5])[0],
                    "Cost_Code": random.choice(df_sov[df_sov['Project_ID'] == proj['Project_ID']]['Cost_Code'].values)
                })
        current_date += timedelta(days=1)

df_labor = pd.DataFrame(labor_logs)

# --- 4. FIELD NOTES (Unstructured Text) ---
field_notes = []
note_templates = [
    "Delay due to {reason}.", 
    "Completed {task} ahead of schedule.", 
    "Site access blocked by {blocker}.",
    "Crew short staffed, {name} called out sick.",
    "Material delivery damaged: {material}."
]
reasons = ["GC not ready", "rain", "missing lift", "inspection failure"]
blockers = ["drywall stacks", "electricians", "painters"]

for proj in projects:
    # Generate random notes for 30% of project days
    project_days = pd.date_range(proj['Start_Date'], proj['End_Date'])
    note_days = random.sample(list(project_days), int(len(project_days) * 0.3))
    
    for day in note_days:
        template = random.choice(note_templates)
        note_text = template.format(
            reason=random.choice(reasons),
            task=random.choice(hvac_tasks),
            blocker=random.choice(blockers),
            name=fake.first_name(),
            material=random.choice(materials).split(' ')[0]
        )
        field_notes.append({
            "Note_ID": fake.uuid4()[:8],
            "Project_ID": proj['Project_ID'],
            "Date": day,
            "Author": "Site Super",
            "Note_Text": note_text
        })

df_notes = pd.DataFrame(field_notes)

# --- 5. RFI LOGS ---
rfis = []
for proj in projects:
    num_rfis = random.randint(2, 10)
    for i in range(num_rfis):
        date_sent = fake.date_between(start_date=proj['Start_Date'], end_date=proj['End_Date'])
        rfis.append({
            "RFI_ID": f"RFI-{proj['Project_ID']}-{i+1:03d}",
            "Project_ID": proj['Project_ID'],
            "Date_Submitted": date_sent,
            "Subject": f"Clarification on {random.choice(hvac_tasks)}",
            "Question": f"Drawing A-{random.randint(100,500)} shows clash with {random.choice(['beams', 'fire sprinklers', 'lighting'])}. Please advise on rerouting.",
            "Status": random.choice(["Open", "Closed", "Void"]),
            "Cost_Impact": random.choice([0, 0, random.randint(500, 5000)])
        })

df_rfis = pd.DataFrame(rfis)

# --- OUTPUT ---
print("Dataset Generation Complete.")
print(f"Projects: {len(df_projects)}")
print(f"SOV Lines: {len(df_sov)}")
print(f"Labor Logs: {len(df_labor)}")
print(f"Field Notes: {len(df_notes)}")
print(f"RFIs: {len(df_rfis)}")

# Example: Save to CSV
# df_projects.to_csv("hvac_projects.csv", index=False)
# df_sov.to_csv("hvac_sov.csv", index=False)
# df_labor.to_csv("hvac_labor.csv", index=False)
# df_notes.to_csv("hvac_field_notes.csv", index=False)
# df_rfis.to_csv("hvac_rfis.csv", index=False)
