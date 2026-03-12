# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class CustomerConsent(models.Model):
    _name = 'customer.consent'
    _description = 'Customer Consent'
    _order = 'consent_date desc'

    user_id = fields.Many2one('res.users', string='User', required=True, index=True)
    consent_given = fields.Boolean(string='Consent Given', required=True, default=False)
    consent_date = fields.Datetime(string='Consent Date', required=True, default=lambda self: fields.Datetime.now())
    terms_version = fields.Char(string='Terms & Conditions Version', required=True)
    jurisdiction = fields.Char(string='Jurisdiction', required=True)
    audit_log_ids = fields.One2many('consent.audit', 'consent_id', string='Audit Log')

    @api.model
    def create(self, vals):
        record = super(CustomerConsent, self).create(vals)
        # Log audit entry for consent creation
        self.env['consent.audit'].create({
            'consent_id': record.id,
            'action': 'consent_given' if record.consent_given else 'consent_not_given',
            'timestamp': fields.Datetime.now(),
            'performed_by': record.user_id.id,
        })
        return record

    def write(self, vals):
        old_consent_given = self.consent_given
        res = super(CustomerConsent, self).write(vals)
        # Log audit entry for consent update
        if 'consent_given' in vals and vals['consent_given'] != old_consent_given:
            self.env['consent.audit'].create({
                'consent_id': self.id,
                'action': 'consent_updated',
                'timestamp': fields.Datetime.now(),
                'performed_by': self.env.uid,
            })
        return res

    def get_latest_consent(self, user_id):
        return self.search([('user_id', '=', user_id)], order='consent_date desc', limit=1)

class ConsentAudit(models.Model):
    _name = 'consent.audit'
    _description = 'Consent Audit Log'
    _order = 'timestamp desc'

    consent_id = fields.Many2one('customer.consent', string='Consent', required=True, index=True)
    action = fields.Selection([
        ('consent_given', 'Consent Given'),
        ('consent_not_given', 'Consent Not Given'),
        ('consent_updated', 'Consent Updated'),
    ], string='Action', required=True)
    timestamp = fields.Datetime(string='Timestamp', required=True, default=lambda self: fields.Datetime.now())
    performed_by = fields.Many2one('res.users', string='Performed By', required=True)

    @api.model
    def create(self, vals):
        # Ensure performed_by is set
        if not vals.get('performed_by'):
            vals['performed_by'] = self.env.uid
        return super(ConsentAudit, self).create(vals)