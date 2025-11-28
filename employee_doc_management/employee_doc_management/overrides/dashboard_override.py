from frappe import _


def get_dashboard_for_employee(data):
    #insert at the beginning of data
    data["transactions"].insert(0,
        {
				"label": _("Documents"),
				"items": [
					"Employee Document",
				],
		},)
    return data
    