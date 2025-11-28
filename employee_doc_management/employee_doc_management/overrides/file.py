
import frappe
import shutil
from frappe import _
from frappe.core.doctype.file.file import File
from frappe.core.doctype.file.utils import update_existing_file_docs, find_file_by_url
from frappe.utils import (
    cint
)


class FileOverride(File):
    def rename_to(self, new_filename):
        if self.is_remote_file:
            return

        from pathlib import Path

        old_file_url = self.file_url
        old_filename = self.file_url.split("/")[-1]
        # file_name = new_filename
        private_file_path_new = Path(frappe.get_site_path("private", "files", new_filename))
        private_file_path_old = Path(frappe.get_site_path("private", "files", old_filename))
        public_file_path_new = Path(frappe.get_site_path("public", "files", new_filename))
        public_file_path_old = Path(frappe.get_site_path("public", "files", old_filename))

        if cint(self.is_private):
            source = private_file_path_old
            target = private_file_path_new
            url_starts_with = "/private/files/"
        else:
            source = public_file_path_old
            target = public_file_path_new
            url_starts_with = "/files/"
        updated_file_url = f"{url_starts_with}{new_filename}"

        # if a file document is created by passing dict throught get_doc and __local is not set,
        # handle_is_private_changed would be executed; we're checking if updated_file_url is same
        # as old_file_url to avoid a FileNotFoundError for this case.
        if updated_file_url == old_file_url:
            return

        if not source.exists():
            frappe.throw(
                _("Cannot find file {} on disk").format(source),
                exc=FileNotFoundError,
            )
        if target.exists():
            frappe.throw(
                _("A file with same name {} already exists").format(target),
                exc=FileExistsError,
            )

        # Uses os.rename which is an atomic operation
        shutil.move(source, target)
        self.flags.original_path = {"old": source, "new": target}
        frappe.db.after_rollback.add(self.on_rollback)

        self.file_url = updated_file_url
        self.file_name = new_filename
        update_existing_file_docs(self)