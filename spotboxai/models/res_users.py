# -*- coding: utf-8 -*-

from odoo import Command, api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if self.env.context.get('from_hr_users_menu'):
            own_group = self.env.ref(
                'spotboxai.group_hr_employee_own_access', raise_if_not_found=False,
            )
            if own_group:
                defaults['groups_id'] = [Command.set([own_group.id])]
        return defaults

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get('from_hr_users_menu'):
            own_group = self.env.ref('spotboxai.group_hr_employee_own_access')
            for vals in vals_list:
                vals['create_employee'] = True
                vals['groups_id'] = [Command.set([own_group.id])]
                if vals.get('login') and not vals.get('email'):
                    vals['email'] = vals['login']
        return super().create(vals_list)
