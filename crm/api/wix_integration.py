import frappe
import json
from frappe import _
from frappe.utils import validate_email_address

@frappe.whitelist(allow_guest=True)
def create_lead_from_wix():
    """
    Create a new lead from Wix form submission.
    Expected POST data format:
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "mobile_no": "+1234567890",
        "organization": "Company Name",
        "website": "www.example.com",
        "notes": "Additional information",
        "create_deal": true,
        "deal_value": 1000
    }
    """
    try:
        # Get JSON data from request
        data = json.loads(frappe.request.data)
        validate_lead_data(data)
        
        # Create lead
        lead = create_new_lead(data)
        
        # Create deal if requested
        deal = None
        if data.get("create_deal"):
            deal = create_deal_from_lead(lead, data)
        
        response = {
            "status": "success",
            "message": _("Lead created successfully"),
            "data": {
                "lead_id": lead.name
            }
        }
        
        if deal:
            response["data"]["deal_id"] = deal.name
            
        return response
        
    except Exception as e:
        frappe.log_error(f"Wix Lead Creation Error: {str(e)}", "Wix Integration")
        return {
            "status": "error",
            "message": str(e)
        }

def validate_lead_data(data):
    """Validate the incoming lead data"""
    if not data.get("email"):
        frappe.throw(_("Email is required"))
        
    if not validate_email_address(data.get("email")):
        frappe.throw(_("Invalid email address"))
        
    if not data.get("first_name"):
        frappe.throw(_("First name is required"))

def create_new_lead(data):
    """Create a new lead from the validated data"""
    lead = frappe.new_doc("CRM Lead")
    
    # Map basic information
    lead.first_name = data.get("first_name")
    lead.last_name = data.get("last_name")
    lead.email = data.get("email")
    lead.mobile_no = data.get("mobile_no")
    lead.organization = data.get("organization")
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
    lead.insert(ignore_permissions=True)
    frappe.db.commit()
    
    return lead

def create_organization(organization_name):
    """Create a new organization if it doesn't exist"""
    if not organization_name:
        return None
        
    if not frappe.db.exists("CRM Organization", {"organization_name": organization_name}):
        org = frappe.new_doc("CRM Organization")
        org.organization_name = organization_name
        org.insert(ignore_permissions=True)
        frappe.db.commit()
        return org.name
    else:
        return frappe.get_value("CRM Organization", {"organization_name": organization_name}, "name")

def create_deal_from_lead(lead, data):
    """Create a deal associated with the lead"""
    try:
        # First, ensure organization exists
        organization_name = None
        if lead.organization:
            organization_name = create_organization(lead.organization)
        
        # Create a new deal
        deal = frappe.new_doc("CRM Deal")
        
        # Map lead information to deal
        if organization_name:
            deal.organization = organization_name
            
        # Set contact information
        deal.first_name = lead.first_name
        deal.last_name = lead.last_name
        deal.email = lead.email
        deal.mobile_no = lead.mobile_no
        
        # Set deal specific information
        deal.status = "Qualification"  # Default status for new deals
        deal.deal_owner = frappe.session.user
        deal.source = "Wix Website"
        
        # Set deal value if provided
        if data.get("deal_value"):
            deal.deal_value = float(data.get("deal_value"))
        
        # Save the deal with ignore permissions
        deal.flags.ignore_permissions = True
        deal.insert()
        
        # Commit the transaction
        frappe.db.commit()
        
        return deal
        
    except Exception as e:
        error_msg = f"Deal Creation Error: {str(e)}"
        frappe.log_error(error_msg, "Wix Integration")
        raise frappe.ValidationError(error_msg)
