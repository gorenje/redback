import json
import os
import requests
import logging
import math

class BackendAPI:
    def __init__(self, cfg):
        self.token = cfg["API_TOKEN"]

        prot = "https://" if int(cfg["API_SERVER_PORT"]) == 443 else "http://"

        self.endpt_url = "{}{}:{}".format(
            prot, cfg["API_SERVER_HOST"], cfg["API_SERVER_PORT"] )

    def url_for(self,path):
        return self.endpt_url + "/api/" + path

    def postit(self, path, data ):
        return requests.post(
            self.url_for(path),
            data = json.dumps(data),
            headers = {
                "Content-Type": "application/json",
                "X-Auth": self.token
            }
        ).json()

    def getit(self, path, data = {} ):
        return requests.get(
            self.url_for(path),
            data,
            headers = {
                "Content-Type": "application/json",
                "X-Auth": self.token
            }
        ).json()

    ##
    ## External Calls
    ##

    ##
    ## Auctions
    ##
    def make_bid_decision(self, user_uuid, proposal_uuid, amount, decision):
        return self.postit("proposal/make_decision", {
            "user_uuid":     user_uuid,
            "proposal_uuid": proposal_uuid,
            "amount":        amount,
            "decision":      decision
        })

    def all_proposals(self, not_accepted = True):
        params = {}
        if not_accepted: params = { "not_accepted": True }

        return self.getit( "proposals/all", params)

    def proposal_details(self, proposal_uuid):
        return self.getit( "proposal/" + proposal_uuid)

    def new_proposal(self, buyer_uuid, f,s, iamseller,
                   description, seller_email, amount):
        return self.postit("proposal/new", {
            "buyer_uuid":      buyer_uuid,
            "buyer_firstname": f,
            "buyer_surname":   s,
            "buyer_iamseller": iamseller,
            "description":     description,
            "seller_email":    seller_email,
            "amount":          math.ceil(amount)
        })

    ##
    ## Bid
    ##
    def make_bid(self, user_uuid, proposal_uuid, amount):
        return self.postit("bid/new", {
            "user_uuid":     user_uuid,
            "proposal_uuid": proposal_uuid,
            "amount":        amount
        })

    def bid_details(self, bid_uuid):
        return self.getit( "bid/" + bid_uuid)

    ##
    ## Users
    ##
    def verify_with_email(self,email,verification_code):
        return self.postit("user/verify", {
            "email":             email,
            "verification_code": verification_code,
        })

    def send_email_with_verification(self,user_uuid,ver_code):
        return self.postit("user/send/verify/email", {
            "user_uuid":         user_uuid,
            "verification_code": ver_code
        })

    def user_register(self,firstname,surname,email):
        return self.postit("user/register", {
            "email":     email,
            "firstname": firstname,
            "surname":   surname,
        })

    def user_resend_verify_code(self,email):
        return self.postit("user/verify/resend", {
            "email":     email
        })

    def user_login_with_email(self,email):
        return self.postit("user/login/email", {
            "email": email,
        })

    def user_login_with_loginlink(self,data):
        return self.postit("user/login/loginlink", {
            "data": data,
        })

    def user_verify_with_verifylink(self,data):
        return self.postit("user/verify/linkdata", {
            "data": data,
        })

    def user_login_with_email_send_login_code(self, user_uuid, ver_code):
        return self.postit("user/login/email/send", {
            "user_uuid":         user_uuid,
            "verification_code": ver_code,
        })

    def user_login_with_email_verify_code(self, email, ver_code):
        return self.postit("user/login/email/verify", {
            "email":             email,
            "verification_code": ver_code,
        })

    def user_dont_spam_me(self, data, confirm_email):
        return self.postit("user/dontspamme", {
            "data":          data,
            "confirm_email": confirm_email,
        })

    def user_proposals(self, user_uuid, which_kind = None):
        return self.getit( "users/" + user_uuid + "/proposals", {
            "kind": which_kind
        })

    def user_email(self, user_uuid ):
        return self.getit( "users/" + user_uuid )
