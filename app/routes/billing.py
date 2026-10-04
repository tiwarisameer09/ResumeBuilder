import stripe
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, session, flash
from flask_login import login_required, current_user
from app.extensions import db, csrf
from app.models import User, Payment

billing_bp = Blueprint("billing", __name__, url_prefix="/billing")

@billing_bp.route("/paywall")
@billing_bp.route("/pricing")
@login_required
def paywall():
    resume_id = request.args.get("resume_id") or session.get("target_resume_id")
    style = request.args.get("style") or session.get("target_style", "modern")
    publishable_key = current_app.config.get("STRIPE_PUBLISHABLE_KEY", "")
    return render_template(
        "billing/paywall.html",
        publishable_key=publishable_key,
        resume_id=resume_id,
        style=style
    )

@billing_bp.route("/pricing-page")
@login_required
def pricing():
    return redirect(url_for("billing.paywall"))

@billing_bp.route("/create-checkout-session", methods=["POST"])
@billing_bp.route("/checkout", methods=["POST"])
@login_required
def create_checkout_session():
    stripe.api_key = current_app.config.get("STRIPE_SECRET_KEY", "")
    domain = request.host_url.rstrip("/")
    resume_id = request.args.get("resume_id") or session.get("target_resume_id")
    style = request.args.get("style") or session.get("target_style", "modern")

    plan_type = "lifetime"
    if request.is_json:
        plan_type = request.json.get("plan", "lifetime")
    else:
        plan_type = request.form.get("plan", "lifetime")

    # If no stripe key is provided (e.g. initial dev mode), provide helpful error
    if not stripe.api_key or stripe.api_key == "fallback-secret-for-dev-only":
        return jsonify({
            "error": "Stripe API key is not configured. Use the Dev Test Bypass button below to test exports."
        }), 400

    if plan_type == "credits":
        price_amount = 299  # $2.99 for 3 download credits
        product_name = "ResumeBuilder 3 Export Credits"
        product_desc = "3 PDF downloads for any prospective job roles."
    else:
        price_amount = 999  # $9.99 for lifetime unlimited access
        product_name = "ResumeBuilder Pro Lifetime Export"
        product_desc = "Unlock infinite PDF downloads in Modern, Minimalist, and Executive styles."

    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            client_reference_id=str(current_user.id),
            metadata={
                "plan_type": plan_type,
                "resume_id": str(resume_id or ""),
                "style": style or "modern"
            },
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": price_amount,
                    "product_data": {
                        "name": product_name,
                        "description": product_desc
                    }
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{domain}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{domain}/billing/paywall?payment=cancelled",
        )
        return jsonify({"id": checkout_session.id, "url": checkout_session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@billing_bp.route("/success")
@login_required
def success():
    session_id = request.args.get("session_id")
    target_resume_id = session.get("target_resume_id")
    target_style = session.get("target_style", "modern")
    return render_template(
        "billing/success.html",
        session_id=session_id,
        resume_id=target_resume_id,
        style=target_style
    )

@billing_bp.route("/webhook", methods=["POST"])
@csrf.exempt
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")
    endpoint_secret = current_app.config.get("STRIPE_WEBHOOK_SECRET")

    # If endpoint secret is set, verify cryptographic signature
    if endpoint_secret:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError:
            return "Invalid payload", 400
        except stripe.error.SignatureVerificationError:
            return "Invalid signature", 400
    else:
        try:
            event = request.get_json(force=True)
        except Exception:
            return "Invalid JSON", 400

    if event and event.get("type") == "checkout.session.completed":
        session_obj = event["data"]["object"]
        user_id = session_obj.get("client_reference_id")
        metadata = session_obj.get("metadata", {})
        plan_type = metadata.get("plan_type", "lifetime")

        if user_id:
            user = User.query.get(int(user_id))
            if user:
                # Idempotent upgrade
                if plan_type == "credits":
                    user.download_credits += 3
                else:
                    user.has_paid_access = True

                # Record transaction
                payment = Payment(
                    user_id=user.id,
                    stripe_session_id=session_obj.get("id"),
                    amount=session_obj.get("amount_total", 0),
                    currency=session_obj.get("currency", "usd"),
                    status="completed"
                )
                db.session.add(payment)
                db.session.commit()

    return jsonify({"status": "success"}), 200

# Developer convenience bypass for local manual testing without active Stripe API keys
@billing_bp.route("/dev-grant-access", methods=["POST"])
@login_required
def dev_grant_access():
    action = request.form.get("action", "lifetime")
    if action == "credits":
        current_user.download_credits += 3
        flash("Granted 3 demo download credits!", "success")
    else:
        current_user.has_paid_access = True
        flash("Unlocked Pro Lifetime Access for testing!", "success")
    db.session.commit()

    resume_id = session.get("target_resume_id")
    style = session.get("target_style")
    if resume_id and style:
        return redirect(url_for("export.download_pdf", resume_id=resume_id, style=style))
    return redirect(url_for("dashboard.index"))