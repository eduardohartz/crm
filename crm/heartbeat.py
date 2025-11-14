import frappe
from frappe.utils import now_datetime

@frappe.whitelist()
def ping():
    user = frappe.session.user
    if user == "Guest":
        return {"ok": False}

    frappe.db.set_value("User", user, "last_active", now_datetime())
    frappe.db.commit()
    return {"ok": True}