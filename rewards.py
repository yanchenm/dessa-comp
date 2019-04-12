''' Script that turns web scraper json data into tabular rewards data for analysis '''

import numpy as np
import pandas as pd

import json


def assess_project(project_data):
    temp = pd.DataFrame(columns=['id', 'name', 'status', 'launch_date', 'deadline',
                                 'goal', 'pledged', 'currency', 'total_backers', 'reward_amount',
                                 'reward_currency', 'reward_title', 'reward_description',
                                 'reward_backers'])

    row = {'id': project_data['id'], 'name': project_data['name'], 'status': project_data['status'],
           'launch_date': project_data['launch_date'], 'deadline': project_data['deadline'],
           'goal': project_data['finances']['goal'], 'pledged': project_data['finances']['pledged'],
           'total_backers': project_data['backers'], 'currency': project_data['finances']['currency']}

    for _, reward in project_data['rewards'].items():
        row['reward_amount'] = reward['amount']
        row['reward_currency'] = reward['currency']
        row['reward_title'] = reward['title']
        row['reward_description'] = reward['description']
        row['reward_backers'] = reward['backers']

        temp = temp.append(row, ignore_index=True)

    return temp


if __name__ == '__main__':
    with open('./data/projects.json') as json_file:
        data = json.load(json_file)

    table = pd.DataFrame(columns=['id', 'name', 'status', 'launch_date', 'deadline',
                                  'goal', 'pledged', 'total_backers', 'reward_amount',
                                  'reward_currency', 'reward_title', 'reward_description',
                                  'reward_backers'])

    for project_id, project_data in data.items():
        print('Processing project {}...'.format(project_id))
        table = table.append(assess_project(project_data), ignore_index=True)

    table.to_csv('./data/rewards.csv', index=False)
