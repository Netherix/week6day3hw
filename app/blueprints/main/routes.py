from flask import request, flash, jsonify, render_template, redirect, url_for
import requests
from app import db
from app.blueprints.main.forms import PokemonForm, CapturePokemon
from app.models import Poke, User
from flask_login import login_required, current_user
from . import main


@main.route("/")
@main.route('/home')
def home():
    return render_template('home.html')

@main.route('/pokemon_search', methods=['GET', 'POST'])
@login_required
def pokemon_search():
    form = PokemonForm()
    if request.method == 'POST':
        pokemon = request.form.get('pokemon')

        def getPokemonInfo():
            base_url = 'https://pokeapi.co/'
            url = f'{base_url}api/v2/pokemon/{pokemon}'
            response = requests.get(url)

            if response.ok:
                data = response.json()
                front_shiny = data['sprites']['front_shiny']
                ability = data['abilities'][0]['ability']['name']
                hp_stat = data['stats'][0]['base_stat']
                attack_stat = data['stats'][1]['base_stat']
                defense_stat = data['stats'][2]['base_stat']

                return {
                    'name': pokemon,
                    'front_shiny': front_shiny,
                    'ability': ability,
                    'hp_stat': hp_stat,
                    'attack_stat': attack_stat,
                    'defense_stat': defense_stat
                }

        pokemon_info = getPokemonInfo()

        # Populate the hidden fields in the form
        form.poke_name.data = pokemon_info['name']
        form.img_url.data = pokemon_info['front_shiny']
        form.ability.data = pokemon_info['ability']
        form.hp.data = pokemon_info['hp_stat']
        form.attack.data = pokemon_info['attack_stat']
        form.defense.data = pokemon_info['defense_stat']
        
        

        return render_template('pokemon_search.html', form=form, pokemon_info=pokemon_info)

    return render_template('pokemon_search.html', form=form)


@main.route('/add_pokemon', methods=['POST'])
@login_required
def add_pokemon():
    print("add_pokemon function is being called")
    form = CapturePokemon(request.form)
    if request.method == 'POST' and form.validate_on_submit():

        existing_pokemon_count = Poke.query.filter_by(user_id=current_user.id).count()
        if existing_pokemon_count >= 5:
            flash('You have reached the maximum limit of stored Pokémon. Click here to edit your team', 'danger')
            return redirect(url_for('main.pokemon_search'))
        
        print(form.data)

        pokemon_data = {
            'poke_name': form.poke_name.data,
            'img_url': form.img_url.data,
            'ability': form.ability.data,
            'hp': form.hp.data,
            'attack': form.attack.data,
            'defense': form.defense.data,
            'user_id': current_user.id
        }

        new_pokemon = Poke()

        new_pokemon.from_dict(pokemon_data)

        db.session.add(new_pokemon)
        db.session.commit()

        flash('Pokemon added successfully!', 'success')
    else:
        flash('Invalid form data', 'danger')
        print('Error Here:')
        print(form.errors)
        print(f"Current User ID: {current_user.id}")
          # Print form validation errors

    # Redirect to the 'pokemon_search' endpoint
    return redirect(url_for('main.pokemon_search'))

@main.route('/pokemon_team')
@login_required
def pokemon_team():
    user = User.query.get(current_user.id)
    team = user.poke  # Assuming the user's Pokémon team is stored in a field called 'pokemon_team'
    return render_template('pokemon_team.html', team=team)

@main.route('/pokemon_team/delete/<poke_name>', methods=['POST', 'DELETE'])
@login_required
def delete_pokemon(poke_name):
    pokemon = Poke.query.filter_by(poke_name=poke_name, user_id=current_user.id).first()
    if pokemon:
        db.session.delete(pokemon)
        db.session.commit()
        flash('Pokemon deleted successfully!', 'success')
    else:
        flash('Pokemon not found or you do not have permission to delete it.', 'danger')

    return redirect(url_for('main.pokemon_team'))
