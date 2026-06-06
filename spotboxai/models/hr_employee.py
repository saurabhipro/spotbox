# -*- coding: utf-8 -*-

import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError

SSN_PATTERN = re.compile(r'^\d{3}-?\d{2}-?\d{4}$')
EIN_PATTERN = re.compile(r'^\d{2}-?\d{7}$')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Line 2 – Business name (if different from line 1)
    w9_business_name = fields.Char(
        string='Business Name',
        help='Business name / disregarded entity name, if different from the name above.',
    )

    activity_ids = fields.One2many(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    activity_ids = fields.One2many(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    activity_state = fields.Selection(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    activity_user_id = fields.Many2one(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    activity_type_id = fields.Many2one(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    activity_type_icon = fields.Char(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    activity_date_deadline = fields.Date(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    my_activity_date_deadline = fields.Date(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    activity_summary = fields.Char(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    activity_exception_decoration = fields.Selection(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    activity_exception_icon = fields.Char(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")

    # mail.thread mixin
    message_is_follower = fields.Boolean(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    message_follower_ids = fields.One2many(groups="hr.group_hr_user")
    message_partner_ids = fields.Many2many(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    message_ids = fields.One2many(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    has_message = fields.Boolean(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    message_needaction = fields.Boolean(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    message_needaction_counter = fields.Integer(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    message_has_error = fields.Boolean(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    message_has_error_counter = fields.Integer(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")
    message_attachment_count = fields.Integer(groups="hr.group_hr_user,spotboxai.group_hr_employee_own_access")

    # Line 3a – Federal tax classification
    w9_federal_tax_classification = fields.Selection(
        selection=[
            ('individual', 'Individual / sole proprietor or single-member LLC'),
            ('c_corp', 'C Corporation'),
            ('s_corp', 'S Corporation'),
            ('partnership', 'Partnership'),
            ('trust_estate', 'Trust / estate'),
            ('llc', 'Limited liability company (LLC)'),
            ('other', 'Other (see instructions)'),
        ],
        string='Federal Tax Classification',
    )
    w9_llc_classification = fields.Selection(
        selection=[
            ('c', 'C – C corporation'),
            ('s', 'S – S corporation'),
            ('p', 'P – Partnership'),
        ],
        string='LLC Tax Classification',
        help="Tax classification for LLC (enter C, S, or P).",
    )
    w9_other_classification = fields.Char(
        string='Other Classification',
        help='Describe the federal tax classification when "Other" is selected.',
    )

    # Line 3b
    w9_foreign_partners = fields.Boolean(
        string='Foreign Partners, Owners, or Beneficiaries',
        help='Check if the entity has any foreign partners, owners, or beneficiaries.',
    )

    # Line 4 – Exemptions
    w9_exempt_payee_code = fields.Char(string='Exempt Payee Code')
    w9_fatca_exemption_code = fields.Char(string='Exemption from FATCA Reporting Code')

    # Line 7
    w9_account_numbers = fields.Text(
        string='Account Number(s)',
        help='Optional list of account number(s) to establish with the requester.',
    )

    # Part I – Taxpayer Identification Number (TIN)
    w9_tax_id_type = fields.Selection(
        selection=[
            ('ssn', 'Social Security Number (SSN)'),
            ('ein', 'Employer Identification Number (EIN)'),
        ],
        string='Tax ID Type',
    )
    w9_ssn = fields.Char(
        string='Social Security Number',
        groups='hr.group_hr_user',
    )
    w9_ein = fields.Char(
        string='Employer Identification Number',
        groups='hr.group_hr_user',
    )

    # Part II – Certification
    w9_certified = fields.Boolean(
        string='W-9 Certified',
        help='Employee certifies that the information on this form is correct.',
    )
    w9_certification_date = fields.Date(string='Certification Date')
    emp_esign = fields.Binary(
        string='E-Signature',
        attachment=True,
        help='Electronic signature certifying the W-9 information.',
    )
    w9_onboarding_complete = fields.Boolean(
        string='Onboarding Complete',
        compute='_compute_w9_onboarding_complete',
        store=True,
    )

    @api.depends(
        'name',
        'w9_federal_tax_classification',
        'w9_tax_id_type',
        'w9_ssn',
        'w9_ein',
        'private_street',
        'private_city',
        'private_state_id',
        'private_zip',
        'w9_certified',
        'w9_certification_date',
        'emp_esign',
    )
    def _compute_w9_onboarding_complete(self):
        for employee in self:
            has_tin = (
                (employee.w9_tax_id_type == 'ssn' and employee.w9_ssn)
                or (employee.w9_tax_id_type == 'ein' and employee.w9_ein)
            )
            employee.w9_onboarding_complete = bool(
                employee.name
                and employee.w9_federal_tax_classification
                and employee.private_street
                and employee.private_city
                and employee.private_state_id
                and employee.private_zip
                and has_tin
                and employee.w9_certified
                and employee.w9_certification_date
                and employee.emp_esign
            )

    @api.onchange('w9_tax_id_type')
    def _onchange_w9_tax_id_type(self):
        if self.w9_tax_id_type == 'ssn':
            self.w9_ein = False
        elif self.w9_tax_id_type == 'ein':
            self.w9_ssn = False

    @api.onchange('w9_federal_tax_classification')
    def _onchange_w9_federal_tax_classification(self):
        if self.w9_federal_tax_classification != 'llc':
            self.w9_llc_classification = False
        if self.w9_federal_tax_classification != 'other':
            self.w9_other_classification = False

    @api.constrains('w9_federal_tax_classification', 'w9_llc_classification', 'w9_other_classification')
    def _check_w9_tax_classification(self):
        for employee in self:
            if employee.w9_federal_tax_classification == 'llc' and not employee.w9_llc_classification:
                raise ValidationError(
                    'Please select the LLC tax classification (C, S, or P).'
                )
            if employee.w9_federal_tax_classification == 'other' and not employee.w9_other_classification:
                raise ValidationError(
                    'Please describe the federal tax classification when "Other" is selected.'
                )

    @api.constrains('w9_tax_id_type', 'w9_ssn', 'w9_ein')
    def _check_w9_tin(self):
        for employee in self:
            if employee.w9_tax_id_type == 'ssn':
                if not employee.w9_ssn:
                    raise ValidationError('Social Security Number is required when SSN is selected.')
                if not SSN_PATTERN.match(employee.w9_ssn.replace(' ', '')):
                    raise ValidationError(
                        'SSN must be 9 digits (e.g. 123-45-6789).'
                    )
            elif employee.w9_tax_id_type == 'ein':
                if not employee.w9_ein:
                    raise ValidationError(
                        'Employer Identification Number is required when EIN is selected.'
                    )
                if not EIN_PATTERN.match(employee.w9_ein.replace(' ', '')):
                    raise ValidationError(
                        'EIN must be 9 digits (e.g. 12-3456789).'
                    )

    @api.constrains('w9_certified', 'w9_certification_date', 'emp_esign')
    def _check_w9_certification(self):
        for employee in self:
            if employee.w9_certified and not employee.w9_certification_date:
                raise ValidationError(
                    'Certification date is required when W-9 is certified.'
                )
            if employee.w9_certified and not employee.emp_esign:
                raise ValidationError(
                    'E-signature is required when W-9 is certified.'
                )
