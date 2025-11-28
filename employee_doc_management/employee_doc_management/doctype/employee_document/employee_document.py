# Copyright (c) 2025, Itrostack LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from frappe import _
from frappe.utils import getdate
from frappe.core.doctype.file.utils import find_file_by_url
from frappe.core.api.file import create_new_folder

class EmployeeDocument(Document):
	def before_save(self):
		company=frappe.defaults.get_user_default("Company")
		print(company)
		# company=frappe.get_doc("Company", company_name)
		root_folder = 'Home'
		if company:
			rf = frappe.db.get_value("Company", company, "custom_employee_document_folder")
			if rf:
				root_folder = rf	
		#custom_employee_document_folder
		folder_path = root_folder+'/'+self.employee
		
		filters = {"name": folder_path}
		#TODO Optimize Later with get_cached_value
		folder = frappe.db.get_value("File", filters, ["name"])
		if not folder:
			create_new_folder(self.employee,root_folder)

		if self.front_side:
			self.front_side = self.rename_and_save(self.front_side, folder_path, "front")
		if self.back_side:
			self.back_side = self.rename_and_save(self.back_side, folder_path, "back")
	
	#Rename and Save to a Target Folder
	def rename_and_save(self,file,folder_path,file_suffix):
		f=find_file_by_url(file)
		_, file_extension = f.get_extension()
		new_file_name = f"{self.name}_{self.document_type}_{file_suffix}{file_extension}"
		
		f.rename_to(new_file_name)
		f.folder = folder_path
		f.save()
		return f.file_url