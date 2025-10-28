import pytest
from unittest.mock import patch, mock_open, MagicMock
import pandas as pd
import utils
import os
import requests
from io import StringIO


def test_get_csv_file_name_from_url():
    url = "https://example.com/data/fatal-police-shootings-data.csv"
    expected_file_name = "fatal-police-shootings-data.csv"
    assert utils.get_csv_file_name_from_url(url) == expected_file_name


@patch('requests.get')
def test_download_csv_file_success(mock_get):
    mock_response = MagicMock()  # Używamy MagicMock zamiast requests.Response
    mock_response.status_code = 200
    mock_response.content = b'test data'
    mock_get.return_value = mock_response

    # Clean up the created file
    if os.path.exists("test.csv"):
        os.remove("test.csv")


@patch('requests.get')
def test_download_csv_file_failure(mock_get):
    url = "https://example.com/data/test.csv"
    mock_response = requests.Response()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    with patch('builtins.open', mock_open()) as mock_file:
        utils.download_csv_file(url)
        mock_file.assert_not_called()
    # Clean up the created file
    if os.path.exists("test.csv"):
        os.remove("test.csv")


@patch('pandas.read_csv')
@patch('os.path.exists')
def test_create_dataframe_from_csv_existing_file(mock_exists, mock_read_csv):
    mock_exists.return_value = True
    expected_df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    mock_read_csv.return_value = expected_df
    url = "https://example.com/data/test.csv"
    df = utils.create_dataframe_from_csv(url)
    assert df.equals(expected_df)
    mock_read_csv.assert_called_once_with('test.csv')


@patch('utils.download_csv_file')
@patch('pandas.read_csv')
@patch('os.path.exists')
def test_create_dataframe_from_csv_non_existing_file(mock_exists, mock_read_csv, mock_download):
    mock_exists.return_value = False
    expected_df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    mock_read_csv.return_value = expected_df
    url = "https://example.com/data/test.csv"

    def mock_download_side_effect(url):
        mock_exists.return_value = True

    mock_download.side_effect = mock_download_side_effect

    df = utils.create_dataframe_from_csv(url)
    assert df.equals(expected_df)
    mock_download.assert_called_once_with(url)
    mock_read_csv.assert_called_once_with('test.csv')


def test_calculate_mental_illness_percentage():
    row1 = pd.Series({True: 50, False: 50})
    row2 = pd.Series({True: 75, False: 25})
    row3 = pd.Series({False: 100})
    row4 = pd.Series({True: 0, False: 100})
    row5 = pd.Series({})

    assert utils.calculate_mental_illness_percentage(row1) == 50.0
    assert utils.calculate_mental_illness_percentage(row2) == 75.0
    assert utils.calculate_mental_illness_percentage(row3) == 0.0
    assert utils.calculate_mental_illness_percentage(row4) == 0.0
    assert utils.calculate_mental_illness_percentage(row5) == 0


def test_get_top_mental_illness_races():
    data = {'signs_of_mental_illness_percentage': pd.Series(
        {'A': 25.0, 'B': 75.0, 'C': 50.0})}
    df = pd.DataFrame(data)
    assert utils.get_top_mental_illness_races(df) == 'B'


def test_create_day_of_week_column():
    data = {'date': ['2023-01-01', '2023-01-02', '2023-01-03']}
    df = pd.DataFrame(data)
    df = utils.create_day_of_week_column(df)
    expected_days = ['Sunday', 'Monday', 'Tuesday']
    assert list(df['day_of_week']) == expected_days


def test_get_intervention_by_day_of_week():
    data = {'day_of_week': ['Monday', 'Tuesday',
                            'Monday', 'Wednesday', 'Tuesday']}
    df = pd.DataFrame(data)
    intervention_counts = utils.get_intervention_by_day_of_week(df)
    assert intervention_counts['Monday'] == 2
    assert intervention_counts['Tuesday'] == 2
    assert intervention_counts['Wednesday'] == 1


def test_translate_and_sort_days_of_week():
    data = {'day_of_week': ['Monday', 'Tuesday',
                            'Monday', 'Wednesday', 'Tuesday']}
    df = pd.DataFrame(data)
    intervention_counts = utils.get_intervention_by_day_of_week(df)
    translated_series = utils.translate_and_sort_days_of_week(
        intervention_counts)
    expected_index = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek',
                      'Piątek', 'Sobota', 'Niedziela']
    assert list(translated_series.index) == expected_index
    assert translated_series['Poniedziałek'] == 2
    assert translated_series['Wtorek'] == 2
    assert translated_series['Środa'] == 1


@patch('matplotlib.pyplot.show')
def test_plot_intervention_by_day_of_week(mock_show):
    data = {'Poniedziałek': 2, 'Wtorek': 2, 'Środa': 1,
            'Czwartek': 0, 'Piątek': 0, 'Sobota': 0, 'Niedziela': 0}
    intervention_by_day = pd.Series(data)
    utils.plot_intervention_by_day_of_week(intervention_by_day)
    mock_show.assert_called_once()


@patch('requests.get')
@patch('pandas.read_html')
def test_create_dataframe_from_html_success(mock_read_html, mock_get):
    url = "https://example.com/tables.html"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '<html><body><table></table></body></html>'
    mock_get.return_value = mock_response
    expected_df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    mock_read_html.return_value = [expected_df]

    df = utils.create_dataframe_from_html(url)
    assert df.equals(expected_df)
    mock_read_html.assert_called_once_with(
        '<html><body><table></table></body></html>', header=0)


@patch('requests.get')
@patch('pandas.read_html')
def test_create_dataframe_from_html_no_tables(mock_read_html, mock_get):
    url = "https://example.com/tables.html"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '<html><body></body></html>'
    mock_get.return_value = mock_response
    mock_read_html.return_value = []

    df = utils.create_dataframe_from_html(url)
    assert df is None
    mock_read_html.assert_called_once_with(
        '<html><body></body></html>', header=0)


@patch('requests.get')
def test_create_dataframe_from_html_request_exception(mock_get):
    url = "https://example.com/tables.html"
    mock_get.side_effect = requests.exceptions.RequestException(
        "Test Exception")

    df = utils.create_dataframe_from_html(url)
    assert df is None


def test_map_state_codes():
    # Sample DataFrames for testing
    df = pd.DataFrame({'state': ['TX', 'CA', 'NY', 'AZ']})
    states_codes_df = pd.DataFrame({
        'USPS (& ANSI)': ['TX', 'CA', 'NY'],
        'Name': ['Texas', 'California', 'New York']
    })

    # Call the function
    result_df = utils.map_state_codes(df.copy(), states_codes_df.copy())

    # Expected DataFrame after mapping
    expected_df = pd.DataFrame(
        {'state': ['Texas', 'California', 'New York', 'AZ']})

    # Assert that the DataFrames are equal
    pd.testing.assert_frame_equal(result_df, expected_df)


def test_map_state_population():
    # Sample DataFrames for testing
    df = pd.DataFrame({'state': ['Texas', 'California', 'New York']})
    states_population_df = pd.DataFrame({
        'State': ['Texas', 'California', 'New York'],
        'Census population, April 1, 2020 [1][2]': [29145505, 39538223, 20201249]
    })

    # Call the function
    result_df = utils.map_state_population(
        df.copy(), states_population_df.copy())

    # Expected DataFrame after mapping
    expected_df = pd.DataFrame({
        'state': ['Texas', 'California', 'New York'],
        'population': [29145505, 39538223, 20201249]
    })

    # Assert that the DataFrames are equal
    pd.testing.assert_frame_equal(result_df, expected_df)
