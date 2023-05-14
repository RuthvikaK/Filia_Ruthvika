from src.models import db, FiliaUser, PhotoPost

def test_editprofpage(test_client):
    prof = FiliaUser(firstname='Ruthvika', lastname='Kosuri', email='rk@uncc.edu', phone='1234567891', gender='female', major='acc_bs', grad_date='fall2023', bio='abc', profile_path='/static/profile-pics/ruth.jpeg', username='ruthK', password='cft67uhnju8')
    resp = test_client.get("http://127.0.0.1:5000/view_edit_profile")
    assert resp.status_code == 200
    assert b'Edit Profile Page' in resp.data
    assert test_client.find_element_by_css_selector('firstname').text == 'Ruthvika'
    assert test_client.find_element_by_css_selector('lastname').text == 'Kosuri'

    username_field = test_client.find_element_by_name('username')
    username_field.clear()
    username_field.send_keys('new_username')

    submit_button = test_client.find_element_by_css_selector('input[type="submit"]')
    submit_button.click()

    assert test_client.current_url == 'https://127.0.0.1:5000/view_edit_profile'
