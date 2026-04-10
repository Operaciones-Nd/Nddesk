from flask import Blueprint, render_template, session
from utils.decorators import login_required, role_required

workflow_bp = Blueprint('workflow', __name__)

@workflow_bp.route('/workflow')
@login_required
def index():
    return render_template('workflow/index.html')