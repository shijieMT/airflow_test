from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.ssh.operators.ssh import SSHOperator


def my_task_function(**kwargs):
    """
    简单的示例任务函数
    kwargs: 包含上下文变量的字典，如执行日期(ds)等
    """
    print("Hello, Airflow! This is a simple task.")
    print(f"Execution date: {kwargs['ds']}")  # ds 是执行日期的简写，格式为 YYYY-MM-DD

# DAG 的默认参数配置
default_args = {
    'owner': 'airflow',                     # DAG 的所有者/维护者
    'depends_on_past': False,               # 是否依赖上一次运行的状态，False 表示不依赖
    'email_on_failure': False,              # 任务失败时是否发送邮件通知
    'email_on_retry': False,                # 任务重试时是否发送邮件通知
    'retries': 1,                           # 任务失败后的最大重试次数
    'retry_delay': timedelta(minutes=5),    # 重试之间的时间间隔
}

# 定义 DAG
with DAG(
    'example_dag',                          # DAG 的唯一标识符
    default_args=default_args,              # 引用上面定义的默认参数
    description='A simple example DAG',     # DAG 的描述信息
    schedule_interval=timedelta(days=1),    # 调度间隔，这里设置为每天执行一次
    start_date=datetime(2023, 1, 1),        # DAG 的开始日期
    catchup=False,                          # 是否追赶历史任务，False 表示不执行过去的任务
    tags=['example'],                       # DAG 的标签，用于在 UI 中分类和筛选
) as dag:

    # 定义第一个 Python 任务
    task_1 = PythonOperator(
        task_id='print_hello_1',            # 任务的唯一标识符
        python_callable=my_task_function,    # 指定要执行的 Python 函数
        provide_context=True,                # 是否向函数传递上下文变量（如执行日期等）
    )

    # 定义第二个 Python 任务
    task_2 = PythonOperator(
        task_id='print_hello_2',            # 任务的唯一标识符
        python_callable=my_task_function,    # 指定要执行的 Python 函数
        provide_context=True,                # 是否向函数传递上下文变量
    )

    # 定义任务依赖关系：task_1 执行完后再执行 task_2
    task_1 >> task_2

    # 定义 SSH 远程执行任务
    execute_remote_script = SSHOperator(
        task_id='execute_remote_script',     # SSH 任务的唯一标识符
        ssh_conn_id='ssh-server',           # Airflow 中配置的 SSH 连接 ID
        command='{{ "bash /script/date_print.sh" }}',  # 使用 Jinja 模板语法包装要执行的命令
        conn_timeout=10,                     # SSH 连接超时时间，单位为秒
        cmd_timeout=10,                      # 命令执行超时时间，单位为秒
        get_pty=True,                       # 是否分配伪终端（pseudo-terminal）
                                           # True 可以更好地处理交互式命令和颜色输出
    )

    task_2 >> execute_remote_script       # task_2 完成后执行 SSH 任务