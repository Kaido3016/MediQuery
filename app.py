"""MediQuery's intentionally small Streamlit client for the authenticated report workflow."""

import os
from typing import Any

import requests
import streamlit as st


API_URL = os.getenv("MEDIQUERY_API_URL", "http://localhost:8000").rstrip("/")
HTTP_TIMEOUT_SECONDS = 30

st.set_page_config(page_title="MediQuery", page_icon="🩺", layout="wide")
st.markdown(
    """<style>
    .block-container {max-width: 1120px; padding-top: 3rem;}
    .mq-card {padding: 1.2rem; border: 1px solid #d9e3ea; border-radius: .75rem; background: #fff;}
    </style>""",
    unsafe_allow_html=True,
)


def _http_session() -> requests.Session:
    """Reuse one HTTP connection pool for the current Streamlit session."""
    session = st.session_state.get("http_session")
    if not isinstance(session, requests.Session):
        session = requests.Session()
        st.session_state.http_session = session
    return session


def api(method: str, path: str, **kwargs: Any) -> requests.Response:
    """Call the API with the current session's bearer token and bounded timeout."""
    headers = dict(kwargs.pop("headers", {}))
    token = st.session_state.get("access_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    normalized_path = f"/{path.lstrip('/')}"
    return _http_session().request(
        method,
        f"{API_URL}{normalized_path}",
        headers=headers,
        timeout=HTTP_TIMEOUT_SECONDS,
        **kwargs,
    )


def request_auth(mode: str, email: str, password: str, acknowledged: bool, totp_code: str = "") -> None:
    try:
        response = api(
            "POST",
            f"/api/auth/{mode}",
            json={
                "email": email,
                "password": password,
                "acknowledge_medical_limitations": acknowledged,
                **({"totp_code": totp_code} if totp_code else {}),
            },
        )
        if response.ok:
            result = response.json()
            token = result.get("access_token")
            if token:
                st.session_state.access_token = token
                st.rerun()
            if result.get("verification_required"):
                st.success("Account created. Check your email to verify the address before signing in.")
                return
        st.error(response.json().get("detail", "We could not complete that request."))
    except (requests.RequestException, ValueError):
        st.error("MediQuery is unavailable. Please try again shortly.")


def signed_out_view() -> None:
    query_params = st.experimental_get_query_params()
    verify_token = (query_params.get("verify_email_token") or [None])[0]
    reset_token = (query_params.get("password_reset_token") or [None])[0]
    if verify_token:
        st.info("Confirm your email address to finish account setup.")
        if st.button("Verify email address", type="primary"):
            try:
                response = api("POST", "/api/auth/verify-email", json={"token": verify_token})
                if response.ok:
                    st.success("Email verified. You can now log in.")
                    st.experimental_set_query_params()
                else:
                    st.error(response.json().get("detail", "Verification link is invalid or expired."))
            except requests.RequestException:
                st.error("MediQuery is unavailable. Please try again shortly.")
    if reset_token:
        with st.form("password_reset_form"):
            new_password = st.text_input("New password", type="password", help="Use at least 12 characters.")
            confirm_password = st.text_input("Confirm new password", type="password")
            submitted = st.form_submit_button("Reset password")
        if submitted:
            if new_password != confirm_password:
                st.error("The passwords do not match.")
            else:
                try:
                    response = api("POST", "/api/auth/password-reset/confirm", json={"token": reset_token, "new_password": new_password})
                    if response.ok:
                        st.success("Password changed. Log in with your new password.")
                        st.experimental_set_query_params()
                    else:
                        st.error(response.json().get("detail", "Reset link is invalid or expired."))
                except requests.RequestException:
                    st.error("MediQuery is unavailable. Please try again shortly.")
    st.title("Understand the facts in your lab report")
    st.subheader(
        "A private, evidence-first way to organize extracted report values before "
        "discussing them with a qualified clinician."
    )
    left, right = st.columns([3, 2], gap="large")
    with left:
        st.markdown(
            """### How it works
        1. Upload a text-based PDF report.
        2. MediQuery preserves detectable values, units, ranges, and source page
           evidence.
        3. Review the original report and speak with a qualified health professional for medical advice.

        MediQuery is not a diagnostic service and does not replace professional medical
        advice, diagnosis, or treatment."""
        )
    with right:
        st.markdown('<div class="mq-card">', unsafe_allow_html=True)
        mode = st.radio("Account", ["Log in", "Create account"], horizontal=True)
        email = st.text_input("Email", autocomplete="email")
        password = st.text_input(
            "Password", type="password", help="Use at least 12 characters."
        )
        totp_code = st.text_input("Authenticator code (if MFA is enabled)", max_chars=8)
        acknowledged = st.checkbox(
            "I understand MediQuery is not medical advice or a diagnostic service.",
            disabled=mode == "Log in",
        )
        if st.button(mode, type="primary", use_container_width=True):
            request_auth(
                "login" if mode == "Log in" else "signup",
                email,
                password,
                acknowledged or mode == "Log in",
                totp_code,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    with st.expander("Forgot your password or need another verification email?"):
        recovery_email = st.text_input("Account email", key="recovery_email")
        recovery_left, recovery_right = st.columns(2)
        with recovery_left:
            if st.button("Send password-reset email"):
                try:
                    response = api("POST", "/api/auth/password-reset/request", json={"email": recovery_email})
                    if response.ok:
                        st.success(response.json().get("message", "If the account exists, an email will be sent."))
                    else:
                        st.error("Could not request a password reset.")
                except requests.RequestException:
                    st.error("MediQuery is unavailable. Please try again shortly.")
        with recovery_right:
            if st.button("Resend verification email"):
                try:
                    response = api("POST", "/api/auth/verification/resend", json={"email": recovery_email})
                    if response.ok:
                        st.success(response.json().get("message", "If verification is needed, an email will be sent."))
                    else:
                        st.error("Could not request verification.")
                except requests.RequestException:
                    st.error("MediQuery is unavailable. Please try again shortly.")
    st.divider()
    first, second, third = st.columns(3)
    with first:
        st.markdown("### Evidence first")
        st.write(
            "Review each detected candidate beside its original report evidence and page."
        )
    with second:
        st.markdown("### Private by design")
        st.write(
            "Reports are owner-scoped and are not published through a public upload URL."
        )
    with third:
        st.markdown("### Simple plans")
        st.write(
            "The Free plan has a configurable report allowance. Pro billing is planned, not active."
        )
    st.markdown("### Frequently asked questions")
    with st.expander("Can MediQuery diagnose me?"):
        st.write(
            "No. It is an educational report-organizing tool. Consult a qualified "
            "health professional for medical decisions."
        )
    with st.expander("What reports can I upload?"):
        st.write(
            "Text-based PDF reports up to the configured limit. Scanned PDFs may not "
            "contain selectable text and OCR is not enabled yet."
        )
    with st.expander("How do I delete my information?"):
        st.write(
            "You can delete each report in the dashboard. Account deletion is "
            "available through the authenticated API; a self-service UI control is planned."
        )
    st.caption(
        "Privacy note: Reports are sensitive. Do not upload a report unless you are "
        "authorized to do so. Production deployment requires approved private storage "
        "and legal/privacy review."
    )


def dashboard() -> None:
    st.sidebar.title("MediQuery")
    if st.sidebar.button("Log out"):
        st.session_state.clear()
        st.rerun()
    st.sidebar.caption("Educational report organization—not diagnosis.")
    with st.sidebar.expander("Account settings"):
        st.caption(
            "Deleting your account permanently removes the reports stored by this local deployment."
        )
        confirm_delete = st.checkbox(
            "I understand this cannot be undone", key="confirm-account-delete"
        )
        if st.button(
            "Delete account", disabled=not confirm_delete, key="delete-account"
        ):
            response = api("DELETE", "/api/auth/account")
            if response.status_code == 204:
                st.session_state.clear()
                st.rerun()
            st.error("We could not delete the account. Please try again.")
    st.title("Your reports")
    try:
        plan_response = api("GET", "/api/reports/plan")
        if plan_response.status_code == 401:
            st.session_state.clear()
            st.rerun()
        plan = plan_response.json()
        if plan["reports_limit"] is None:
            st.caption(f"{plan['plan'].title()} plan")
        else:
            st.caption(
                f"{plan['reports_used']} of {plan['reports_limit']} reports used on the Free plan"
            )
    except (requests.RequestException, ValueError):
        st.error("We could not load your account. Please try again shortly.")
        return

    upload = st.file_uploader(
        "Upload a text-based PDF report",
        type=["pdf"],
        help="Maximum 10 MB. Scanned PDFs may require OCR, which is not yet available.",
    )
    if upload and st.button("Process report", type="primary"):
        with st.spinner("Validating and extracting report facts…"):
            upload_bytes = upload.getvalue()
            response = api(
                "POST",
                "/api/reports",
                files={"file": (upload.name, upload_bytes, "application/pdf")},
            )
        if response.ok:
            st.success(
                "Report processed. Review detected candidates against the original PDF."
            )
            st.rerun()
        else:
            try:
                detail = response.json().get(
                    "detail", "The report could not be processed."
                )
            except ValueError:
                detail = "The report could not be processed."
            st.error(detail)

    response = api("GET", "/api/reports")
    if not response.ok:
        st.error("We could not load your reports.")
        return
    try:
        reports = response.json()
    except ValueError:
        st.error("The report service returned an invalid response.")
        return
    if not reports:
        st.info(
            "Upload your first report to see extracted values and page-level evidence here."
        )
        return
    for report in reports:
        with st.expander(
            f"{report['original_filename']} · {report['page_count']} pages",
            expanded=False,
        ):
            if report.get("extraction_note"):
                st.warning(report["extraction_note"])
            findings = report["findings"]
            if findings:
                st.caption(
                    "Extracted candidates — verify every item against the original report."
                )
                st.dataframe(
                    [
                        {
                            "Name": x["name"],
                            "Value": x["value"],
                            "Unit": x["unit"],
                            "Reference range": x["reference_range"],
                            "Flag": x["flag"],
                            "Page": x["page"],
                        }
                        for x in findings
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
                with st.popover("Show source evidence"):
                    for finding in findings:
                        st.write(
                            f"Page {finding['page']} · {finding['name']}: {finding['evidence']}"
                        )
            else:
                st.info(
                    "No structured values were identified. Review the original report."
                )
            if st.button("Delete report", key=f"delete-{report['id']}"):
                deleted = api("DELETE", f"/api/reports/{report['id']}")
                if deleted.status_code == 204:
                    st.success("Report deleted.")
                    st.rerun()
                st.error("The report could not be deleted.")


if st.session_state.get("access_token"):
    dashboard()
else:
    signed_out_view()
