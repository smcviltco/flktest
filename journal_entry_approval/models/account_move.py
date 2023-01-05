# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('to_review', 'Waiting For Review'),
        ('approve', 'Waiting For Approval'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
        ('rejected', 'Rejected'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')

    def action_post(self):
        if self.move_type == 'entry':
            self.write({
                'state': 'to_review'
            })
        else:
            rec = super(AccountMoveInh, self).action_post()
            return rec

    def button_review(self):
        self.write({
            'state': 'approve'
        })

    def action_reset(self):
        self.write({
            'state': 'draft'
        })

    def button_approved(self):
        rec = super(AccountMoveInh, self).action_post()
        return rec

    def button_review_reject(self):
        self.write({
            'state': 'rejected'
        })

    def button_approve_reject(self):
        self.write({
            'state': 'rejected'
        })
