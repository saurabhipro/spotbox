# -*- coding: utf-8 -*-

from odoo import models


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def _load_menus_blacklist(self):
        res = super()._load_menus_blacklist()
        user = self.env.user
        if not user.has_group('base.group_system'):
            apps_menu = self.env.ref('base.menu_management', raise_if_not_found=False)
            if apps_menu:
                res.append(apps_menu.id)
        if user.has_group('spotboxai.group_hr_employee_own_access') and user.has_group('hr.group_hr_user'):
            menu = self.env.ref('spotboxai.menu_hr_employee_own', raise_if_not_found=False)
            if menu:
                res.append(menu.id)
        elif user.has_group('spotboxai.group_hr_employee_own_access'):
            for menu_xmlid in ('hr.menu_hr_department_kanban',):
                menu = self.env.ref(menu_xmlid, raise_if_not_found=False)
                if menu:
                    res.append(menu.id)
        return res
