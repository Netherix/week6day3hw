from flask import Blueprint

poke = Blueprint('poke', __name__, template_folder='poke_templates', url_prefix='/poke')

from . import routes