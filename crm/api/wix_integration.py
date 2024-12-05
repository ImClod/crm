import frappe
import json
from frappe import _
from frappe.utils import validate_email_address
from crm.fcrm.doctype.crm_lead.crm_lead import convert_to_deal

@frappe.whitelist(allow_guest=True)
def create_lead_from_wix():
    """
    Create a new lead from Wix form submission and convert it to a deal.
    Expected POST data format:
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "mobile_no": "+1234567890",
        "organization": "Company Name",
        "website": "www.example.com",
        "notes": "Additional information"
    }
    """
    try:
        frappe.set_user("Administrator")  # Set admin privileges for all operations
        
        # Get JSON data from request
        data = json.loads(frappe.request.data)
        validate_lead_data(data)
        
        # Create lead
        lead = create_new_lead(data)
        
        # Convert lead to deal using the CRM's built-in conversion function
        lead_doc = frappe.get_doc("CRM Lead", lead.name)
        lead_doc.flags.ignore_permissions = True
        deal = convert_to_deal(lead=lead_doc.name, doc=lead_doc)
        
        response = {
            "status": "success",
            "message": _("Lead created and converted to deal successfully"),
            "data": {
                "lead_id": lead_doc.name,
                "deal_id": deal
            }
        }
            
        return response
        
    except Exception as e:
        frappe.log_error(f"Wix Lead Creation Error: {str(e)}", "Wix Integration")
        return {
            "status": "error",
            "message": str(e)
        }

def validate_lead_data(data):
    frappe.throw(_(f"Wix Lead Creation Error: {data}"))
    """Validate the incoming lead data"""
    # Allow creation even if some fields are missing
    if not (data.get("email") or data.get("mobile_no")):
        frappe.throw(_("At least one of email, mobile number."))

    if data.get("email") and not validate_email_address(data.get("email")):
        frappe.throw(_("Invalid email address"))
        
    if not data.get("first_name") and not data.get("last_name"):
        frappe.throw(_("At least first name or last name is required"))

def create_new_lead(data):
    """Create a new lead from the validated data"""
    lead = frappe.new_doc("CRM Lead")
    
    # Map basic information
    lead.first_name = data.get("first_name")
    lead.last_name = data.get("last_name")
    lead.email = data.get("email")
    lead.mobile_no = data.get("mobile_no")
    
    # Check organization name and set it
    organization_name = data.get("organization")
    if not organization_name or organization_name.strip() == "":
        organization_name = f"{lead.first_name} {lead.last_name}"
    lead.organization = organization_name
    
    lead.website = data.get("website")
    lead.notes = data.get("notes")
    
    # Check if the source exists, if not create it
    if not frappe.db.exists("CRM Lead Source", "Wix Website"):
        source_doc = frappe.new_doc("CRM Lead Source")
        source_doc.source_name = "Wix Website"
        source_doc.insert(ignore_permissions=True)
        frappe.db.commit()
    
    # Set source and status
    lead.source = "Wix Website"
    lead.status = "New"
    
    # Save the lead
    lead.flags.ignore_permissions = True
    lead.insert()
    frappe.db.commit()
    
    return lead
