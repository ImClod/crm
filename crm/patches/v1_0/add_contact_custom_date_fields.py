import frappe
from crm.install import add_contact_custom_fields

def execute():
    """Add custom date fields to Contact doctype"""
    add_contact_custom_fields()
