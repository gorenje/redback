from flask import Blueprint, render_template, abort, jsonify
from flask import Flask, session, request, url_for, redirect

favicon_bp = Blueprint('favicon', __name__,
                    template_folder='templates',
                    url_prefix='/')
__all__ = [
    "favicon_bp"
]

##
## Favicon
##
@favicon_bp.route('/favicon.ico', methods=['GET'])
def favicon():
    return redirect("/static/favicon/favicon.ico")
