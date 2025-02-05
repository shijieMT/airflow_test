from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta


# 示例任务函数
def print_task_info(task_name):
    def inner_func(**context):
        print(f"执行任务: {task_name}")

    return inner_func


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 2, 1),
}

with DAG('task_group_example',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False,  # 设置为 False，禁用追赶
         ) as dag:
    # 开始任务
    start_task = PythonOperator(
        task_id='start_task',
        python_callable=print_task_info('开始任务')
    )

    # 定义数据处理任务组
    with TaskGroup(group_id='data_processing',
                   tooltip="数据处理任务组") as data_processing:
        # 数据清洗任务
        clean_data = PythonOperator(
            task_id='clean_data',
            python_callable=print_task_info('数据清洗')
        )

        # 数据转换任务组
        with TaskGroup(group_id='transform_tasks') as transform_tasks:
            transform_a = PythonOperator(
                task_id='transform_a',
                python_callable=print_task_info('转换A')
            )

            transform_b = PythonOperator(
                task_id='transform_b',
                python_callable=print_task_info('转换B')
            )

            # 定义转换任务的依赖关系
            transform_a >> transform_b

        # 数据验证任务
        validate_data = PythonOperator(
            task_id='validate_data',
            python_callable=print_task_info('数据验证')
        )

        # 定义任务组内的依赖关系
        clean_data >> transform_tasks >> validate_data

    # 定义报告任务组
    with TaskGroup(group_id='reporting',
                   tooltip="报告生成任务组") as reporting:
        generate_report = PythonOperator(
            task_id='generate_report',
            python_callable=print_task_info('生成报告')
        )

        send_report = PythonOperator(
            task_id='send_report',
            python_callable=print_task_info('发送报告')
        )

        # 定义报告任务组内的依赖关系
        generate_report >> send_report

    # 结束任务
    end_task = PythonOperator(
        task_id='end_task',
        python_callable=print_task_info('结束任务')
    )

    # 定义整体任务流程
    start_task >> data_processing >> reporting >> end_task

    # 定义第一个 Python 任务
    task_1 = PythonOperator(
        task_id='print_hello_1',            # 任务的唯一标识符
        python_callable=print_task_info("task_1"),    # 指定要执行的 Python 函数
        provide_context=True,                # 是否向函数传递上下文变量（如执行日期等）
    )

    # 定义第二个 Python 任务
    task_2 = PythonOperator(
        task_id='print_hello_2',            # 任务的唯一标识符
        python_callable=print_task_info("task_2"),    # 指定要执行的 Python 函数
        provide_context=True,                # 是否向函数传递上下文变量
    )
    task_1 >> task_2
