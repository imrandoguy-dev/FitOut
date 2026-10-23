import json
import os

import frappe
from frappe.installer import update_site_config

APP = "fitout"
MODULES = ["Fitout"]

# Lifecycle stages a new site starts with. They are only created when the site
# has none, so a site's own stage setup is never overwritten on migrate.
DEFAULT_STAGES = [
	{
		"stage_name": "Enquiry & Requirements",
		"sequence": 1,
		"responsible_role": "Sales Team",
		"require_approval": 0,
		"entry_criteria": "Client enquiry received",
		"exit_criteria": "Brief and site survey recorded",
		"description": "Capture the client brief, site details and survey findings.",
	},
	{
		"stage_name": "Estimation & BOQ",
		"sequence": 2,
		"responsible_role": "Estimation Team",
		"require_approval": 1,
		"entry_criteria": "Brief and site survey recorded",
		"exit_criteria": "Estimate internally approved",
		"description": "Prepare the BOQ, cost the scope and agree the selling price.",
	},
	{
		"stage_name": "Contract Award",
		"sequence": 3,
		"responsible_role": "Account Manager",
		"require_approval": 1,
		"entry_criteria": "Quotation submitted to client",
		"exit_criteria": "Client approval and contract signed",
		"description": "Client approval of the quotation, contract award and budget baseline.",
	},
	{
		"stage_name": "Design & Approvals",
		"sequence": 4,
		"responsible_role": "Design Coordinator",
		"require_approval": 0,
		"entry_criteria": "Contract awarded",
		"exit_criteria": "Drawings and authority permits approved",
		"description": "Coordinate drawings, material submittals and authority approvals.",
	},
	{
		"stage_name": "Procurement",
		"sequence": 5,
		"responsible_role": "Procurement Team",
		"require_approval": 0,
		"entry_criteria": "Material submittals approved",
		"exit_criteria": "Long-lead materials ordered",
		"description": "Order materials and award subcontract packages against the baseline budget.",
	},
	{
		"stage_name": "Site Execution",
		"sequence": 6,
		"responsible_role": "Project Manager",
		"require_approval": 1,
		"entry_criteria": "Client Approval Completed",
		"exit_criteria": "Key Work Packages Completed",
		"description": "Execute the approved scope on site including coordination with subcontractors, inspections and progress tracking.",
	},
	{
		"stage_name": "Commercial Review",
		"sequence": 7,
		"responsible_role": "Commercial / QS Team",
		"require_approval": 0,
		"entry_criteria": "Key work packages completed",
		"exit_criteria": "Final measurement and variations agreed",
		"description": "Agree final measurements, variations and the final account.",
	},
	{
		"stage_name": "Handover & Closure",
		"sequence": 8,
		"responsible_role": "Project Manager",
		"require_approval": 1,
		"entry_criteria": "Snags rectified",
		"exit_criteria": "Client handover recorded",
		"description": "Close snags, hand over documents and record client acceptance.",
	},
]

DEFAULT_SETTINGS = {
	"variation_approval_threshold": 10000,
	"additional_approver": "Managing Director",
	"commercial_reviewer": "Commercial Manager",
	"require_client_approval": 1,
	"due_soon_days": 3,
	"handover_window_days": 60,
	"materials_keywords": "material,stock,cost of goods,cogs,purchase",
	"labour_keywords": "labour,labor,salary,wage,payroll",
	"subcontract_keywords": "subcontract,sub-contract,contractor",
}


def after_install():
	enable_server_scripts()
	create_module_defs()
	ensure_shared_custom_fields()
	seed_workflow_stages()
	seed_settings()
	sync_stage_options()
	frappe.db.commit()


def after_migrate():
	create_module_defs()
	ensure_shared_custom_fields()
	seed_workflow_stages()
	# Fixtures reset Project "Fit Out Stage" options to the shipped list on every
	# migrate; put back the site's own configured stages.
	sync_stage_options()
	frappe.db.commit()


def enable_server_scripts():
	"""All Fit Out logic (Command Centre APIs, BOQ totals, lifecycle sync...) runs
	as Server Scripts. Frappe silently skips every Server Script unless
	`server_script_enabled` is set in site_config.json.
	"""
	if frappe.conf.get("server_script_enabled"):
		return
	try:
		update_site_config("server_script_enabled", 1)
	except Exception:
		frappe.log_error(
			title="fitout: could not enable server scripts",
			message="Set 'server_script_enabled': 1 in site_config.json manually.",
		)


def create_module_defs():
	"""Claim the Fitout module for this app, also on sites where it was built by
	hand first (a custom Module Def owned by another app)."""
	for module_name in MODULES:
		existing = frappe.db.get_value(
			"Module Def", module_name, ["app_name", "package", "custom"], as_dict=True
		)
		if existing:
			if existing.app_name != APP or existing.package or existing.custom:
				frappe.db.set_value(
					"Module Def", module_name, {"app_name": APP, "package": None, "custom": 0}
				)
			continue
		doc = frappe.new_doc("Module Def")
		doc.module_name = module_name
		doc.app_name = APP
		doc.custom = 0
		doc.insert(ignore_permissions=True)


def ensure_shared_custom_fields():
	"""Project Manager, Contract Value (Project) and Assign To (Task) are generic
	names other apps or hand-made setups often already have. Create them only when
	missing, so an existing field of the same name is never overwritten."""
	path = os.path.join(os.path.dirname(__file__), "setup", "shared_custom_fields.json")
	with open(path) as fh:
		fields = json.load(fh)

	for df in fields:
		if not frappe.db.exists("DocType", df["dt"]):
			continue
		if frappe.get_meta(df["dt"]).has_field(df["fieldname"]):
			continue
		doc = frappe.new_doc("Custom Field")
		doc.update(df)
		doc.module = "Fitout"
		doc.insert(ignore_permissions=True)


def seed_workflow_stages():
	if frappe.db.count("Fit Out Workflow Stage"):
		return
	for row in DEFAULT_STAGES:
		doc = frappe.new_doc("Fit Out Workflow Stage")
		doc.update(row)
		doc.is_active = 1
		doc.flags.ignore_permissions = True
		doc.insert()


def seed_settings():
	settings = frappe.get_single("Fit Out Settings")
	changed = False
	for key, value in DEFAULT_SETTINGS.items():
		if settings.meta.has_field(key) and not settings.get(key):
			settings.set(key, value)
			changed = True
	if changed:
		settings.flags.ignore_permissions = True
		settings.save()


def sync_stage_options():
	"""Keep Project > Fit Out Stage options in step with the active lifecycle
	stages (same rule as the 'Fit Out Workflow Stage - Sync Options' script)."""
	if not frappe.db.exists("Custom Field", "Project-fo_stage"):
		return
	stages = frappe.get_all(
		"Fit Out Workflow Stage",
		filters={"is_active": 1},
		pluck="stage_name",
		order_by="sequence asc",
	)
	if not stages:
		return
	options = "\n" + "\n".join(stages) + "\nCompleted"
	if frappe.db.get_value("Custom Field", "Project-fo_stage", "options") != options:
		cf = frappe.get_doc("Custom Field", "Project-fo_stage")
		cf.options = options
		cf.save(ignore_permissions=True)
