import math

from flask import Blueprint, abort, jsonify
from flask import Flask, session, request, url_for, redirect

api_bp = Blueprint('api', __name__,
                    template_folder='templates',
                    url_prefix='/api')
__all__ = [
    "api_bp"
]

from models  import config
from backend import BackendAPI

backendapi = BackendAPI(config)

##
## User endpoints
##
@api_bp.route('/user/register', methods=['POST'])
def user_register():
    reqdata = request.get_json()

    resp = backendapi.user_register(
        reqdata["firstname"],
        reqdata["surname"],
        reqdata["email"]
    )

    if ( resp.get("verification_code", False) ):
        session["ver_code"]       = resp["verification_code"]
        session["email"]          = reqdata["email"]
        resp["verification_code"] = "this is obviously wrong"
        return jsonify({
            "status": "ok",
            "user_uuid": resp["user_uuid"]
        })
    else:
        return jsonify({
            "status": resp["status"],
            "msg": resp.get("msg")
        })

@api_bp.route('/user/verify/email', methods=['POST'])
def user_login_by_verifying_email():
    dt = request.get_json()

    resp = backendapi.verify_with_email(dt["email"], dt["ver_code"])

    if ( resp["status"] == "ok" ):
        session["user_id"]        = resp["user"]["uuid"]
        session["user_firstname"] = resp["user"]["firstname"]
        session["user_surname"]   = resp["user"]["surname"]
        session.pop("email")
        del resp["user"]

    return jsonify({
        "status": "ok",
        **resp
    })

@api_bp.route('/user/verify/login/code', methods=['POST'])
def user_login_verify_login_code():
    dt = request.get_json()

    ver_code = dt["ver_code"]
    email = session["email"]

    resp = backendapi.user_login_with_email_verify_code(email,ver_code)

    if ( resp["status"] == "ok" ):
        session["user_id"]        = resp["user"]["uuid"]
        session["user_firstname"] = resp["user"]["firstname"]
        session["user_surname"]   = resp["user"]["surname"]
        session.pop("email")
        del resp["user"]

    return jsonify({
        "status": "ok",
        **resp
    })

@api_bp.route('/user/login/with/email', methods=['POST'])
def user_login_with_email():
    if session.get("user_id") != None: return redirect(url_for('proposals'))

    dt = request.get_json()

    resp = backendapi.user_login_with_email(dt["email"])

    if resp["status"] == "ok":
        session["email"] = resp["email"]
        session["uuid"]  = resp["user_uuid"]
        ver_code         = resp["verification_code"]

        resp = backendapi.user_login_with_email_send_login_code(
            resp["user_uuid"],
            ver_code,
        )

        return jsonify({ "status": "ok", **resp })

    elif resp["status"] == "email_not_verified":
        session["email"] = resp["email"]

    return jsonify(resp)

@api_bp.route('/user/resend/verify/email', methods=['POST'])
def user_resend_verify_code():
    return jsonify(backendapi.user_resend_verify_code(
        request.get_json()["email"]
    ))

@api_bp.route('/user/send/verify/email', methods=['POST'])
def send_verify_email():
    if session.get("ver_code") == None: return redirect(url_for('index'))

    resp = backendapi.send_email_with_verification(
        request.get_json()["user_uuid"],
        session.pop("ver_code")
    )

    return jsonify({
        "status": "ok",
        **resp
    })

@api_bp.route('/users/proposals', methods=['GET'])
def user_proposals():
    if session.get("user_id") == None: return redirect(url_for('index'))

    return jsonify(backendapi.user_proposals(
        session.get("user_id"),
        request.args.get("kind", None)
    ))

@api_bp.route('/users/getemail', methods=['GET'])
def user_getemail():
    if session.get("user_id") == None: return redirect(url_for('index'))

    return jsonify(backendapi.user_email(session.get("user_id")))


##
## Auction endpoints
##
@api_bp.route('/proposals/bid', methods=['POST'])
def proposals_bid():
    if session.get("user_id") == None: return redirect(url_for('index'))

    dt = request.get_json()

    r = backendapi.make_bid(session.get("user_id"),
                            dt["proposal_uuid"],
                            math.ceil( int(dt["amount"]) *
                                       (1 + int(dt["percent"])/100.0)))
    return jsonify({
        "status": "ok",
        **r
    })

@api_bp.route('/proposals/decline', methods=['POST'])
def proposals_decline():
    if session.get("user_id") == None: return redirect(url_for('index'))

    dt = request.get_json()

    r = backendapi.make_bid_decision(session.get("user_id"),
                                     dt["proposal_uuid"],
                                     dt["amount"],
                                     "decline")
    return jsonify({
        "status": "ok",
        **r
    })

@api_bp.route('/proposals/accept', methods=['POST'])
def proposals_accept():
    if session.get("user_id") == None: return redirect(url_for('index'))

    dt = request.get_json()

    r = backendapi.make_bid_decision(session.get("user_id"),
                                     dt["proposal_uuid"],
                                     dt["amount"],
                                     "accept")
    return jsonify({
        "status": "ok",
        **r
    })

@api_bp.route('/proposals/all', methods=['GET'])
def proposals_all():
    if session.get("user_id") == None: return redirect(url_for('index'))

    return jsonify({
        "status": "ok",
        "data": backendapi.all_proposals(False)
    })

@api_bp.route('/proposal/new', methods=["POST"])
def submit_new_proposal():
    if session.get("user_id") == None: return redirect(url_for('index'))

    dt = request.get_json()

    if not dt["amount"] or dt["amount"] == "" or int(dt["amount"]) <= 0:
        return jsonify({
            "status": "error",
            "msg": "amount NaN"
        })
    else:
        return jsonify({
            "status": "ok",
            **backendapi.new_proposal(session.get("user_id"),
                                      session.get("user_firstname"),
                                      session.get("user_surname"),
                                      dt["iamseller"],
                                      dt["description"],
                                      dt["seller_email"],
                                      int(dt["amount"]))
        })

##
## Bid endpoints
##
@api_bp.route('/bids/<bid_uuid>', methods=['GET'])
def previous_bids_for_bid(bid_uuid):
    return jsonify(backendapi.bid_details(bid_uuid))


##
## Don't spam me endpoint
##
@api_bp.route('/dont-spam-me', methods=['POST'])
def user_dont_spam_me():
    dt = request.get_json()

    return jsonify(backendapi.user_dont_spam_me(dt["data"],dt["email"]))
