import re
import os
import json
import requests
import pymongo


from datetime import datetime
from bs4 import BeautifulSoup


base_url = 'https://www.kickstarter.com/discover/advanced?category_id=12&woe_id=0&sort=most_funded&seed=2591527'


def scrape_project(json_data):
    final_data = {}

    # Copy base json project data
    final_data['id'] = json_data['id']
    final_data['name'] = json_data['name']
    final_data['blurb'] = json_data['blurb']
    final_data['link'] = json_data['urls']['web']['project']
    final_data['status'] = json_data['state']
    final_data['backers'] = json_data['backers_count']
    final_data['location'] = json_data['location']['displayable_name']

    final_data['launch_date'] = datetime.utcfromtimestamp(
        int(json_data['launched_at'])).strftime('%Y-%m-%d %H:%M:%S')

    final_data['deadline'] = datetime.utcfromtimestamp(
        int(json_data['deadline'])).strftime('%Y-%m-%d %H:%M:%S')

    final_data['finances'] = {}
    final_data['finances']['goal'] = json_data['goal']
    final_data['finances']['pledged'] = json_data['pledged']
    final_data['finances']['currency'] = json_data['currency']
    final_data['finances']['percent_funded'] = json_data['percent_funded']

    # Scrape description from individual project page
    print('Scraping {}...'.format(json_data['name']))
    project_url = json_data['urls']['web']['project']

    page = requests.get(project_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    description_container = soup.find(
        'div', {'class': 'description-container'})

    # Format description text in readable string form
    description_content = description_container.find_all('p', text=True)
    description_content = [p.text for p in description_content]

    description_content = list(
        filter(lambda x: (x != '\n') and (x != '\xa0') and (x != ' '), description_content))[1:]

    description_string = ''

    for string in description_content:
        string = string.strip()
        string = re.sub(r'\xa0', '', string)

        description_string = description_string + ' ' + string

    final_data['description'] = description_string

    # Scrape reward tiers information from project page
    tiers = {}

    rewards_container = soup.find('div', {'class': 'js-project-rewards'})
    rewards_list = rewards_container.find_all(
        'li', {'class': 'pledge-selectable-sidebar'})

    for reward in rewards_list:
        if (reward['data-reward-id'] == 0):
            continue

        reward_data = {}

        # Scrape tier amount and currency
        reward_amount_string = reward.find('span', {'class': 'money'}).text
        reward_match = re.match(r'(\D+)(\d+[,.]?\d*)', reward_amount_string)

        reward_data['amount'] = int(reward_match.group(2).replace(',', ''))
        reward_data['currency'] = reward_match.group(1).strip()

        # Scrape reward title
        try:
            reward_data['title'] = reward.find(
                'h3', {'class': 'pledge__title'}).text.strip('\n')
        except (AttributeError):
            reward_data['title'] = None

        # Scrape reward description and convert to readable form
        try:
            reward_description = reward.find(
                'div', {'class': 'pledge__reward-description'}).find_all('p', text=True)

            reward_description = [p.text for p in reward_description]

            reward_description = list(
                filter(lambda x: (x != '\n') and (x != '\xa0') and (x != ' '), reward_description))[1:]

            reward_description_string = ''

            for string in reward_description:
                string = string.strip()
                string = re.sub(r'\xa0', '', string)

                reward_description_string = reward_description_string + ' ' + string

            reward_data['description'] = reward_description_string

        except (AttributeError):
            reward_data['description'] = None

        # Scrape number of backers for each tier
        try:
            reward_backer_string = reward.find(
                'span', {'class': 'pledge__backer-count'}).text.strip()

            reward_data['backers'] = int(
                re.match(r'(\S+) \D+', reward_backer_string).group(1).replace(',', ''))
        except (AttributeError):
            reward_data['backers'] = None

        tiers[reward['data-reward-id']] = reward_data

    final_data['rewards'] = tiers

    return final_data


if __name__ == '__main__':

    projects = {}

    if not os.path.isdir('./data'):
        os.mkdir('./data')

    else:
        for i in range(1, 201):

            print('Scraping page {}...'.format(i))

            projects_html = []

            page = requests.get('{}&page={}'.format(base_url, i))
            soup = BeautifulSoup(page.content, 'html.parser')

            projects_list = soup.find('div', {'id': 'projects_list'})
            projects_outer = projects_list.find_all(
                'div', {'class': 'grid-row'})

            for div in projects_outer:
                projects_html.extend(div.find_all(
                    'div', {'class': 'js-react-proj-card'}))

            for project in projects_html:
                json_data = json.loads(project['data-project'])
                projects[json_data['id']] = scrape_project(json_data)

    with open('./data/projects.json', 'w') as file:
        json.dump(projects, file)
