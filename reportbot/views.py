from typing import Dict, Any, Optional

# return slack modal view for duty report
# currently used by both /report command and reminder button action
def build_report_modal_view(private_metadata: Optional[str] = None) -> Dict[str, Any]:
    view: Dict[str, Any] = {
        "type": "modal",
        "callback_id": "report_modal",
        "title": {"type": "plain_text", "text": "Duty Report"},
        "submit": {"type": "plain_text", "text": "Submit"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "input",
                "block_id": "summary_block",
                "label": {"type": "plain_text", "text": "Summary (free text)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "summary_input",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Night summary, incidents, flow, etc.",
                    },
                },
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": "*KYC — General*"}},
            {
                "type": "input",
                "block_id": "kyc_general_queue_block",
                "label": {"type": "plain_text", "text": "General Queue (number)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "kyc_general_queue_input",
                },
            },
            {
                "type": "input",
                "block_id": "kyc_security_block",
                "label": {"type": "plain_text", "text": "Security (number)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "kyc_security_input",
                },
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": "*KYC — Peru*"}},
            {
                "type": "input",
                "block_id": "kyc_peru_queue_block",
                "label": {"type": "plain_text", "text": "Peru Queue (number)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "kyc_peru_queue_input",
                },
            },
            {
                "type": "input",
                "block_id": "kyc_peru_security_block",
                "label": {"type": "plain_text", "text": "Peru Security (number)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "kyc_peru_security_input",
                },
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": "*Payouts*"}},
            {
                "type": "input",
                "block_id": "payouts_row_block",
                "label": {
                    "type": "plain_text",
                    "text": "ROW (short text, e.g. 'up to date', '1 page')",
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "payouts_row_input",
                },
            },
            {
                "type": "input",
                "block_id": "payouts_peru_block",
                "label": {"type": "plain_text", "text": "Peru (short text)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "payouts_peru_input",
                },
            },
            {
                "type": "input",
                "block_id": "highlights_block",
                "label": {"type": "plain_text", "text": "Highlights (free text)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "highlights_input",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Critical updates/issues",
                    },
                },
            },
            {
                "type": "input",
                "block_id": "routines_block",
                "optional": True,
                "label": {"type": "plain_text", "text": "Routines"},
                "element": {
                    "type": "multi_static_select",
                    "action_id": "routines_input",
                    "placeholder": {"type": "plain_text", "text": "Select completed routines..."},
                    "options": [
                        {"text": {"type": "plain_text", "text": "Accounts with Negative Balance"}, "value": "accounts_negative_balance"},
                        {"text": {"type": "plain_text", "text": "Customers in KYC Status 'Security'"}, "value": "kyc_security_status"},
                        {"text": {"type": "plain_text", "text": "Iceland Security Trigger Report"}, "value": "iceland_security_trigger"},
                        {"text": {"type": "plain_text", "text": "Lost 5000 or More"}, "value": "lost_5000_or_more"},
                        {"text": {"type": "plain_text", "text": "Occasional Transaction Report"}, "value": "occasional_transaction"},
                        {"text": {"type": "plain_text", "text": "Unverified Accounts to be Reminded"}, "value": "unverified_accounts"},
                        {"text": {"type": "plain_text", "text": "Weekly 2k Deposits Reports"}, "value": "weekly_2k_deposits"},
                        {"text": {"type": "plain_text", "text": "IDscan KYC waiting or Security Daily"}, "value": "idscan_kyc_daily"},
                    ],
                },
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": "*Edgetier*"}},
            {
                "type": "input",
                "block_id": "edgetier_reports_block",
                "label": {"type": "plain_text", "text": "Reports (number)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "edgetier_reports_input",
                },
            },
            {
                "type": "input",
                "block_id": "edgetier_general_block",
                "label": {"type": "plain_text", "text": "General (number)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "edgetier_general_input",
                },
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": "*PSP inbox*"}},
            {
                "type": "input",
                "block_id": "psp_inbox_block",
                "label": {"type": "plain_text", "text": "Pending cases (number)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "psp_inbox_input",
                },
            },
        ],
    }
    if private_metadata:
        view["private_metadata"] = private_metadata
    return view
