#!/usr/bin/env python3
"""
HVAC Construction Project Dataset Generator
Generates realistic synthetic data for mechanical contracting projects with
proper interrelationships between all data categories.
"""

import json
import random
import csv
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import uuid

# Seed for reproducibility
random.seed(42)

# =============================================================================
# CONFIGURATION & CONSTANTS
# =============================================================================

PROJECTS = [
    {
        "id": "PRJ-2024-001",
        "name": "Mercy General Hospital - HVAC Modernization",
        "type": "Healthcare",
        "location": "Phoenix, AZ",
        "sq_ft": 285000,
        "floors": 6,
        "duration_months": 18,
        "complexity": "high"
    },
    {
        "id": "PRJ-2024-002", 
        "name": "Riverside Office Tower - Core & Shell MEP",
        "type": "Commercial Office",
        "location": "Denver, CO",
        "sq_ft": 420000,
        "floors": 22,
        "duration_months": 24,
        "complexity": "high"
    },
    {
        "id": "PRJ-2024-003",
        "name": "Greenfield Elementary School - New Construction",
        "type": "K-12 Education",
        "location": "Austin, TX",
        "sq_ft": 95000,
        "floors": 2,
        "duration_months": 14,
        "complexity": "medium"
    },
    {
        "id": "PRJ-2024-004",
        "name": "Summit Data Center - Phase 2 Expansion",
        "type": "Data Center",
        "location": "Ashburn, VA",
        "sq_ft": 65000,
        "floors": 1,
        "duration_months": 10,
        "complexity": "high"
    },
    {
        "id": "PRJ-2024-005",
        "name": "Harbor View Condominiums - 3 Buildings",
        "type": "Multifamily Residential",
        "location": "Seattle, WA",
        "sq_ft": 340000,
        "floors": 8,
        "duration_months": 20,
        "complexity": "medium"
    }
]

SOV_TEMPLATE = [
    {"code": "01", "description": "General Conditions & Project Management", "pct_range": (0.06, 0.09)},
    {"code": "02", "description": "Submittals & Engineering", "pct_range": (0.02, 0.04)},
    {"code": "03", "description": "Ductwork - Fabrication", "pct_range": (0.08, 0.12)},
    {"code": "04", "description": "Ductwork - Installation", "pct_range": (0.10, 0.14)},
    {"code": "05", "description": "Piping - Hydronic Systems", "pct_range": (0.08, 0.12)},
    {"code": "06", "description": "Piping - Refrigerant", "pct_range": (0.04, 0.07)},
    {"code": "07", "description": "Equipment - RTUs/AHUs", "pct_range": (0.12, 0.18)},
    {"code": "08", "description": "Equipment - Chillers/Boilers", "pct_range": (0.08, 0.14)},
    {"code": "09", "description": "Equipment - Terminal Units (VAV/FCU)", "pct_range": (0.06, 0.10)},
    {"code": "10", "description": "Controls - DDC/BAS Installation", "pct_range": (0.06, 0.10)},
    {"code": "11", "description": "Controls - Programming & Commissioning", "pct_range": (0.03, 0.05)},
    {"code": "12", "description": "Insulation", "pct_range": (0.04, 0.06)},
    {"code": "13", "description": "Testing, Adjusting & Balancing (TAB)", "pct_range": (0.02, 0.04)},
    {"code": "14", "description": "Startup & Commissioning Support", "pct_range": (0.02, 0.03)},
    {"code": "15", "description": "Closeout Documentation & Training", "pct_range": (0.01, 0.02)},
]

CREW_ROLES = [
    {"role": "Foreman", "hourly_rate": 85.50, "burden_rate": 1.42},
    {"role": "Journeyman Sheet Metal", "hourly_rate": 72.00, "burden_rate": 1.42},
    {"role": "Journeyman Pipefitter", "hourly_rate": 74.50, "burden_rate": 1.42},
    {"role": "Apprentice 4th Year", "hourly_rate": 52.00, "burden_rate": 1.38},
    {"role": "Apprentice 2nd Year", "hourly_rate": 38.00, "burden_rate": 1.38},
    {"role": "Controls Technician", "hourly_rate": 68.00, "burden_rate": 1.40},
    {"role": "Insulator", "hourly_rate": 58.00, "burden_rate": 1.40},
    {"role": "Helper/Laborer", "hourly_rate": 32.00, "burden_rate": 1.35},
]

MATERIAL_CATEGORIES = [
    {"category": "Ductwork", "items": ["Galvanized Sheet Metal 22ga", "Galvanized Sheet Metal 20ga", "Flex Duct 8\"", "Flex Duct 10\"", "Flex Duct 12\"", "Spiral Duct 12\"", "Spiral Duct 16\"", "Spiral Duct 24\"", "Duct Sealant", "Hanging Hardware"]},
    {"category": "Piping", "items": ["Copper Type L 1\"", "Copper Type L 1.5\"", "Copper Type L 2\"", "Black Steel Sch40 2\"", "Black Steel Sch40 4\"", "PVC Sch40 4\"", "Pipe Hangers Assorted", "Brazing Alloy", "Flux", "Refrigerant R-410A"]},
    {"category": "Equipment", "items": ["RTU 15-Ton", "RTU 25-Ton", "AHU Custom", "Chiller 200-Ton", "Boiler 2000MBH", "VAV Box 12\"", "VAV Box 16\"", "FCU 2-Pipe", "FCU 4-Pipe", "Split System 3-Ton"]},
    {"category": "Controls", "items": ["DDC Controller", "VAV Controller", "Temp Sensor", "Pressure Sensor", "Actuator 24V", "Damper Motor", "Control Valve 1\"", "Control Valve 2\"", "BACnet Gateway", "Touchscreen Interface"]},
    {"category": "Insulation", "items": ["Fiberglass Duct Wrap R-8", "Fiberglass Duct Liner R-6", "Pipe Insulation 1\" Armaflex", "Pipe Insulation 2\" Armaflex", "Insulation Adhesive", "Vapor Barrier Tape"]},
]

RFI_SUBJECTS = [
    "Coordination conflict with electrical conduit at grid {grid}",
    "Clarification needed on diffuser layout for {room}",
    "Structural penetration approval required at {location}",
    "Equipment access clearance insufficient per spec",
    "Ductwork routing conflicts with beam at elevation {elev}",
    "Control sequence clarification for {system}",
    "Pipe sleeve size discrepancy at {location}",
    "Seismic bracing requirements for equipment over {weight} lbs",
    "Fire damper location verification needed",
    "Insulation spec clarification for exterior application",
    "VAV box sizing appears undersized for zone CFM",
    "Refrigerant piping routing through {area} - approval needed",
    "Existing conditions differ from drawings at {location}",
    "Thermostat location conflicts with furniture layout",
    "Access panel requirements for concealed valves",
]

CHANGE_ORDER_REASONS = [
    ("Owner Request", "Added {item} per owner directive"),
    ("Design Error", "Drawings showed incorrect {dimension} - field correction required"),
    ("Unforeseen Condition", "Discovered {condition} not shown on documents"),
    ("Coordination", "Rerouting required due to {trade} conflict"),
    ("Code Compliance", "Inspector required {requirement}"),
    ("Value Engineering", "Substitution approved: {old_item} to {new_item}"),
    ("Scope Gap", "Work not clearly defined in bid documents"),
    ("Acceleration", "Premium time to maintain schedule"),
]

FIELD_NOTE_TEMPLATES = [
    "Crew arrived {time}. Weather: {weather}. {crew_count} workers on site. Focus today: {task}. {observation}",
    "Safety meeting held at start of shift - topic: {safety_topic}. All PPE verified. {work_description}",
    "Received delivery of {material} - {qty} units. {receipt_note}. Staged at {location}.",
    "Met with {trade} foreman re: coordination. {meeting_outcome}. Action items: {actions}",
    "GC weekly meeting - discussed {topics}. Schedule status: {schedule_status}. RFIs pending: {rfi_count}.",
    "Installed {qty} {units} on floor {floor}. {quality_note}. Inspections needed: {inspections}.",
    "Equipment startup for {equipment}. {startup_result}. Punch list items: {punch_items}.",
    "{issue_type} encountered: {issue_description}. Resolution: {resolution}. Impact: {impact}.",
    "Working in {area} - {progress_pct}% complete this zone. Remaining: {remaining_work}.",
    "TAB contractor on site - balancing {system}. Initial readings: {readings}. Adjustments: {adjustments}.",
]

# =============================================================================
# DATA GENERATION FUNCTIONS
# =============================================================================

def generate_contract_value(project: Dict) -> Dict:
    """Generate base contract value based on project characteristics."""
    # Base cost per SF varies by project type
    cost_per_sf = {
        "Healthcare": random.uniform(85, 120),
        "Commercial Office": random.uniform(45, 65),
        "K-12 Education": random.uniform(55, 75),
        "Data Center": random.uniform(180, 280),
        "Multifamily Residential": random.uniform(35, 50),
    }
    
    base_cost = project["sq_ft"] * cost_per_sf[project["type"]]
    
    # Complexity adjustment
    complexity_mult = {"low": 0.9, "medium": 1.0, "high": 1.15}
    base_cost *= complexity_mult[project["complexity"]]
    
    # Round to realistic contract value
    base_cost = round(base_cost / 1000) * 1000
    
    return {
        "project_id": project["id"],
        "project_name": project["name"],
        "original_contract_value": base_cost,
        "contract_date": (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d"),
        "substantial_completion_date": (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 90) + project["duration_months"] * 30)).strftime("%Y-%m-%d"),
        "retention_pct": 0.10,
        "payment_terms": "Net 30",
        "gc_name": random.choice(["Turner Construction", "DPR Construction", "Skanska USA", "JE Dunn", "Mortenson"]),
        "architect": random.choice(["Gensler", "HOK", "Perkins&Will", "HKS", "SmithGroup"]),
        "engineer_of_record": random.choice(["WSP", "ARUP", "Syska Hennessy", "Henderson Engineers", "AEI"]),
    }


def generate_sov(project: Dict, contract_value: float) -> List[Dict]:
    """Generate Schedule of Values line items that sum to contract value."""
    sov_lines = []
    
    # Generate percentages ensuring they sum to 1.0
    raw_pcts = []
    for item in SOV_TEMPLATE:
        pct = random.uniform(item["pct_range"][0], item["pct_range"][1])
        raw_pcts.append(pct)
    
    # Normalize to sum to 1.0
    total_pct = sum(raw_pcts)
    normalized_pcts = [p / total_pct for p in raw_pcts]
    
    for i, item in enumerate(SOV_TEMPLATE):
        line_value = contract_value * normalized_pcts[i]
        # Round to nearest $100
        line_value = round(line_value / 100) * 100
        
        sov_lines.append({
            "project_id": project["id"],
            "sov_line_id": f"{project['id']}-SOV-{item['code']}",
            "line_number": int(item["code"]),
            "description": item["description"],
            "scheduled_value": line_value,
            "labor_pct": random.uniform(0.55, 0.75) if "Equipment" not in item["description"] else random.uniform(0.15, 0.30),
            "material_pct": random.uniform(0.25, 0.45) if "Equipment" not in item["description"] else random.uniform(0.70, 0.85),
        })
    
    # Adjust last line to make sum exact
    current_total = sum(line["scheduled_value"] for line in sov_lines)
    sov_lines[-1]["scheduled_value"] += (contract_value - current_total)
    
    return sov_lines


def generate_labor_logs(project: Dict, sov_lines: List[Dict], start_date: datetime) -> List[Dict]:
    """Generate daily labor logs with realistic crew patterns."""
    logs = []
    project_duration_days = project["duration_months"] * 22  # ~22 work days per month
    
    # Track cumulative hours by SOV line for realistic progression
    sov_labor_budgets = {}
    for line in sov_lines:
        labor_value = line["scheduled_value"] * line["labor_pct"]
        # Estimate hours based on blended rate of ~$65/hr
        sov_labor_budgets[line["sov_line_id"]] = labor_value / 65
    
    current_date = start_date
    day_count = 0
    
    while day_count < project_duration_days:
        # Skip weekends
        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue
        
        # Determine crew size based on project phase
        phase_pct = day_count / project_duration_days
        if phase_pct < 0.15:  # Mobilization/submittals
            base_crew = random.randint(2, 5)
        elif phase_pct < 0.75:  # Peak production
            base_crew = random.randint(8, 18) if project["complexity"] == "high" else random.randint(5, 12)
        else:  # Closeout
            base_crew = random.randint(3, 7)
        
        # Determine which SOV lines are active
        active_sov_lines = []
        if phase_pct < 0.10:
            active_sov_lines = [l for l in sov_lines if l["line_number"] in [1, 2]]
        elif phase_pct < 0.30:
            active_sov_lines = [l for l in sov_lines if l["line_number"] in [1, 2, 3, 4, 5]]
        elif phase_pct < 0.60:
            active_sov_lines = [l for l in sov_lines if l["line_number"] in [1, 3, 4, 5, 6, 7, 8, 9]]
        elif phase_pct < 0.85:
            active_sov_lines = [l for l in sov_lines if l["line_number"] in [1, 9, 10, 11, 12]]
        else:
            active_sov_lines = [l for l in sov_lines if l["line_number"] in [1, 11, 13, 14, 15]]
        
        if not active_sov_lines:
            active_sov_lines = [sov_lines[0]]
        
        # Generate individual worker entries for the day
        workers_assigned = random.sample(CREW_ROLES, min(base_crew, len(CREW_ROLES)))
        
        # Possibly add duplicates of common roles
        if base_crew > len(CREW_ROLES):
            common_roles = [r for r in CREW_ROLES if "Journeyman" in r["role"] or "Apprentice" in r["role"]]
            for _ in range(base_crew - len(CREW_ROLES)):
                workers_assigned.append(random.choice(common_roles))
        
        for worker in workers_assigned:
            # Assign to an SOV line
            assigned_sov = random.choice(active_sov_lines)
            
            # Hours - typically 8, sometimes OT
            if random.random() < 0.15:  # 15% chance of OT
                hours_st = 8
                hours_ot = random.choice([2, 4])
            else:
                hours_st = 8 if random.random() > 0.1 else random.choice([4, 6, 10])
                hours_ot = 0
            
            logs.append({
                "project_id": project["id"],
                "log_id": str(uuid.uuid4())[:8],
                "date": current_date.strftime("%Y-%m-%d"),
                "employee_id": f"EMP-{random.randint(1000, 9999)}",
                "role": worker["role"],
                "sov_line_id": assigned_sov["sov_line_id"],
                "hours_st": hours_st,
                "hours_ot": hours_ot,
                "hourly_rate": worker["hourly_rate"],
                "burden_multiplier": worker["burden_rate"],
                "work_area": f"Floor {random.randint(1, project['floors'])}",
                "cost_code": assigned_sov["line_number"],
            })
        
        current_date += timedelta(days=1)
        day_count += 1
    
    return logs


def generate_material_deliveries(project: Dict, sov_lines: List[Dict], start_date: datetime) -> List[Dict]:
    """Generate material delivery records with realistic timing and quantities."""
    deliveries = []
    project_duration_days = project["duration_months"] * 30
    
    # Map SOV lines to material categories
    sov_to_materials = {
        3: "Ductwork", 4: "Ductwork",
        5: "Piping", 6: "Piping",
        7: "Equipment", 8: "Equipment", 9: "Equipment",
        10: "Controls", 11: "Controls",
        12: "Insulation",
    }
    
    for sov_line in sov_lines:
        if sov_line["line_number"] not in sov_to_materials:
            continue
        
        material_cat = sov_to_materials[sov_line["line_number"]]
        cat_info = next(c for c in MATERIAL_CATEGORIES if c["category"] == material_cat)
        
        # Material budget for this SOV line
        material_budget = sov_line["scheduled_value"] * sov_line["material_pct"]
        
        # Generate 3-8 deliveries per SOV line
        num_deliveries = random.randint(3, 8)
        delivery_values = []
        
        for _ in range(num_deliveries):
            delivery_values.append(random.random())
        
        # Normalize
        total = sum(delivery_values)
        delivery_values = [(v / total) * material_budget for v in delivery_values]
        
        for i, value in enumerate(delivery_values):
            # Delivery timing based on SOV line number (phase)
            if sov_line["line_number"] <= 4:
                day_offset = random.randint(15, int(project_duration_days * 0.4))
            elif sov_line["line_number"] <= 9:
                day_offset = random.randint(int(project_duration_days * 0.15), int(project_duration_days * 0.7))
            else:
                day_offset = random.randint(int(project_duration_days * 0.4), int(project_duration_days * 0.9))
            
            delivery_date = start_date + timedelta(days=day_offset)
            
            # Select items
            item = random.choice(cat_info["items"])
            
            # Generate realistic quantities
            if "RTU" in item or "Chiller" in item or "Boiler" in item or "AHU" in item:
                qty = random.randint(1, 4)
                unit = "EA"
                unit_cost = value / qty
            elif "Sheet Metal" in item:
                qty = random.randint(20, 100)
                unit = "SHEET"
                unit_cost = value / qty
            elif "Duct" in item:
                qty = random.randint(50, 500)
                unit = "LF"
                unit_cost = value / qty
            elif "Pipe" in item or "Copper" in item or "Steel" in item:
                qty = random.randint(100, 1000)
                unit = "LF"
                unit_cost = value / qty
            elif "VAV" in item or "FCU" in item:
                qty = random.randint(5, 40)
                unit = "EA"
                unit_cost = value / qty
            elif "Controller" in item or "Sensor" in item or "Actuator" in item:
                qty = random.randint(10, 100)
                unit = "EA"
                unit_cost = value / qty
            else:
                qty = random.randint(5, 50)
                unit = "EA"
                unit_cost = value / qty
            
            deliveries.append({
                "project_id": project["id"],
                "delivery_id": f"DEL-{project['id'][-3:]}-{str(uuid.uuid4())[:6]}",
                "date": delivery_date.strftime("%Y-%m-%d"),
                "sov_line_id": sov_line["sov_line_id"],
                "material_category": material_cat,
                "item_description": item,
                "quantity": qty,
                "unit": unit,
                "unit_cost": round(unit_cost, 2),
                "total_cost": round(value, 2),
                "po_number": f"PO-{random.randint(10000, 99999)}",
                "vendor": random.choice(["Ferguson Supply", "Winsupply", "RE Michel", "ACR Group", "Carrier Enterprise", "Johnstone Supply"]),
                "received_by": random.choice(["J. Martinez", "K. Thompson", "R. Williams", "M. Chen", "D. Patel"]),
                "condition_notes": random.choice(["Good condition", "Good condition", "Good condition", "Minor packaging damage - product OK", "Partial shipment - backorder pending", "Good condition"]),
            })
    
    return sorted(deliveries, key=lambda x: x["date"])


def generate_change_orders(project: Dict, contract_value: float, sov_lines: List[Dict], start_date: datetime) -> List[Dict]:
    """Generate change order requests with realistic reasons and values."""
    change_orders = []
    
    # Number of COs based on project complexity and size
    num_cos = {
        "low": random.randint(3, 6),
        "medium": random.randint(6, 12),
        "high": random.randint(10, 20),
    }[project["complexity"]]
    
    project_duration_days = project["duration_months"] * 30
    
    for i in range(num_cos):
        reason_type, reason_template = random.choice(CHANGE_ORDER_REASONS)
        
        # CO value - mix of adds and credits
        if reason_type == "Value Engineering":
            # Credits are typically smaller
            co_value = -1 * random.uniform(0.002, 0.015) * contract_value
        elif reason_type in ["Owner Request", "Scope Gap"]:
            co_value = random.uniform(0.005, 0.04) * contract_value
        else:
            co_value = random.uniform(0.002, 0.025) * contract_value
        
        # Round to nearest $100
        co_value = round(co_value / 100) * 100
        
        # Timing
        day_offset = random.randint(30, project_duration_days - 30)
        co_date = start_date + timedelta(days=day_offset)
        
        # Status based on age
        age_days = (datetime.now() - co_date).days
        if age_days < 14:
            status = random.choice(["Pending", "Under Review"])
        elif age_days < 45:
            status = random.choice(["Under Review", "Approved", "Rejected"])
        else:
            status = random.choice(["Approved", "Approved", "Approved", "Rejected"])
        
        # Fill in template
        reason_text = reason_template.format(
            item=random.choice(["exhaust fan", "VAV boxes", "chilled water piping", "controls points"]),
            dimension=random.choice(["duct size", "pipe elevation", "equipment clearance"]),
            condition=random.choice(["existing ductwork", "abandoned piping", "structural conflict", "asbestos insulation"]),
            trade=random.choice(["electrical", "plumbing", "fire protection", "structural"]),
            requirement=random.choice(["additional smoke detectors", "seismic upgrades", "fire dampers", "access panels"]),
            old_item=random.choice(["Carrier RTU", "Trane chiller", "copper piping"]),
            new_item=random.choice(["Daikin RTU", "York chiller", "steel piping"]),
        )
        
        change_orders.append({
            "project_id": project["id"],
            "co_number": f"CO-{str(i+1).zfill(3)}",
            "date_submitted": co_date.strftime("%Y-%m-%d"),
            "reason_category": reason_type,
            "description": reason_text,
            "amount": co_value,
            "status": status,
            "related_rfi": f"RFI-{random.randint(1, 30):03d}" if random.random() > 0.4 else None,
            "affected_sov_lines": random.sample([l["sov_line_id"] for l in sov_lines], random.randint(1, 3)),
            "labor_hours_impact": random.randint(8, 200) if co_value > 0 else -random.randint(8, 100),
            "schedule_impact_days": random.choice([0, 0, 0, 0, 2, 5, 7, 14]) if co_value > 0 else 0,
            "submitted_by": random.choice(["J. Martinez", "K. Thompson", "R. Williams"]),
            "approved_by": random.choice(["Project Manager", "Owner Rep", None]),
        })
    
    return sorted(change_orders, key=lambda x: x["date_submitted"])


def generate_rfis(project: Dict, start_date: datetime) -> List[Dict]:
    """Generate RFI log with realistic construction questions."""
    rfis = []
    
    num_rfis = {
        "low": random.randint(15, 30),
        "medium": random.randint(30, 60),
        "high": random.randint(50, 100),
    }[project["complexity"]]
    
    project_duration_days = project["duration_months"] * 30
    
    for i in range(num_rfis):
        day_offset = random.randint(14, project_duration_days - 14)
        submit_date = start_date + timedelta(days=day_offset)
        
        # Response time varies
        response_days = random.choices(
            [3, 5, 7, 10, 14, 21, None],
            weights=[0.15, 0.25, 0.25, 0.15, 0.10, 0.05, 0.05]
        )[0]
        
        response_date = (submit_date + timedelta(days=response_days)).strftime("%Y-%m-%d") if response_days else None
        
        # Generate subject from template
        subject_template = random.choice(RFI_SUBJECTS)
        subject = subject_template.format(
            grid=f"{random.choice('ABCDEFGH')}-{random.randint(1, 12)}",
            room=f"Room {random.randint(100, 600)}",
            location=f"Floor {random.randint(1, project['floors'])}, Grid {random.choice('ABCDEFGH')}-{random.randint(1, 12)}",
            elev=f"+{random.randint(10, 50)}'-0\"",
            system=random.choice(["AHU-1", "CHW Loop", "HW Loop", "Exhaust System", "VAV Zone 3"]),
            area=random.choice(["mechanical room", "ceiling plenum", "exterior wall", "elevator shaft"]),
            weight=random.choice(["500", "1000", "2000"]),
        )
        
        status = "Closed" if response_date else random.choice(["Open", "Pending Response"])
        
        rfis.append({
            "project_id": project["id"],
            "rfi_number": f"RFI-{str(i+1).zfill(3)}",
            "date_submitted": submit_date.strftime("%Y-%m-%d"),
            "subject": subject,
            "submitted_by": random.choice(["J. Martinez - Project Manager", "K. Thompson - Foreman", "R. Williams - Engineer"]),
            "assigned_to": random.choice(["Architect", "MEP Engineer", "Structural Engineer", "Owner"]),
            "priority": random.choices(["Low", "Medium", "High", "Critical"], weights=[0.2, 0.45, 0.25, 0.10])[0],
            "status": status,
            "date_required": (submit_date + timedelta(days=random.randint(7, 21))).strftime("%Y-%m-%d"),
            "date_responded": response_date,
            "response_summary": random.choice([
                "Proceed as noted in attached sketch.",
                "Refer to ASI-{} for clarification.".format(random.randint(1, 20)),
                "Approved as submitted.",
                "Revise per attached markup.",
                "Coordinate with {} contractor.".format(random.choice(["electrical", "plumbing", "structural"])),
            ]) if response_date else None,
            "cost_impact": random.choice([True, False, False, False]),
            "schedule_impact": random.choice([True, False, False, False, False]),
        })
    
    return sorted(rfis, key=lambda x: x["date_submitted"])


def generate_field_notes(project: Dict, start_date: datetime) -> List[Dict]:
    """Generate unstructured field notes/daily reports."""
    notes = []
    
    project_duration_days = project["duration_months"] * 22  # Work days
    current_date = start_date
    day_count = 0
    
    while day_count < project_duration_days:
        # Skip weekends
        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue
        
        # Not every day has detailed notes
        if random.random() < 0.7:  # 70% of days have notes
            template = random.choice(FIELD_NOTE_TEMPLATES)
            
            note_text = template.format(
                time=random.choice(["0600", "0630", "0700"]),
                weather=random.choice(["Clear, 72°F", "Partly cloudy, 65°F", "Rain - indoor work only", "Hot, 95°F - heat protocol", "Cold, 35°F"]),
                crew_count=random.randint(4, 16),
                task=random.choice([
                    "ductwork installation Floor 3", "piping rough-in mechanical room",
                    "hanging VAV boxes wing B", "controls wiring", "insulation west side",
                    "equipment rigging", "startup AHU-2", "TAB work zones 1-4"
                ]),
                observation=random.choice([
                    "Good progress.", "Behind schedule due to material delay.",
                    "Ahead of plan.", "Coordination issues with electrical - resolved on site.",
                    "Waiting on RFI response to proceed.", "Inspection passed."
                ]),
                safety_topic=random.choice([
                    "ladder safety", "PPE requirements", "fall protection",
                    "hot work permits", "lockout/tagout", "confined space entry"
                ]),
                work_description=random.choice([
                    "Continued ductwork installation per plan.",
                    "Completed piping pressure test - passed.",
                    "Set 3 VAV boxes, awaiting controls.",
                    "Ran refrigerant lines to condensers."
                ]),
                material=random.choice(["sheet metal", "copper piping", "VAV boxes", "RTU", "insulation"]),
                qty=random.randint(10, 200),
                receipt_note=random.choice(["Matched PO", "Short 2 boxes - claim filed", "All accounted for"]),
                location=random.choice(["laydown area A", "mechanical room", "loading dock", "floor 3 staging"]),
                trade=random.choice(["electrical", "plumbing", "fire protection", "drywall"]),
                meeting_outcome=random.choice([
                    "Agreed on sequence for ceiling close-in",
                    "Resolved duct routing conflict",
                    "Scheduled joint walkthrough Friday"
                ]),
                actions=random.choice([
                    "HVAC to relocate diffuser 6 inches east",
                    "FP to adjust sprinkler head locations",
                    "Awaiting revised drawings"
                ]),
                topics=random.choice([
                    "schedule recovery, material lead times, inspections",
                    "safety incident review, upcoming inspections, manpower",
                    "change orders, RFI backlog, coordination"
                ]),
                schedule_status=random.choice(["on track", "3 days behind", "ahead 2 days", "critical - recovery plan in place"]),
                rfi_count=random.randint(2, 15),
                qty2=random.randint(5, 25),
                units=random.choice(["VAV boxes", "diffusers", "LF of duct", "pipe hangers"]),
                floor=random.randint(1, project["floors"]),
                quality_note=random.choice(["Passed QC inspection", "Minor punch items noted", "Rework required grid C-4"]),
                inspections=random.choice(["rough-in Friday", "pressure test Monday", "none"]),
                equipment=random.choice(["RTU-1", "AHU-2", "Chiller", "Boiler", "FCU bank west"]),
                startup_result=random.choice([
                    "Successful - all parameters normal",
                    "Minor vibration issue - balancing tomorrow",
                    "Delayed - controls not ready"
                ]),
                punch_items=random.choice(["none", "3 minor items", "damper actuator adjustment", "sensor calibration"]),
                issue_type=random.choice(["Coordination conflict", "Material issue", "Design discrepancy", "Access issue"]),
                issue_description=random.choice([
                    "sprinkler head conflicts with diffuser at B-7",
                    "wrong size fittings delivered",
                    "field conditions don't match drawings",
                    "ceiling access restricted by other trade"
                ]),
                resolution=random.choice([
                    "RFI submitted", "Resolved on site with GC", "Awaiting engineer response", "Workaround implemented"
                ]),
                impact=random.choice(["none", "1 day delay", "cost impact TBD", "schedule neutral"]),
                area=random.choice(["Zone 3", "mechanical room", "penthouse", "basement", "floors 4-6"]),
                progress_pct=random.randint(40, 95),
                remaining_work=random.choice([
                    "diffusers and connections", "insulation and startup",
                    "controls terminations", "final connections"
                ]),
                system=random.choice(["VAV system floor 2", "AHU-1 supply", "FCU loop", "exhaust system"]),
                readings=random.choice([
                    "CFM within 5% of design", "static pressure high",
                    "flow low on 3 boxes", "all zones balanced"
                ]),
                adjustments=random.choice([
                    "sheave change AHU", "damper repositioning", "none required", "VFD reprogramming"
                ]),
            )
            
            notes.append({
                "project_id": project["id"],
                "note_id": str(uuid.uuid4())[:8],
                "date": current_date.strftime("%Y-%m-%d"),
                "author": random.choice(["J. Martinez", "K. Thompson", "R. Williams", "M. Chen"]),
                "note_type": random.choice(["Daily Report", "Safety Log", "Coordination Note", "Inspection Note", "Issue Log"]),
                "content": note_text,
                "photos_attached": random.randint(0, 5),
                "weather": random.choice(["Clear", "Cloudy", "Rain", "Hot", "Cold"]),
                "temp_high": random.randint(55, 100),
                "temp_low": random.randint(35, 75),
            })
        
        current_date += timedelta(days=1)
        day_count += 1
    
    return notes


def generate_billing_history(project: Dict, sov_lines: List[Dict], contract_value: float, start_date: datetime) -> List[Dict]:
    """Generate progress billing history with realistic draw patterns."""
    billing = []
    
    project_duration_months = project["duration_months"]
    
    # Track cumulative billing per SOV line
    sov_billing = {line["sov_line_id"]: 0 for line in sov_lines}
    sov_values = {line["sov_line_id"]: line["scheduled_value"] for line in sov_lines}
    sov_numbers = {line["sov_line_id"]: line["line_number"] for line in sov_lines}
    
    for month in range(project_duration_months + 1):
        billing_date = start_date + timedelta(days=30 * month + 25)
        
        # Determine progress percentage based on S-curve
        month_pct = month / project_duration_months
        if month_pct < 0.15:
            progress_mult = month_pct * 2  # Slow start
        elif month_pct < 0.85:
            progress_mult = 0.3 + (month_pct - 0.15) * 1.0  # Peak production
        else:
            progress_mult = 0.95 + (month_pct - 0.85) * 0.33  # Closeout
        
        progress_mult = min(progress_mult, 1.0)
        
        # Bill each SOV line
        line_items = []
        period_total = 0
        
        for sov_line in sov_lines:
            sov_id = sov_line["sov_line_id"]
            sov_num = sov_numbers[sov_id]
            
            # Determine target progress for this SOV line based on phase
            if sov_num <= 2:  # Early items
                target_pct = min(progress_mult * 1.3, 1.0)
            elif sov_num <= 9:  # Core work
                target_pct = progress_mult
            elif sov_num <= 12:  # Controls/insulation
                target_pct = max(progress_mult - 0.15, 0) * 1.15
            else:  # Closeout
                target_pct = max(progress_mult - 0.3, 0) * 1.4
            
            target_pct = min(target_pct, 1.0)
            target_amount = sov_values[sov_id] * target_pct
            
            # Current period billing
            period_billing = max(target_amount - sov_billing[sov_id], 0)
            
            # Add some randomness
            period_billing *= random.uniform(0.85, 1.0)
            period_billing = round(period_billing / 100) * 100
            
            # Don't exceed scheduled value
            if sov_billing[sov_id] + period_billing > sov_values[sov_id]:
                period_billing = sov_values[sov_id] - sov_billing[sov_id]
            
            if period_billing > 0:
                sov_billing[sov_id] += period_billing
                period_total += period_billing
                
                line_items.append({
                    "sov_line_id": sov_id,
                    "description": sov_line["description"],
                    "scheduled_value": sov_values[sov_id],
                    "previous_billed": sov_billing[sov_id] - period_billing,
                    "this_period": period_billing,
                    "total_billed": sov_billing[sov_id],
                    "pct_complete": round(sov_billing[sov_id] / sov_values[sov_id] * 100, 1),
                    "balance_to_finish": sov_values[sov_id] - sov_billing[sov_id],
                })
        
        if period_total > 0:
            cumulative = sum(sov_billing.values())
            retention = cumulative * 0.10
            
            billing.append({
                "project_id": project["id"],
                "application_number": month + 1,
                "period_end": billing_date.strftime("%Y-%m-%d"),
                "period_total": period_total,
                "cumulative_billed": cumulative,
                "retention_held": retention,
                "net_payment_due": cumulative - retention,
                "status": random.choice(["Paid", "Paid", "Paid", "Pending", "Approved"]) if month < project_duration_months - 1 else "Pending",
                "payment_date": (billing_date + timedelta(days=random.randint(25, 40))).strftime("%Y-%m-%d") if random.random() > 0.2 else None,
                "line_items": line_items,
            })
    
    return billing


def generate_bid_estimate(project: Dict, contract_value: float, sov_lines: List[Dict]) -> Dict:
    """Generate original bid estimate assumptions."""
    
    # Labor assumptions
    total_labor_hours = sum(
        (line["scheduled_value"] * line["labor_pct"]) / 65  # Avg $65/hr
        for line in sov_lines
    )
    
    # Calculate what contract should have been at current rates
    bid_date = datetime(2023, 10, 1) + timedelta(days=random.randint(0, 60))
    
    return {
        "project_id": project["id"],
        "bid_date": bid_date.strftime("%Y-%m-%d"),
        "bid_amount": contract_value,
        "estimator": random.choice(["S. Johnson", "M. Rodriguez", "T. Wilson"]),
        
        "labor_assumptions": {
            "total_hours_estimated": round(total_labor_hours),
            "blended_labor_rate": 65.00,
            "productivity_factor": random.uniform(0.85, 0.95),
            "crew_mix": {
                "foreman_pct": 0.08,
                "journeyman_pct": 0.45,
                "apprentice_pct": 0.35,
                "helper_pct": 0.12,
            },
            "overtime_allowance_pct": random.uniform(0.05, 0.12),
            "shift_premium": 0.0,
        },
        
        "material_assumptions": {
            "escalation_factor_pct": random.uniform(0.02, 0.05),
            "waste_factor_pct": random.uniform(0.03, 0.08),
            "freight_pct": random.uniform(0.02, 0.04),
            "key_material_quotes": [
                {"item": "Major Equipment", "vendor": random.choice(["Carrier", "Trane", "Daikin"]), "quote_date": bid_date.strftime("%Y-%m-%d"), "validity_days": 60},
                {"item": "Sheet Metal", "vendor": "Local Fab Shop", "quote_date": bid_date.strftime("%Y-%m-%d"), "validity_days": 30},
                {"item": "Controls", "vendor": random.choice(["Siemens", "Johnson Controls", "Honeywell"]), "quote_date": bid_date.strftime("%Y-%m-%d"), "validity_days": 45},
            ],
        },
        
        "subcontractor_assumptions": {
            "insulation_sub": {"name": "ABC Insulation", "quote": round(contract_value * 0.045, 2)},
            "tab_sub": {"name": "XYZ Balancing", "quote": round(contract_value * 0.025, 2)},
            "controls_sub": {"name": "Smart Building Controls", "quote": round(contract_value * 0.08, 2)},
        },
        
        "general_conditions": {
            "project_management_months": project["duration_months"],
            "site_supervision_months": project["duration_months"],
            "equipment_rental_months": round(project["duration_months"] * 0.6),
            "small_tools_pct": 0.015,
            "consumables_pct": 0.01,
        },
        
        "markup": {
            "overhead_pct": random.uniform(0.08, 0.12),
            "profit_pct": random.uniform(0.04, 0.08),
            "bond_pct": 0.015,
            "insurance_pct": random.uniform(0.02, 0.035),
        },
        
        "risk_allowances": {
            "design_contingency_pct": random.uniform(0.02, 0.05),
            "escalation_contingency_pct": random.uniform(0.02, 0.04),
            "schedule_risk_pct": random.uniform(0.01, 0.03),
        },
        
        "key_assumptions": [
            f"Project duration: {project['duration_months']} months from NTP",
            f"Work performed during normal hours (7:00 AM - 3:30 PM)",
            "GC to provide adequate laydown area and hoisting",
            "MEP coordination via BIM - 3 weeks prior to each floor",
            f"Equipment access via {random.choice(['loading dock', 'temporary opening', 'roof hatch'])}",
            "Fire watch by GC when required",
            "Temporary power and water by GC",
            f"Assumes {random.choice(['union', 'open shop'])} labor",
        ],
        
        "exclusions": [
            "Hazardous material abatement",
            "Structural modifications",
            "Electrical connections (by EC)",
            "Architectural louvers and grilles",
            "Access flooring",
            "Fire suppression (by FP contractor)",
            "Plumbing (by plumber)",
            "Testing beyond standard TAB",
        ],
        
        "clarifications": [
            "Ductwork pricing based on spec section 23 31 00",
            "Equipment selections per approved substitution list",
            "Refrigerant pricing based on current market - subject to adjustment",
            "Control points count per attached schedule",
        ],
    }


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Generate complete dataset for all projects."""
    
    all_data = {
        "contracts": [],
        "sov": [],
        "labor_logs": [],
        "material_deliveries": [],
        "change_orders": [],
        "rfis": [],
        "field_notes": [],
        "billing_history": [],
        "bid_estimates": [],
    }
    
    for project in PROJECTS:
        print(f"Generating data for: {project['name']}")
        
        # Generate contract
        contract = generate_contract_value(project)
        all_data["contracts"].append(contract)
        
        contract_value = contract["original_contract_value"]
        start_date = datetime.strptime(contract["contract_date"], "%Y-%m-%d")
        
        # Generate SOV
        sov_lines = generate_sov(project, contract_value)
        all_data["sov"].extend(sov_lines)
        
        # Generate labor logs
        labor_logs = generate_labor_logs(project, sov_lines, start_date)
        all_data["labor_logs"].extend(labor_logs)
        
        # Generate material deliveries
        deliveries = generate_material_deliveries(project, sov_lines, start_date)
        all_data["material_deliveries"].extend(deliveries)
        
        # Generate change orders
        cos = generate_change_orders(project, contract_value, sov_lines, start_date)
        all_data["change_orders"].extend(cos)
        
        # Generate RFIs
        rfis = generate_rfis(project, start_date)
        all_data["rfis"].extend(rfis)
        
        # Generate field notes
        notes = generate_field_notes(project, start_date)
        all_data["field_notes"].extend(notes)
        
        # Generate billing history
        billing = generate_billing_history(project, sov_lines, contract_value, start_date)
        all_data["billing_history"].extend(billing)
        
        # Generate bid estimate
        bid = generate_bid_estimate(project, contract_value, sov_lines)
        all_data["bid_estimates"].append(bid)
    
    # Save outputs
    output_dir = "/home/claude/hvac_dataset"
    
    # Save as JSON
    with open(f"{output_dir}/hvac_construction_dataset.json", "w") as f:
        json.dump(all_data, f, indent=2)
    
    # Save individual CSVs for flat tables
    for table_name in ["contracts", "sov", "labor_logs", "material_deliveries", "change_orders", "rfis", "field_notes"]:
        data = all_data[table_name]
        if data:
            with open(f"{output_dir}/{table_name}.csv", "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
    
    # Billing history needs special handling (nested structure)
    billing_flat = []
    for bill in all_data["billing_history"]:
        bill_copy = {k: v for k, v in bill.items() if k != "line_items"}
        bill_copy["line_item_count"] = len(bill.get("line_items", []))
        billing_flat.append(bill_copy)
    
    with open(f"{output_dir}/billing_history.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=billing_flat[0].keys())
        writer.writeheader()
        writer.writerows(billing_flat)
    
    # Save billing line items separately
    billing_lines = []
    for bill in all_data["billing_history"]:
        for line in bill.get("line_items", []):
            line_copy = line.copy()
            line_copy["project_id"] = bill["project_id"]
            line_copy["application_number"] = bill["application_number"]
            billing_lines.append(line_copy)
    
    if billing_lines:
        with open(f"{output_dir}/billing_line_items.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=billing_lines[0].keys())
            writer.writeheader()
            writer.writerows(billing_lines)
    
    # Print summary
    print("\n" + "="*60)
    print("DATASET GENERATION COMPLETE")
    print("="*60)
    print(f"\nProjects generated: {len(PROJECTS)}")
    print(f"Total contract value: ${sum(c['original_contract_value'] for c in all_data['contracts']):,.0f}")
    print(f"\nRecord counts:")
    for table_name, data in all_data.items():
        if isinstance(data, list):
            print(f"  {table_name}: {len(data):,} records")
    
    print(f"\nFiles saved to: {output_dir}/")


if __name__ == "__main__":
    main()
