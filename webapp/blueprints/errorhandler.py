from flask import Blueprint, render_template, abort, jsonify
from flask import Flask, session, request, url_for, redirect

import traceback, sys

error_bp = Blueprint('errorhandler', __name__,
                    template_folder='templates')
__all__ = [
    "error_bp"
]

##
## Error handlers
##
@error_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@error_bp.app_errorhandler(405)
def not_allowed(e):
    return render_template('405.html'), 405

@error_bp.app_errorhandler(Exception)
@error_bp.app_errorhandler(500)
def server_error(error):
    repr_error = repr(error)
    exc_type, exc_value, exc_tb = sys.exc_info()
    trcbck = "\n".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    return render_template('500.html', error=error, trcbck=trcbck), 500
