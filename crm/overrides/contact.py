# import frappe
from frappe import _
import frappe
from frappe.contacts.doctype.contact.contact import Contact
from datetime import datetime, timedelta

class CustomContact(Contact):
    def validate(self):
        super().validate()
        self.set_custom_dates()

    def set_custom_dates(self):
        # Set creation date if not already set
        if not self.custom_creation_date:
            self.custom_creation_date = frappe.utils.today()
            self.custom_creation_date = self.get_next_business_day(self.custom_creation_date)

        # Calculate first date (2 business days after creation)
        if not self.custom_first_date or self.has_value_changed('custom_creation_date'):
            self.custom_first_date = self.add_business_days(self.custom_creation_date, 2)

        # Calculate second date (4 business days after first date)
        if not self.custom_second_date or self.has_value_changed('custom_first_date'):
            self.custom_second_date = self.add_business_days(self.custom_first_date, 4)

    def get_next_business_day(self, start_date_str):
        """Ensure the given start date is a business day. If not, move forward until you find one."""
        if isinstance(start_date_str, str):
            current_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            current_date = start_date_str

        while current_date.weekday() >= 5 or self.is_holiday(current_date):
            current_date += timedelta(days=1)
        return current_date.strftime('%Y-%m-%d')

    def add_business_days(self, start_date, days):
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        current_date = start_date
        remaining_days = days

        while remaining_days > 0:
            current_date += timedelta(days=1)

            # Skip weekends
            if current_date.weekday() >= 5:
                continue

            # Skip holidays
            if self.is_holiday(current_date):
                continue

            remaining_days -= 1

        return current_date.strftime('%Y-%m-%d')

    def is_holiday(self, date):
        # Get active holiday list
        holiday_list = frappe.get_all('CRM Holiday List', 
            filters={
                'from_date': ['<=', date],
                'to_date': ['>=', date]
            }, 
            limit=1)

        if not holiday_list:
            return False

        # Check if date is a holiday
        holiday = frappe.get_all('CRM Holiday',
            filters={
                'parent': holiday_list[0].name,
                'date': date.strftime('%Y-%m-%d')
            },
            limit=1)

        return bool(holiday)

    @staticmethod
    def default_list_data():
        columns = [
            {
                'label': 'Name',
                'type': 'Data',
                'key': 'full_name',
                'width': '17rem',
            },
            {
                'label': 'Email',
                'type': 'Data',
                'key': 'email_id',
                'width': '12rem',
            },
            {
                'label': 'Phone',
                'type': 'Data',
                'key': 'mobile_no',
                'width': '12rem',
            },
            {
                'label': 'Organization',
                'type': 'Data',
                'key': 'company_name',
                'width': '12rem',
            },
            {
                'label': 'Last Modified',
                'type': 'Datetime',
                'key': 'modified',
                'width': '8rem',
            },
        ]
        rows = [
            "name",
            "full_name",
            "company_name",
            "email_id",
            "mobile_no",
            "modified",
            "image",
        ]
        return {'columns': columns, 'rows': rows}
