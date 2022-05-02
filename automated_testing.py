# build weighted from pageview.csv
import re
import random
import time

import requests
import pandas as pd
# closes to me is a, farthest is c
REPLICA_DICT_IP = {"p5-http-a.5700.network": "50.116.41.109",
                   "p5-http-b.5700.network": "45.33.50.187",
                   "p5-http-c.5700.network": "194.195.121.150",
                   "p5-http-d.5700.network": "172.104.144.157",
                   "p5-http-e.5700.network": "172.104.110.211",
                   "p5-http-f.5700.network": "88.80.186.80",
                   "p5-http-g.5700.network": "172.105.55.115",
                  }

def build_associative_arr(file_name):
    list_content = []
    list_weight = []

    with open(file_name, mode="r", encoding="utf8") as pviews:
        for line in pviews.readlines():
            try:
                if "\"" in line:
                    temp = line.split("\",")
                    temp[0] = temp[0].replace("\"",'')
                else:
                    temp = line.split(",")
                content_add = temp[0].strip()
                weight_add = int(temp[1].strip())
                list_content.append(content_add)
                list_weight.append(weight_add)
            except ValueError as e:
                print(e, "check if content or weight is invalid")
                print(f"content: {temp[0].strip()}")
                print(f"weight:")

    print("==========================\n")
    return list_content, list_weight

def get_list_pages_following_distribution_cumulative_weight(list_content_in, list_weight_in, amount):
    return random.choices(list_content_in, cum_weights=list_weight_in,k=amount)

#use abs
def get_list_pages_following_distribution_abs_weight(list_content_in, list_weight_in, amount):
    return random.choices(list_content_in, weights=list_weight_in, k=amount)

def make_matching_list(list_column_names, list_input):
    dict_ = {}
    if len(list_column_names) != len(list_input):
        print("mismatch in data and columns")
        raise RuntimeError
    else:
        for i in range(len(list_column_names)):
            dict_[list_column_names[i]] = list_input[i]
    return dict_

def make_df_for_analysis(df_with_col,list_pages, http_target_ip, http_target_port):
    df_columns = list(df_with_col.columns)

    total_page_request_len = len(list_pages)
    quarter_amt_abs = total_page_request_len // 4
    quarter_tracker = total_page_request_len // 4
    percent_counter = 25
    counter = 0
    for each in list_pages:
        if counter == quarter_tracker:
            quarter_tracker += quarter_amt_abs
            print(f"Progressed through {percent_counter}% of requests")
            percent_counter += 25

        target_page = each
        list_data = []
        d_temp = {}

        list_data.append(target_page)
        request_query = f'http://{http_target_ip}:{http_target_port}/{target_page}'

        start_time = time.perf_counter()
        try:
            requested_page = requests.get(request_query)
            end_time = time.perf_counter()
            status_code_rcvd = requested_page.status_code
        except requests.exceptions.ConnectionError:
            print(f"Possible Query Error: \n{request_query}")
            print(f"Page may be invalid for {target_page}, Unable to request")
            end_time = 999999999
            status_code_rcvd = 404

        #add to slow request to not be seen as ddos
        #time.sleep(0.2)

        duration_request = round(end_time - start_time, 5)
        if duration_request >= 999:
            duration_request = 999

        list_data.append(duration_request)
        list_data.append(status_code_rcvd)

        d_temp = make_matching_list(df_columns, list_data)
        d_temp = pd.DataFrame([d_temp])
        df_with_col = pd.concat([df_with_col, d_temp], ignore_index=True)
        counter += 1

    print(f"Progressed through 100% of requests")
    print("----------------\n")
    return df_with_col

def get_stats_for_one_page(df_in, page_name):
    temp_df = df_in[df_in['content_requested'] == page_name]

    max_val = round(temp_df['http_time_sec'].max(),5)
    min_val = round(temp_df['http_time_sec'].min(),5)
    avg_overall = round(temp_df['http_time_sec'].mean(),5)

    max_val_index = temp_df['http_time_sec'].idxmax()

    df_without_max = temp_df.drop(axis=0,index=max_val_index)
    avg_post_cache = round(df_without_max['http_time_sec'].mean(),5)

    return page_name,max_val,min_val,avg_overall,avg_post_cache

def build_analysis_df(df_raw_res, df_analysis, page_name):
    results_analysis_one_page = get_stats_for_one_page(df_raw_res, page_name)
    d_analysis_temp = make_matching_list(list(df_analysis.columns), results_analysis_one_page)
    d_analysis_temp_df = pd.DataFrame([d_analysis_temp])
    analysis_results = pd.concat([df_analysis, d_analysis_temp_df], ignore_index=True)
    return analysis_results


def main():
    df_columns =['content_requested','http_time_sec','status_code']
    df_results = pd.DataFrame(columns=df_columns)
    file_name = "pageviews.csv"
    list_content, list_weight = build_associative_arr(file_name)
    print(f"done building associative array from {file_name}")
    NUMBER_OF_REQUEST = 100

    mandatory = ['Main_Page','-','India','Coronavirus','Doja_Cat']
    list_page_requests_distributed = get_list_pages_following_distribution_abs_weight(list_content,list_weight,NUMBER_OF_REQUEST)

    #add mandatory id not in list page_request
    for each in mandatory:
        if each not in list_page_requests_distributed:
            list_page_requests_distributed.append(each)


    target_ip = REPLICA_DICT_IP["p5-http-a.5700.network"]
    target_port = 40015

    df_results = make_df_for_analysis(df_results, list_page_requests_distributed,target_ip,target_port)

    # running at least twice so every request is at least hit twice, can see difference between caching and not caching
    df_results = make_df_for_analysis(df_results, list_page_requests_distributed, target_ip, target_port)
    df_results = make_df_for_analysis(df_results, list_page_requests_distributed, target_ip, target_port)

    #sorting for easy viewing of raw
    df_results = df_results.sort_values(by=['content_requested','http_time_sec'], ascending=[True,False],)

    df_results.to_csv('auto_test_results.csv',index=False)
    print("Done getting raw results\n")

    analysis_column_names = ['page_content','max_latency','min_latency','overall_avg_latency','post_cache_latency']
    analysis_results = pd.DataFrame(columns=analysis_column_names)

    unique_pages = list(set(list_page_requests_distributed))
    total_unique_count = len(unique_pages)

    for each in mandatory:
        analysis_results = build_analysis_df(df_results,analysis_results,each)
        unique_pages.remove(each)

    quarter_amt = total_unique_count // 4
    currnet_abs_tracker = quarter_amt
    quarter_tracker = 25

    for i in range(len(unique_pages)):
        if i == currnet_abs_tracker:
            print(f"Analyzed {quarter_tracker}% pages")
            quarter_tracker += 25
            currnet_abs_tracker += quarter_amt

        results_analysis_one_page = get_stats_for_one_page(df_results, unique_pages[i])
        d_analysis_temp = make_matching_list(analysis_column_names, results_analysis_one_page)
        d_analysis_temp_df = pd.DataFrame([d_analysis_temp])
        analysis_results = pd.concat([analysis_results, d_analysis_temp_df], ignore_index=True)

    print(f"Analyzed {quarter_tracker}% pages")
    analysis_results.to_csv('analyses_results.csv',index=False )



    #df_only_one = df_results[df_results['content_requested'] == content_page]
    #print(df_only_one)
    #print(f"Content: {requested_page.status_code}")


main()