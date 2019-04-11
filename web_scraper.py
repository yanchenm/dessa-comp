import re
import os
import json
import requests
import pymongo


from datetime import datetime
from bs4 import BeautifulSoup


base_url = 'https://www.kickstarter.com/discover/advanced?category_id=12&woe_id=0&sort=most_funded&seed=2591527'


def scrape_project(project_data):
    json_data = json.loads(project_data)
    final_data = {}

    # Copy base json project data
    final_data['id'] = json_data['id']
    final_data['name'] = json_data['name']
    final_data['blurb'] = json_data['blurb']
    final_data['link'] = json_data['urls']['project']
    final_data['status'] = json_data['state']
    final_data['backers'] = json_data['backers_count']
    final_data['location'] = json_data['location']['displayable_name']

    final_data['finances'] = {}
    final_data['finances']['goal'] = json_data['goal']
    final_data['finances']['pledged'] = json_data['pledged']
    final_data['finances']['currency'] = json_data['currency']
    final_data['finances']['percent_funded'] = json_data['percent_funded']

    # Scrape description, rewards tiers, etc. from individual project page
    print('Scraping {}...'.format(json_data['name']))
    project_url = json_data['urls']['project']

    page = requests.get(project_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    description_container = soup.find(
        'div', {'class': 'description-container'})

    description_content = description_container.find_all(text=True)
    description_content = list(
        filter(lambda x: x != '\n', description_content))

    return final_data


if __name__ == '__main__':

    projects_html = []
    projects = []

    if not os.path.isdir('./data'):
        os.mkdir('./data')

    # if os.path.isfile('./data/temp_project_list'):
    #     with open('./data/temp_project_list', 'r') as file:
    #         projects = [line.rstrip('\n') for line in file]

    else:
        for i in range(1, 2):

            print('Scraping page {}...'.format(i))

            page = requests.get('{}&page={}'.format(base_url, i))
            soup = BeautifulSoup(page.content, 'html.parser')

            projects_list = soup.find('div', {'id': 'projects_list'})
            projects_outer = projects_list.find_all(
                'div', {'class': 'grid-row'})

            for div in projects_outer:
                projects_html.extend(div.find_all(
                    'div', {'class': 'js-react-proj-card'}))

            for project in projects_html:
                projects.append(scrape_project(project))

        # with open('./data/temp_project_list', 'w') as file:
        #     for item in projects:
        #         file.write('%s\n' % item)
