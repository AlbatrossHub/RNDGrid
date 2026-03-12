from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    terms_template_id = fields.Many2one(
        "sale.terms_template",
        string="Terms and conditions template",
    )
    want_note = fields.Boolean("Add terms in PDF?", default=True)
    # note = fields.Html(readonly=True, states={"draft": [("readonly", False)]})

    @api.onchange("terms_template_id")
    def _onchange_terms_template_id(self):
        if self.terms_template_id:
            self.note = self.terms_template_id.get_value(self)
