import sqlalchemy as db # helps process with plenty of database
import sqlite3          # lite version of mysql
import psycopg2         # helps to use PostgreSQL for Python
import redis            # handling of database (which are key-value)


import pandas as pd
import numpy as np
from scipy import stats
import json
import logging
from multiprocessing import Pool
from datetime import datetime


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def detect_outliers(data, threshold=3):                             # detect outliers using Z-score for numerical data.
    numerical_data = data.select_dtypes(include=[np.number])
    if not numerical_data.empty:
        z_scores = np.abs(stats.zscore(numerical_data))
        outliers = (z_scores > threshold).any(axis=1)
        return data[outliers]
    return pd.DataFrame()


def check_data_distribution(data, alpha=0.05):      # check numerical data distributions, customizable significance level.
    results = {}
    numerical_columns = data.select_dtypes(include=[np.number]).columns
    for column in numerical_columns:
        stat, p_value = stats.shapiro(data[column].dropna())
        results[column] = {'stat': stat, 'p_value': p_value, 'normal': p_value > alpha}
    return results


def apply_validation_rules(data, rules):            # customizable validation rules defined as a dictionary.
    errors = []
    for rule_name, rule_func in rules.items():
        if not rule_func(data):
            errors.append(f"Validation rule failed: {rule_name}")
    return errors


def check_completeness(data, required_fields):              # check if all required fields are present and not empty.
    missing_data = data[required_fields].isnull().any(axis=1)
    if missing_data.any():
        missing_count = missing_data.sum()
        logging.info(f"Completeness check failed: {missing_count} entries missing required data.")
        return False
    return True

def check_consistency(data, date_fields, date_format="%Y-%m-%d"):       # check for consistent data formats, especially date formats.
    inconsistencies = []
    for field in date_fields:
        try:
            pd.to_datetime(data[field], format=date_format)
        except ValueError as e:
            inconsistencies.append(field)
    if inconsistencies:
        logging.info(f"Consistency check failed: Date format issues in {', '.join(inconsistencies)}.")
        return False
    return True


def check_uniqueness(data, unique_fields):  # Ensure certain fields are unique within the dataset.
    for field in unique_fields:
        if data[field].duplicated().any():
            logging.info(f"Uniqueness check failed: Duplicates found in {field}.")
            return False
    return True

def check_relevance(data, field, valid_values):         # check if values in a specific field are within an allowed set.
    irrelevant_data = ~data[field].isin(valid_values)
    if irrelevant_data.any():
        irrelevant_count = irrelevant_data.sum()
        logging.info(f"Relevance check failed: {irrelevant_count} irrelevant entries found in {field}.")
        return False
    return True


def validate_data(data):
    existing_emails = {'user@example.com'}  # assume we have a set of existing emails
    try:
        if not check_completeness(data):
            raise ValueError("Data incomplete.")
        if not check_consistency(data):
            raise ValueError("Data inconsistent.")
        if not check_uniqueness(data, existing_emails):
            raise ValueError("Data not unique.")
        if not check_relevance(data):
            raise ValueError("Data not relevant.")
    except ValueError as e:
        logging.error(f"Validation failed for {data['email']}: {e}")
        return False
    return True

def process_data_in_batches(dataset):
    with Pool(processes=4) as pool:  # adjust number of processes based on your environment
        results = pool.map(validate_data, dataset)
    return results


validation_rules = {
    "Non-negative age": lambda df: df['age'].min() >= 0,
    "Valid email": lambda df: df['email'].str.contains('@').all()
    # .............
}


data = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie', 'Dave'],
    'email': ['alice@example.com', 'bob@example.com', 'charlie@test.com', 'dave@example.com'],
    'date_of_birth': ['1990-01-01', '1991-02-30', '1992-03-15', '1993-04-20'],  # Note: invalid date
    'role': ['Manager', 'Analyst', 'Clerk', 'Intern']
})

outliers = detect_outliers(data)
distribution = check_data_distribution(data[['name', 'email']])

complete = check_completeness(data, ['name', 'email', 'date_of_birth', 'role'])
consistent = check_consistency(data, ['date_of_birth'])
unique = check_uniqueness(data, ['email'])
relevant = check_relevance(data, 'role', ['Manager', 'Analyst', 'Intern'])

if not outliers.empty:
    logging.info(f"Outliers detected:\n{outliers}")

for col, result in distribution.items():
    if result['p_value'] < 0.05:
        logging.info(f"Data in {col} does not follow normal distribution (p={result['p_value']:.3f}).")


else:
    logging.info(f"Data Completeness: {'Passed' if complete else 'Failed'}")
    logging.info(f"Data Consistency: {'Passed' if consistent else 'Failed'}")
    logging.info(f"Data Uniqueness: {'Passed' if unique else 'Failed'}")
    logging.info(f"Data Relevance: {'Passed' if relevant else 'Failed'}")


