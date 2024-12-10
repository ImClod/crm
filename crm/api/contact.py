import frappe
from frappe import _
from frappe.utils import nowdate, getdate  # type: ignore

def validate(doc, method):
	set_primary_email(doc)
	set_primary_mobile_no(doc)
	doc.set_primary_email()
	doc.set_primary("mobile_no")
	update_deals_email_mobile_no(doc)


def set_primary_email(doc):
	if not doc.email_ids:
		return

	if len(doc.email_ids) == 1:
		doc.email_ids[0].is_primary = 1


def set_primary_mobile_no(doc):
	if not doc.phone_nos:
		return

	if len(doc.phone_nos) == 1:
		doc.phone_nos[0].is_primary_mobile_no = 1


def update_deals_email_mobile_no(doc):
	linked_deals = frappe.get_all(
		"CRM Contacts",
		filters={"contact": doc.name, "is_primary": 1},
		fields=["parent"],
	)

	for linked_deal in linked_deals:
		deal = frappe.get_cached_doc("CRM Deal", linked_deal.parent)
		if deal.email != doc.email_id or deal.mobile_no != doc.mobile_no:
			deal.email = doc.email_id
			deal.mobile_no = doc.mobile_no
			deal.save(ignore_permissions=True)


@frappe.whitelist()
def get_scheduled_calls():
    """
    Retrieve scheduled calls for today that haven't been called yet
    """

    # Ottieni la data di oggi
    today = getdate(nowdate())

    # Recupera i contatti con date corrispondenti a oggi
    contacts = frappe.get_all(
        "CRM Contact",
        filters=[
            ["custom_first_date", "=", today],
            ["custom_creation_date", "=", today],
            ["custom_second_date", "=", today],
        ],
        fields=[
            "name",
            "first_name",
            "last_name",
            "email",
            "mobile_no",
            "custom_creation_date",
            "custom_first_date",
            "custom_second_date",
        ],
    )

    # Filtra i contatti che non hanno chiamate oggi
    scheduled_calls = []
    for contact in contacts:
        # Verifica se esiste già un call log per questo contatto oggi
        existing_call_logs = frappe.get_all(
            "CRM Call Log",
            filters={
                "reference_doctype": "Contact",
                "reference_docname": contact["name"],
                "creation": ["between", [today + " 00:00:00", today + " 23:59:59"]],
            },
        )

        # Se non esistono call log, aggiungi alle chiamate pianificate
        if not existing_call_logs:
            scheduled_calls.append(
                {
                    "name": contact.get("name"),
                    "full_name": f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
                    "email": contact.get("email"),
                    "mobile_no": contact.get("mobile_no"),
                    "custom_first_date": frappe.utils.format_date(contact.get("custom_first_date")),
                    "custom_creation_date": frappe.utils.format_date(contact.get("custom_creation_date")),
                    "custom_second_date": frappe.utils.format_date(contact.get("custom_second_date")),
                }
            )

    return scheduled_calls
@frappe.whitelist()
def mark_call_status(contact, status):
    """Log call status and create call log"""
    try:
        # Crea log chiamata
        call_log = frappe.new_doc('CRM Call Log')
        
        # Genera un ID univoco
        import uuid
        unique_id = str(uuid.uuid4())[:12]  # Usa UUID per generare ID univoco
        
        call_log.update({
            'id': unique_id,  # Aggiungi ID univoco
            'caller': frappe.session.user,
            'to': contact,
            'type': 'Outgoing',
            'status': status,
            'start_time': frappe.utils.now(),
            'end_time': frappe.utils.now(),
            'reference_doctype': 'Contact',
            'reference_docname': contact
        })
        call_log.insert(ignore_permissions=True)
        
        # Pubblica evento in tempo reale per sincronizzazione
        frappe.publish_realtime('scheduled_call_updated', {
            'contact': contact,
            'status': status
        })
        
        frappe.db.commit()
        
        return {
            'status': 'success', 
            'message': f'Call marked as {status} for {contact}'
        }
    
    except Exception as e:
        frappe.log_error(f"Error marking call status: {str(e)}")
        frappe.db.rollback()
        return {
            'status': 'error', 
            'message': f'Failed to mark call: {str(e)}'
        }
@frappe.whitelist()
def get_contact(name):
	Contact = frappe.qb.DocType("Contact")

	query = (
		frappe.qb.from_(Contact)
		.select("*")
		.where(Contact.name == name)
		.limit(1)
	)

	contact = query.run(as_dict=True)
	if not len(contact):
		frappe.throw(_("Contact not found"), frappe.DoesNotExistError)
	contact = contact.pop()

	contact["doctype"] = "Contact"
	contact["email_ids"] = frappe.get_all(
		"Contact Email", filters={"parent": name}, fields=["name", "email_id", "is_primary"]
	)
	contact["phone_nos"] = frappe.get_all(
		"Contact Phone", filters={"parent": name}, fields=["name", "phone", "is_primary_mobile_no"]
	)
	return contact

@frappe.whitelist()
def get_linked_deals(contact):
	"""Get linked deals for a contact"""

	if not frappe.has_permission("Contact", "read", contact):
		frappe.throw("Not permitted", frappe.PermissionError)

	deal_names = frappe.get_all(
		"CRM Contacts",
		filters={"contact": contact, "parenttype": "CRM Deal"},
		fields=["parent"],
		distinct=True,
	)

	# get deals data
	deals = []
	for d in deal_names:
		deal = frappe.get_cached_doc(
			"CRM Deal",
			d.parent,
			fields=[
				"name",
				"organization",
				"currency",
				"annual_revenue",
				"status",
				"email",
				"mobile_no",
				"deal_owner",
				"modified",
			],
		)
		deals.append(deal.as_dict())

	return deals


@frappe.whitelist()
def create_new(contact, field, value):
	"""Create new email or phone for a contact"""
	if not frappe.has_permission("Contact", "write", contact):
		frappe.throw("Not permitted", frappe.PermissionError)

	contact = frappe.get_doc("Contact", contact)

	if field == "email":
		contact.append("email_ids", {"email_id": value})
	elif field in ("mobile_no", "phone"):
		contact.append("phone_nos", {"phone": value})
	else:
		frappe.throw("Invalid field")

	contact.save()
	return True


@frappe.whitelist()
def set_as_primary(contact, field, value):
	"""Set email or phone as primary for a contact"""
	if not frappe.has_permission("Contact", "write", contact):
		frappe.throw("Not permitted", frappe.PermissionError)

	contact = frappe.get_doc("Contact", contact)

	if field == "email":
		for email in contact.email_ids:
			if email.email_id == value:
				email.is_primary = 1
			else:
				email.is_primary = 0
	elif field in ("mobile_no", "phone"):
		name = "is_primary_mobile_no" if field == "mobile_no" else "is_primary_phone"
		for phone in contact.phone_nos:
			if phone.phone == value:
				phone.set(name, 1)
			else:
				phone.set(name, 0)
	else:
		frappe.throw("Invalid field")

	contact.save()
	return True


@frappe.whitelist()
def search_emails(txt: str):
	doctype = "Contact"
	meta = frappe.get_meta(doctype)
	filters = [["Contact", "email_id", "is", "set"]]

	if meta.get("fields", {"fieldname": "enabled", "fieldtype": "Check"}):
		filters.append([doctype, "enabled", "=", 1])
	if meta.get("fields", {"fieldname": "disabled", "fieldtype": "Check"}):
		filters.append([doctype, "disabled", "!=", 1])

	or_filters = []
	search_fields = ["full_name", "email_id", "name"]
	if txt:
		for f in search_fields:
			or_filters.append([doctype, f.strip(), "like", f"%{txt}%"])

	results = frappe.get_list(
		doctype,
		filters=filters,
		fields=search_fields,
		or_filters=or_filters,
		limit_start=0,
		limit_page_length=20,
		order_by='email_id, full_name, name',
		ignore_permissions=False,
		as_list=True,
		strict=False,
	)

	return results