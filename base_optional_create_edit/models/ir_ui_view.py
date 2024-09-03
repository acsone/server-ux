# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, models


class Model(models.AbstractModel):
    _inherit = "base"

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        views = res.get("views")
        view_form = views["form"]["arch"]
        tree = etree.fromstring(view_form)
        view_fields = set(tree.xpath(".//field[not(ancestor::field)]"))

        field_names = []
        for field_name, model in self._fields.items():
            if model.relational:
                ir_model = self.env["ir.model"].search(
                    [("model", "=", model.comodel_name)]
                )
                if ir_model.avoid_create_edit:
                    field_names.append(field_name)

        for view_field in view_fields:
            if view_field.attrib["name"] in field_names:
                view_field.set("can_create", "false")
                view_field.set("can_write", "false")
                view_field.set("no_create", "true")
                view_field.set("no_edit", "true")

        view_form = etree.tostring(tree)
        res["views"]["form"]["arch"] = view_form
        return res
