1. The Operations Proxy: NYC Housing Work Orders
Best for: Labor logs, Material deliveries, Field notes, RFI context.
This dataset tracks maintenance tickets in New York City public housing. It is the closest real-world equivalent to a "mechanical contractor's service log."

Dataset: NYC Housing Authority (NYCHA) Work Orders
https://www.google.com/search?q=https://data.cityofnewyork.us/Housing-Development/Work-Orders/59rp-2kjs

Volume: ~2.5M+ rows (updated daily)

Mapping to Your Needs:

Labor Logs: Use WO_Type (Emergency/Routine) + Duration (Calculated from Created_Date vs Completed_Date).

Field Notes: The Description field often contains unstructured text like "Leak in ceiling, crew arrived, parts missing."

Material Deliveries: Proxied by Status changes (e.g., "Pending Material" status codes).

RFI Logs: Use Delay_Reason (e.g., "Access Denied," "Awaiting Approval") to simulate RFI blockers.

2. The Financial Proxy: Federal Construction Contracts (USAspending)
Best for: Project contract values, Progress billing, Change order requests.
Federal contracts require strict reporting on "modifications" (Change Orders). You can download raw CSVs of specific construction NAICS codes (238220 for HVAC).

Dataset: USAspending.gov (Custom Download)
https://www.usaspending.gov/download_center/custom_award_data

Filter Instructions:

Award Type: Contracts

NAICS: 238220 (Plumbing, Heating, and Air-Conditioning Contractors)

Mapping to Your Needs:

Project Contract Values: Total_Obligated_Amount.

Change Order Requests: Look at the Modification_Number column. Each increment (Mod 1, Mod 2) represents a change.

Progress Billing: Action_Date + Federal_Action_Obligation shows the cash flow history over time.

Original Bid Assumptions: Base_And_Exercised_Options_Value vs. Current_Total_Value.

3. The "Schedule of Values" Proxy: GSA Schedule Rates
Best for: Schedule of Values (SOV) line items, Bid estimates.
The GSA publishes the labor rates and unit prices that contractors are allowed to charge the government. This gives you the "line item" granularity missing from the other datasets.

Dataset: GSA CALC (Contract Awarded Labor Category) (Exportable as CSV)
https://calc.gsa.gov/

Mapping to Your Needs:

Schedule of Values (SOV): Use the Labor_Category (e.g., "HVAC Technician," "Sheet Metal Worker") and Price columns to build a realistic SOV.

Bid Estimate Assumptions: The Experience and Education columns explain why a rate is priced the way it is.
