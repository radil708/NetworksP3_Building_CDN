# build weighted from pageview.csv
import re
import random
import time

import requests
import pandas as pd

# closes to me is a, farthest is c
# Using this to show ip addresses of servers
REPLICA_DICT_IP = {"p5-http-a.5700.network": "50.116.41.109",
                   "p5-http-b.5700.network": "45.33.50.187",
                   "p5-http-c.5700.network": "194.195.121.150",
                   "p5-http-d.5700.network": "172.104.144.157",
                   "p5-http-e.5700.network": "172.104.110.211",
                   "p5-http-f.5700.network": "88.80.186.80",
                   "p5-http-g.5700.network": "172.105.55.115",
                   }

DEFAULT_REQUEST_AMT = 100
DEFAULT_PORT = 40015
DEFAULT_SERVER_TARGET = REPLICA_DICT_IP["p5-http-a.5700.network"]

# Print statement separators
PLUS_DIVIDER = "+++++++++++++++++++++++++++++++++++++++++++++++\n"
MINUS_DIVIDER = "----------------------------------------------\n"
EQUALS_DIVIDER = "==============================================\n"


def build_associative_arr(file_name: str = "pageviews.csv", display_prints=False):
    """
    This function is used to open the pageviews.csv file and build two lists. These
    lists are associative arrays where one list contains the page content and the other
    contains a the amount of times a user has queried for that page.

    How to use:
        list_content, list_weight = build_associative_arr()

    :param file_name: (str) path to .csv file containing pageview information.
                        Default value is "pageviews.csv"
    :param display_prints: (bool) if true, will print statements to the terminal.
            > errors will print regardless of value
    :return: tuple (list, list) Two lists which act as associative arrays. The former contains
                the content name and the latter contains view count for the content. Default value is false.
    """

    list_content = []
    list_weight = []

    with open(file_name, mode="r", encoding="utf8") as pviews:
        for line in pviews.readlines():
            try:
                if "\"" in line:
                    temp = line.split("\",")
                    temp[0] = temp[0].replace("\"", '')
                else:
                    temp = line.split(",")
                content_add = temp[0].strip()
                weight_add = int(temp[1].strip())
                list_content.append(content_add)
                list_weight.append(weight_add)

                if display_prints == True:
                    print(f"Content: {content_add}\t Weight: {weight_add} successfully added to array")
                    print(MINUS_DIVIDER)

            except ValueError as e:
                print(e, "check if content or weight is invalid, weight must be an int")
                print(f"content: {content_add}")
                print(f"weight: {temp[1].strip()}")
                print("Cannot add values to associative arrays")
                print(MINUS_DIVIDER)

    if display_prints == True:
        print(PLUS_DIVIDER)

    return list_content, list_weight


def get_list_pages_following_distribution_cumulative_weight(list_content_in, list_weight_in, amount):
    return random.choices(list_content_in, cum_weights=list_weight_in, k=amount)


# use abs
def get_list_pages_following_distribution_abs_weight(list_content_in: list, list_weight_in: list, amount: int) -> list:
    """
    Generates a list of size amount. Each element is the name of a page from list_content_in.
    The elements chosen following weighted distribution. i.e. if element Main_Page has a high weight
    then the list generated will be populated with a lot of 'Main_Page; elements.
    The list_weight_in is an associative array for list_content_in which contains the weights of each page.

    How to use:
        list_content, list_weight = build_associative_arr()
        elements_distributed_weight = get_list_pages_following_distribution_abs_weight(list_content, list_weight_in,
        amount)

    :param list_content_in: (list) Contains a list of page names
    :param list_weight_in: (list) an associative array for list_content_in which contains the weights of each page.
    :param amount:
    :return:
    """
    return random.choices(list_content_in, weights=list_weight_in, k=amount)


def make_matching_list(list_1_in: list, list_2_in: list) -> dict:
    """
    Helper function to create a dictionary from two lists/associative arrays.
    Useful for building dictionaries that are used in dataframes. These lists
    need to be the same size. If not an error will be raised.

    How to use:
        list_1 = [ key1, key2, key3 ]
        list_2 = [ value1, value2, value3 ]
        dict_out =  make_matching_list(list_1, list_2)

    :param list_1_in: (list) The list containing keys for the dictionary. This should not
                        contain duplicate values.
    :param list_2_in: (list) The list containing values for the dictionary.
    :return: (dict) A dictionary where the keys come from the list_1, and the values
                come from list_2
    """

    dict_ = {}
    if len(list_1_in) != len(list_2_in):
        print("mismatch in data and columns")
        raise RuntimeError
    else:
        for i in range(len(list_1_in)):
            dict_[list_1_in[i]] = list_2_in[i]
    return dict_


def make_df_for_analysis(df_with_col: pd.DataFrame, list_pages: list, http_target_ip: str, http_target_port: int,
                         display: bool = True) -> pd.DataFrame:
    """
    This function makes a dataframe containing raw time data that shows the speed of the response from the http
        server.

        How to use:
            - First make sure that the http servers are running, and mark the server ip address and server port

            list_content, list_weight = build_associative_arr()
            elements_distributed_weight = get_list_pages_following_distribution_abs_weight(list_content, list_weight_in,
            amount)

            df_in = pandas.DataFrame(columns = [ 'content_requested', 'http_time_sec', 'status_code' ])

            df_out = make_df_for_analysis(df_in, elements_distributed_weight, server_ip, server_port)

    :param df_with_col: a dataframe containing the column names in this order:
                            'content_requested', 'http_time_sec', 'status_code'
    :param list_pages: This contains a list of pages that will be sent as queries to the http server.
                        ideally the value passed in for this param is the output of the function
                        get_list_pages_following_distribution_abs_weight
    :param http_target_ip: (str) The ip address of the http server to query
    :param http_target_port: (int) The port of the http server to query
    :param display: (bool) if true, will print statements to the terminal
    :return: (pd.DataFrame) a dataframe containing speed of requests data
    """
    df_columns = list(df_with_col.columns)

    total_page_request_len = len(list_pages)
    quarter_amt_abs = total_page_request_len // 4
    quarter_tracker = total_page_request_len // 4
    percent_counter = 25
    counter = 0
    for each in list_pages:
        if counter == quarter_tracker:
            quarter_tracker += quarter_amt_abs
            if display == True:
                print(f"Progressed through {percent_counter}% of requests")
            percent_counter += 25

        target_page = each
        list_data = []

        list_data.append(target_page)
        request_query = f'http://{http_target_ip}:{http_target_port}/{target_page}'

        start_time = time.perf_counter()
        try:
            requested_page = requests.get(request_query)
            end_time = time.perf_counter()
            status_code_rcvd = requested_page.status_code
        except requests.exceptions.ConnectionError:
            if display == True:
                print(f"Possible Query Error: \n{request_query}")
                print(f"Page may be invalid for {target_page}, Unable to request")
            end_time = 999999999
            status_code_rcvd = 404

        # time.sleep(0.2)

        duration_request = round(end_time - start_time, 5)
        if duration_request >= 999:
            duration_request = 999

        list_data.append(duration_request)
        list_data.append(status_code_rcvd)

        d_temp = make_matching_list(df_columns, list_data)
        d_temp = pd.DataFrame([d_temp])
        df_with_col = pd.concat([df_with_col, d_temp], ignore_index=True)
        counter += 1

    if display == True:
        print(f"Progressed through 100% of requests")
        print(MINUS_DIVIDER)

    return df_with_col


def get_stats_for_one_page(df_in: pd.DataFrame, page_name: str) -> tuple:
    """
    This function takes is meant to take in the output of make_df_for_analysis.
    It filters for a specific page name and obtains data for max, min, avg, and post-cache
    http response speed in seconds. These values are returned as a tuple

    How to use:

        df_out = make_df_for_analysis(df_in, elements_distributed_weight, server_ip, server_port)
        example_page = Main_Page
        page_name, max_val, min_val, avg_overall, avg_post_cache = get_stats_for_one_page(df_out, example_page)

    :param df_in: (pd.DataFrame) a dataframe containing the follolwing columns
    :param page_name: (str) a string representing a page name
    :return: (tuple) a quintuple of floats representing max response time, min response time,
                    average response time, average response time post cache.
    """
    temp_df = df_in[df_in['content_requested'] == page_name]

    max_val = round(temp_df['http_time_sec'].max(), 5)
    min_val = round(temp_df['http_time_sec'].min(), 5)
    avg_overall = round(temp_df['http_time_sec'].mean(), 5)

    max_val_index = temp_df['http_time_sec'].idxmax()

    df_without_max = temp_df.drop(axis=0, index=max_val_index)
    avg_post_cache = round(df_without_max['http_time_sec'].mean(), 5)

    return page_name, max_val, min_val, avg_overall, avg_post_cache


def build_analysis_df(df_raw_res: pd.DataFrame, df_analysis: pd.DataFrame, page_name: str) -> pd.DataFrame:
    """
    This will create a csv file containing max response time, min response time,
                    average response time, average response time post cache per page
    :param df_raw_res: (pd.Dataframe) the output of make_df_for_analysis
    :param df_analysis:
    :param page_name:
    :return:
    """
    results_analysis_one_page = get_stats_for_one_page(df_raw_res, page_name)
    d_analysis_temp = make_matching_list(list(df_analysis.columns), list(results_analysis_one_page))
    d_analysis_temp_df = pd.DataFrame([d_analysis_temp])
    analysis_results = pd.concat([df_analysis, d_analysis_temp_df], ignore_index=True)
    return analysis_results


def main():

    df_columns = ['content_requested', 'http_time_sec', 'status_code']
    df_results = pd.DataFrame(columns=df_columns)
    file_name = "pageviews.csv"
    list_content, list_weight = build_associative_arr(file_name)

    number_of_requests = DEFAULT_REQUEST_AMT

    mandatory = ['Main_Page', '-', 'India', 'Coronavirus', 'Doja_Cat']
    list_page_requests_distributed = get_list_pages_following_distribution_abs_weight(list_content, list_weight,
                                                                                      number_of_requests)

    # add mandatory id not in list page_request
    for each in mandatory:
        if each not in list_page_requests_distributed:
            list_page_requests_distributed.append(each)

    target_ip = DEFAULT_SERVER_TARGET
    target_port = DEFAULT_PORT

    df_results = make_df_for_analysis(df_results, list_page_requests_distributed, target_ip, target_port)

    # running at least twice so every request is at least hit twice, can see difference between caching and not caching
    df_results = make_df_for_analysis(df_results, list_page_requests_distributed, target_ip, target_port)
    df_results = make_df_for_analysis(df_results, list_page_requests_distributed, target_ip, target_port)

    # sorting for easy viewing of raw
    df_results = df_results.sort_values(by=['content_requested', 'http_time_sec'], ascending=[True, False], )

    df_results.to_csv('auto_test_results.csv', index=False)
    print("Done getting raw results\n")

    analysis_column_names = ['page_content', 'max_latency', 'min_latency', 'overall_avg_latency', 'post_cache_latency']
    analysis_results = pd.DataFrame(columns=analysis_column_names)

    unique_pages = list(set(list_page_requests_distributed))
    total_unique_count = len(unique_pages)

    for each in mandatory:
        analysis_results = build_analysis_df(df_results, analysis_results, each)
        unique_pages.remove(each)

    quarter_amt = total_unique_count // 4
    currnet_abs_tracker = quarter_amt
    quarter_tracker = 25

    for i in range(len(unique_pages)):
        if i == currnet_abs_tracker:
            print(f"Analyzed {quarter_tracker}% pages")
            quarter_tracker += 25
            currnet_abs_tracker += quarter_amt

        analysis_results = build_analysis_df(df_results,analysis_results,unique_pages[i])

    print(f"Analyzed {quarter_tracker}% pages")
    analysis_results.to_csv('analyses_results.csv', index=False)


if __name__ == "__main__":
    main()
