from django.test import TestCase
import os
import requests_mock
from brewkeeper import Recipe


# Create your tests here.


@requests_mock.Mocker()
def test_get_recipe_details(m):
    recipeurl = 'https://brew-keeper-api.herokuapp.com/api/user/don.pablo/'
    with open('fixtures/examples.json') as data:
        m.get(recipeurl + 'recipes/1')

    assert created_on == "2015-08-06 15:12"
    assert last_brewed_on == "2015-11-02 06:22"
    assert username == "don.pablo"
    assert title == "The Original"
    assert orientation == "Regular"
    assert rating == "5"
    assert general_recipe_comment == "No stirring, just hard pour."
    assert bean_name == "Arabica"
    assert roast == "Medium"
    assert grind == "Regular"
    assert orientation == "Capresso M2"
    assert total_bean_amount == "18"
    assert bean_units == "g"
    assert water_type == "tap"
    assert total_water_amount == "8"
    assert water_units == "oz"
    assert temp == "176"
    assert brew_count == "524"
    assert total_duration == "140"



    with requests_mock.Mocker() as mock:
        mock.post('https://brew-keeper-api.herokuapp.com/api/user/don.pablo/', text='posted')

        assert requests.post('https://brew-keeper-api.herokuapp.com/api/user/don.pablo/').text == 'posted'



# @requests_mock.Mocker()
# def test_recipe_creation(m):
#     userurl = 'https://brew-keeper-api.herokuapp.com/api/user/don.pablo/'
#     with open('fixtures/examples.json') as data:
#         m.post(userurl + 'recipes/')
#



# don.pablo = user_id(1)
#
# def test_get_user():
#     assert don.pablo.user_id == 1
#     assert don.pablo.user_id != 2
#
# def test_get_recipe():
#     assert
