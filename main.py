from web_scraper import scrape
from rewards import find_rewards

import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('base_url')
    parser.add_argument('output')

    args = parser.parse_args()

    scrape(args.base_url, './data/{}.json'.format(args.output))
    find_rewards('./data/{}.json'.format(args.output),
                 './data/{}_rewards.csv'.format(args.output))
