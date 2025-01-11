# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt


from press.api.site import get_domain


def get_context(context):
	domain = "mbwnext.com"  #get_domain()
	context.domain = domain
	return context
