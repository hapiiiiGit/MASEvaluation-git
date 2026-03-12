# -*- coding: utf-8 -*-
from odoo import http, fields, _
from odoo.http import request
from odoo.exceptions import AccessError, UserError

class PortalController(http.Controller):
    @http.route(['/my/portal'], type='http', auth='user', website=True)
    def show_portal(self, **kwargs):
        user = request.env.user
        consent = request.env['customer.consent'].search(
            [('user_id', '=', user.id)], order='consent_date desc', limit=1
        )
        values = {
            'user': user,
            'consent': consent,
        }
        return request.render('odoo_online_customer_portal.portal_dashboard', values)

    @http.route(['/my/submit_consent'], type='json', auth='user', methods=['POST'])
    def submit_consent(self, consent_given, terms_version, jurisdiction, **kwargs):
        user = request.env.user
        if not user:
            raise AccessError(_("You must be logged in to submit consent."))
        consent = request.env['customer.consent'].create({
            'user_id': user.id,
            'consent_given': consent_given,
            'terms_version': terms_version,
            'jurisdiction': jurisdiction,
        })
        return {
            'success': True,
            'consent_id': consent.id,
            'message': _("Consent submitted successfully.")
        }

    @http.route(['/my/consent_status'], type='json', auth='user', methods=['GET'])
    def get_consent_status(self, **kwargs):
        user = request.env.user
        consent = request.env['customer.consent'].search(
            [('user_id', '=', user.id)], order='consent_date desc', limit=1
        )
        if not consent:
            return {'consent_given': False, 'terms_version': '', 'jurisdiction': '', 'consent_date': ''}
        return {
            'consent_given': consent.consent_given,
            'terms_version': consent.terms_version,
            'jurisdiction': consent.jurisdiction,
            'consent_date': fields.Datetime.to_string(consent.consent_date),
        }

class AdminConsentController(http.Controller):
    @http.route(['/admin/consents'], type='http', auth='user', website=True)
    def list_consents(self, **kwargs):
        if not request.env.user.has_group('base.group_system'):
            raise AccessError(_("You do not have permission to view consents."))
        consents = request.env['customer.consent'].search([], order='consent_date desc')
        values = {
            'consents': consents,
        }
        return request.render('odoo_online_customer_portal.admin_consent_list', values)

    @http.route(['/admin/consent/<int:consent_id>'], type='http', auth='user', website=True)
    def view_consent(self, consent_id, **kwargs):
        if not request.env.user.has_group('base.group_system'):
            raise AccessError(_("You do not have permission to view consent details."))
        consent = request.env['customer.consent'].browse(consent_id)
        if not consent.exists():
            raise UserError(_("Consent record not found."))
        audit_logs = request.env['consent.audit'].search([('consent_id', '=', consent_id)], order='timestamp desc')
        values = {
            'consent': consent,
            'audit_logs': audit_logs,
        }
        return request.render('odoo_online_customer_portal.admin_consent_detail', values)

    @http.route(['/admin/update_consent'], type='json', auth='user', methods=['POST'])
    def update_consent(self, consent_id, consent_given, **kwargs):
        if not request.env.user.has_group('base.group_system'):
            raise AccessError(_("You do not have permission to update consents."))
        consent = request.env['customer.consent'].browse(consent_id)
        if not consent.exists():
            raise UserError(_("Consent record not found."))
        consent.write({'consent_given': consent_given})
        return {
            'success': True,
            'message': _("Consent updated successfully.")
        }

    @http.route(['/admin/consent_audit/<int:consent_id>'], type='json', auth='user', methods=['GET'])
    def get_audit_trail(self, consent_id, **kwargs):
        if not request.env.user.has_group('base.group_system'):
            raise AccessError(_("You do not have permission to view audit trails."))
        audit_logs = request.env['consent.audit'].search([('consent_id', '=', consent_id)], order='timestamp desc')
        logs = [{
            'action': log.action,
            'timestamp': fields.Datetime.to_string(log.timestamp),
            'performed_by': log.performed_by.name if log.performed_by else '',
        } for log in audit_logs]
        return {'audit_logs': logs}