import logging
import os
import time
import pandas as pd
from datetime import datetime, timedelta

from azure.identity import AzureCliCredential
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.applicationinsights import ApplicationInsightsDataClient
from azure.core.exceptions import ResourceNotFoundError

# --- 配置 --- #
FUNCTION_APP_NAME = "airquality"  # 请确保这是你的 Function App 名称
RESOURCE_GROUP_NAME = "airquality_rg" # 请确保这是你的资源组名称
TEST_SCENARIOS = {
    "low": 100,
    "medium": 500,
    "high": 1000,
    "very_high": 2000
}
WAIT_TIME_SECONDS = 180  # 更新配置后等待函数执行的时间
QUERY_TIME_RANGE_MINUTES = 5 # 从多长时间范围内查询日志
# --- END 配置 --- #

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_subscription_id():
    """获取当前活动的 Azure 订阅 ID"""
    import subprocess
    import json
    try:
        result = subprocess.run(["az", "account", "show"], capture_output=True, text=True, check=True, shell=True)
        return json.loads(result.stdout)["id"]
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        logging.error(f"无法获取订阅 ID。请确保已通过 'az login' 登录。错误: {e}")
        exit(1)

def get_function_app_details(client: WebSiteManagementClient, rg_name: str, app_name: str):
    """获取 Function App 的详细信息，包括 App Insights Key"""
    try:
        return client.web_apps.get(rg_name, app_name)
    except ResourceNotFoundError:
        logging.error(f"找不到 Function App '{app_name}' 在资源组 '{rg_name}' 中。")
        exit(1)

def update_batch_size(client: WebSiteManagementClient, rg_name: str, app_name: str, batch_size: int):
    """更新 Function App 的 BATCH_SIZE 配置"""
    logging.info(f"正在将 BATCH_SIZE 更新为 {batch_size}...")
    try:
        app_settings = client.web_apps.list_application_settings(rg_name, app_name)
        app_settings.properties["BATCH_SIZE"] = str(batch_size)
        client.web_apps.update_application_settings(rg_name, app_name, app_settings)
        logging.info("配置更新成功。等待应用重启...")
        time.sleep(60) # 等待应用重启
    except Exception as e:
        logging.error(f"更新配置失败: {e}")
        raise

def trigger_data_generation(client: WebSiteManagementClient, rg_name: str, app_name: str):
    """手动触发 GenerateAirQualityData 函数"""
    logging.info("正在触发 'GenerateAirQualityData' 函数...")
    try:
        # 注意：这是一个异步操作，我们不等待它完成
        client.web_apps.begin_trigger_function(rg_name, app_name, "GenerateAirQualityData", "")
        logging.info("触发请求已发送。")
    except Exception as e:
        logging.error(f"触发函数失败: {e}")
        raise

def query_execution_logs(app_insights_client: ApplicationInsightsDataClient, app_id: str, duration_minutes: int) -> pd.DataFrame:
    """查询 Application Insights 获取 ProcessAirQualitySummary 的执行时长"""
    logging.info(f"正在从 Application Insights 查询过去 {duration_minutes} 分钟的日志...")
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=duration_minutes)
    query = (
        f"requests "
        f"| where timestamp > ago({duration_minutes}m) "
        f"| where name == 'ProcessAirQualitySummary' "
        f"| where success == true "
        f"| extend record_count = toint(customDimensions['record_count']) "
        f"| project timestamp, duration, record_count"
    )
    try:
        response = app_insights_client.query.execute(app_id, query, timespan=(start_time, end_time))
        if response.tables:
            df = pd.DataFrame(response.tables[0].rows, columns=[col.name for col in response.tables[0].columns])
            logging.info(f"查询成功，找到 {len(df)} 条记录。")
            return df
        logging.warning("查询成功，但未返回任何数据。")
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"查询 App Insights 日志失败: {e}")
        return pd.DataFrame()

def main():
    credential = AzureCliCredential()
    subscription_id = get_subscription_id()
    
    web_client = WebSiteManagementClient(credential, subscription_id)
    
    app_details = get_function_app_details(web_client, RESOURCE_GROUP_NAME, FUNCTION_APP_NAME)
    app_insights_key = [s for s in app_details.app_settings if s.name == "APPINSIGHTS_INSTRUMENTATIONKEY"][0].value
    app_insights_client = ApplicationInsightsDataClient(credential)

    all_results = []

    for scenario, batch_size in TEST_SCENARIOS.items():
        logging.info(f"\n{'='*20} 开始测试场景: {scenario.upper()} (BATCH_SIZE={batch_size}) {'='*20}")
        try:
            update_batch_size(web_client, RESOURCE_GROUP_NAME, FUNCTION_APP_NAME, batch_size)
            trigger_data_generation(web_client, RESOURCE_GROUP_NAME, FUNCTION_APP_NAME)
            logging.info(f"等待 {WAIT_TIME_SECONDS} 秒让函数执行和数据处理...")
            time.sleep(WAIT_TIME_SECONDS)
            
            # 查询最近的执行结果
            results_df = query_execution_logs(app_insights_client, app_insights_key, QUERY_TIME_RANGE_MINUTES)
            if not results_df.empty:
                results_df['scenario'] = scenario
                results_df['batch_size'] = batch_size
                all_results.append(results_df)
            else:
                logging.warning(f"场景 '{scenario}' 未找到任何执行日志。")

        except Exception as e:
            logging.error(f"场景 '{scenario}' 执行失败: {e}")
            continue

    if all_results:
        final_df = pd.concat(all_results, ignore_index=True)
        output_path = "performance_results.csv"
        final_df.to_csv(output_path, index=False)
        logging.info(f"\n{'='*20} 所有测试完成! 结果已保存到 {output_path} {'='*20}")
        print(final_df)
    else:
        logging.warning("所有测试场景均未收集到任何数据。")

if __name__ == "__main__":
    main()
