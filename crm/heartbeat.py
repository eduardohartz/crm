import frappe
from frappe.utils import now_datetime, add_to_date

@frappe.whitelist()
def ping():
    user = frappe.session.user
    if user == "Guest":
        return {"ok": False}

    # Mark active
    frappe.db.set_value("User", user, "last_active", now_datetime())

    # Try to assign 1 queued lead
    try_assign_queued_lead(user)

    frappe.db.commit()
    return {"ok": True}


def user_has_role(user, role_name):
    user = frappe.session.user
    user_doc = frappe.get_doc("User", user)
    roles = {r.role for r in user_doc.roles}
    return role_name in roles


def try_assign_queued_lead(user):
    # Only Sales User should receive queued leads
    if not user_has_role(user, "Sales User"):
        return

    now = now_datetime()
    five_minutes_ago = add_to_date(now, minutes=-5, as_datetime=True)

    # Find last assigned queue entry for this user
    last_assigned = frappe.get_all(
        "Lead Assignment Queue",
        filters={
            "assigned_to": user,
            "status": "Assigned",
        },
        fields=["assigned_at"],
        order_by="assigned_at desc",
        limit=1,
    )

    if last_assigned:
        last_time = last_assigned[0].get("assigned_at")
        if last_time and last_time > five_minutes_ago:
            return  # Too soon to receive another lead

    # Fetch oldest queued item
    queue_item = frappe.get_all(
        "Lead Assignment Queue",
        filters={"status": "Queued"},
        fields=["name", "lead"],
        order_by="creation asc",
        limit=1,
    )

    if not queue_item:
        return

    queue_item = queue_item[0]
    lead_name = queue_item["lead"]

    # Double-check lead still has no owner + correct status
    lead_doc = frappe.get_doc("CRM Lead", lead_name)

    if lead_doc.lead_owner or lead_doc.status != "Aguardando Atendimento":
        # Mark queue as consumed (but it was already assigned or changed)
        frappe.db.set_value(
            "Lead Assignment Queue",
            queue_item["name"],
            {
                "status": "Assigned",
                "assigned_to": lead_doc.lead_owner or "",
                "assigned_at": now,
            },
        )
        return

    # Assign lead to current user
    frappe.db.set_value("CRM Lead", lead_name, "lead_owner", user)
    frappe.db.set_value("CRM Lead", lead_name, "status", "Em atendimento")

    # Update queue row
    frappe.db.set_value(
        "Lead Assignment Queue",
        queue_item["name"],
        {
            "status": "Assigned",
            "assigned_to": user,
            "assigned_at": now,
        },
    )

    # Add comment
    lead_doc.add_comment(
        "Comment",
        f"Lead distribuído da fila para {user} pelo heartbeat."
    )