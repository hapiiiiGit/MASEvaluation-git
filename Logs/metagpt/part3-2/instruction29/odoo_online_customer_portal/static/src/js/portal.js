/**
 * portal.js - Interactive features for Odoo Online Customer Portal
 * Handles Terms & Conditions checkbox logic, consent form validation,
 * AJAX consent submission, and UI updates for consent status.
 */

odoo.define('odoo_online_customer_portal.portal', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    /**
     * Registration Form: Ensure T&C checkbox is checked before submission.
     */
    $(document).ready(function () {
        // Registration form validation
        var $registrationForm = $('#portal_registration_form');
        if ($registrationForm.length) {
            $registrationForm.on('submit', function (e) {
                var $termsCheckbox = $('#terms_checkbox');
                if (!$termsCheckbox.is(':checked')) {
                    e.preventDefault();
                    alert(_t("You must accept the Terms & Conditions to register."));
                    $termsCheckbox.focus();
                    return false;
                }
            });
        }

        // Consent status AJAX update (for profile/dashboard)
        var $consentStatusContainer = $('.o_portal_consent_status');
        if ($consentStatusContainer.length) {
            ajax.jsonRpc('/my/consent_status', 'call', {})
                .then(function (result) {
                    if (result) {
                        var html = '';
                        if (result.consent_given) {
                            html += '<span class="badge badge-success">' + _t('Accepted') + '</span>';
                        } else {
                            html += '<span class="badge badge-danger">' + _t('Not Accepted') + '</span>';
                        }
                        html += '<br/><strong>' + _t('Terms Version:') + '</strong> ' + result.terms_version;
                        html += '<br/><strong>' + _t('Jurisdiction:') + '</strong> ' + result.jurisdiction;
                        html += '<br/><strong>' + _t('Date:') + '</strong> ' + result.consent_date;
                        $consentStatusContainer.html(html);
                    }
                });
        }

        // Consent submission (if a separate consent form is present)
        var $consentForm = $('#portal_consent_form');
        if ($consentForm.length) {
            $consentForm.on('submit', function (e) {
                e.preventDefault();
                var consentGiven = $('#consent_checkbox').is(':checked');
                var termsVersion = $('#consent_terms_version').val();
                var jurisdiction = $('#consent_jurisdiction').val();

                if (!consentGiven) {
                    alert(_t("You must accept the Terms & Conditions to proceed."));
                    return false;
                }

                ajax.jsonRpc('/my/submit_consent', 'call', {
                    consent_given: consentGiven,
                    terms_version: termsVersion,
                    jurisdiction: jurisdiction
                }).then(function (result) {
                    if (result && result.success) {
                        alert(_t("Consent submitted successfully."));
                        window.location.reload();
                    } else {
                        alert(_t("Failed to submit consent. Please try again."));
                    }
                });
            });
        }

        // Admin: Update consent status via AJAX (handled in QWeb template, but fallback here)
        window.updateConsentStatus = function (btn) {
            var consentId = btn.getAttribute('data-consent_id');
            var consentGiven = document.getElementById('update_consent_checkbox').checked;
            var messageSpan = document.getElementById('update_consent_message');
            messageSpan.innerText = '';
            ajax.jsonRpc('/admin/update_consent', 'call', {
                consent_id: parseInt(consentId),
                consent_given: consentGiven
            }).then(function (response) {
                if (response && response.success) {
                    messageSpan.innerText = response.message;
                    messageSpan.className = 'text-success ml-2';
                    setTimeout(function () { location.reload(); }, 1000);
                } else {
                    messageSpan.innerText = _t('Update failed.');
                    messageSpan.className = 'text-danger ml-2';
                }
            }).catch(function () {
                messageSpan.innerText = _t('Error updating consent.');
                messageSpan.className = 'text-danger ml-2';
            });
        };
    });
});