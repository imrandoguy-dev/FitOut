app_name = "fitout"
app_title = "Fit Out"
app_publisher = "Hipersign Technologies"
app_description = "Fit-out project management for ERPNext: estimation & BOQ, procurement, site execution, variations, document control and handover"
app_email = "support@hipersignerp.com"
app_license = "mit"

required_apps = ["erpnext"]

app_logo_url = "/assets/fitout/images/fitout_logo.png"

after_install = "fitout.install.after_install"
after_migrate = "fitout.install.after_migrate"

# ------------------------------------------------------------------------------
# What the app ships (exported from construction.hipersignerp.cloud /desk/fit-out)
# ------------------------------------------------------------------------------

FITOUT_CUSTOM_FIELDS = [
	"Project-fo_section",
	"Project-fo_is_fitout",
	"Project-fo_stage",
	"Project-fo_col1",
	"Project-fo_location",
	"Project-fo_health",
	"Project-fo_health_note",
	"Project-fo_image",
	"Project-fo_lifecycle_section",
	"Project-fo_stages",
	"Project-fo_details_section",
	"Project-fo_fitout_category",
	"Project-fo_subcontractor_package",
	"Project-fo_inspection_requirement",
	"Project-fo_col2",
	"Project-fo_client_approval_ref",
	"Project-fo_drawing_revision",
	"Project-fo_material_readiness",
	"Project-fo_forecast_section",
	"Project-fo_ctc",
	"Task-fo_stage",
	"Task-fo_work_package",
	"Quotation-fo_boq",
]

FITOUT_SERVER_SCRIPTS = [
	# APIs used by the Fit Out Command Centre
	"Hipersign Fitout Dashboard API",
	"Hipersign Fitout Portfolio API",
	"Hipersign Fitout Project API",
	"Hipersign Fitout BOQ API",
	"Hipersign Fitout Procurement API",
	"Hipersign Fitout Execution API",
	"Hipersign Fitout Commercial API",
	"Hipersign Fitout Closeout API",
	# Document events
	"Fit Out - Sync Lifecycle Stages",
	"Fit Out BOQ - Calculate",
	"Fit Out BOQ - Revision Number",
	"Fit Out BOQ - Quotation Link",
	"Fit Out BOQ - Quotation Submitted",
	"Fit Out Work Package - Calculate",
	"Fit Out Work Package - Task Progress",
	"Fit Out Inspection - Sign Off",
	"Fit Out Inspection - Update Package",
	"Fit Out Variation - Approval Rules",
	"Fit Out Handover - Readiness",
	"Fit Out Workflow Stage - Sync Options",
]

# Order matters: the HTML block must exist before the Workspace that embeds it,
# and the Workspace before the Sidebar that links to it.
fixtures = [
	{"dt": "Custom Field", "filters": [["name", "in", FITOUT_CUSTOM_FIELDS]]},
	{"dt": "Server Script", "filters": [["name", "in", FITOUT_SERVER_SCRIPTS]]},
	{"dt": "Custom HTML Block", "filters": [["name", "in", ["Fitout Command Centre"]]]},
	{"dt": "Workspace", "filters": [["name", "in", ["Fit Out"]]]},
	{"dt": "Workspace Sidebar", "filters": [["name", "in", ["Fit Out"]]]},
]
