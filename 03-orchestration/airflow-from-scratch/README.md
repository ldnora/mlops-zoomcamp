# Airflow from scracth 




## Table of content 

- [Airflow from scracth](#airflow-from-scracth)
  - [Table of content](#table-of-content)
  - [Objective](#objective)
  - [How to learn about the Apache Airflow?](#how-to-learn-about-the-apache-airflow)
  - [Content explanation](#content-explanation)
    - [What is a DAG?](#what-is-a-dag)
    - [Some code](#some-code)
      - [DAG: operator to creat tasks (node -- vertex) and dependencies (edge)](#dag-operator-to-creat-tasks-node----vertex-and-dependencies-edge)
  - [References](#references)






## Objective

The objetive of this folder is learn about the Apache Airflow.




## How to learn about the Apache Airflow?

I'm using the official tutorial that explains how to build a first workflow.





## Content explanation




### What is a DAG?

A DAG is a roadmap for your wokflow. With it, you can explain to the machine what is the dependencies, tasks, code to run using a logic sequence.

The sigle DAG is: directed acyclic graph ("grafo dirigido sem ciclo", in portuguese). It means that you can link a vertex to anoter vertex, using edges, without a cycle.

![Image](https://upload.wikimedia.org/wikipedia/commons/0/08/Directed_acyclic_graph.png)

The vertex 7, 5 and 3 are the origin off the workflow. There aren't any edge from these vertex.

This image prepresent a finite workflow.



### Some code 

You can check the code [here](./src/tutorial.py)


```python

import textwrap
from datetime import datetime, timedelta

# Operators; we need this to operate!
from airflow.providers.standard.operators.bash import BashOperator

# The DAG object; we'll need this to instantiate a DAG
from airflow.sdk import DAG
with DAG(
    "tutorial",
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function, # or list of functions
        # 'on_success_callback': some_other_function, # or list of functions
        # 'on_retry_callback': another_function, # or list of functions
        # 'sla_miss_callback': yet_another_function, # or list of functions
        # 'on_skipped_callback': another_function, #or list of functions
        # 'trigger_rule': 'all_success'
    },
    description="A simple tutorial DAG",
    schedule=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:

    # t1, t2 and t3 are examples of tasks created by instantiating operators
    t1 = BashOperator(
        task_id="print_date",
        bash_command="date",
    )

    t2 = BashOperator(
        task_id="sleep",
        depends_on_past=False,
        bash_command="sleep 5",
        retries=3,
    )
    t1.doc_md = textwrap.dedent(
        """\
    #### Task Documentation
    You can document your task using the attributes `doc_md` (markdown),
    `doc` (plain text), `doc_rst`, `doc_json`, `doc_yaml` which gets
    rendered in the UI's Task Instance Details page.
    ![img](https://imgs.xkcd.com/comics/fixing_problems.png)
    **Image Credit:** Randall Munroe, [XKCD](https://xkcd.com/license.html)
    """
    )

    dag.doc_md = __doc__  # providing that you have a docstring at the beginning of the DAG; OR
    dag.doc_md = """
    This is a documentation placed anywhere
    """  # otherwise, type it like this
    templated_command = textwrap.dedent(
        """
    {% for i in range(5) %}
        echo "{{ ds }}"
        echo "{{ macros.ds_add(ds, 7)}}"
    {% endfor %}
    """
    )

    t3 = BashOperator(
        task_id="templated",
        depends_on_past=False,
        bash_command=templated_command,
    )

    t1 >> [t2, t3]

```

Let's go to explain the code.


#### DAG: operator to creat tasks (node -- vertex) and dependencies (edge)

"An operator represents a unit of work in Airflow".

For me, an operator is the way and rules to execute tasks. 

DAG (1) <-> (n) nodes (tasks)

This is a DAG:

````python
with DAG(
    "tutorial",
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function, # or list of functions
        # 'on_success_callback': some_other_function, # or list of functions
        # 'on_retry_callback': another_function, # or list of functions
        # 'sla_miss_callback': yet_another_function, # or list of functions
        # 'on_skipped_callback': another_function, #or list of functions
        # 'trigger_rule': 'all_success'
    },
    description="A simple tutorial DAG",
    schedule=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=["example"],
) as dag:
````

With the declaration of the DAG, you can create the tasks:

````python
    t1 = BashOperator(
        task_id="print_date",
        bash_command="date",
    )

    t2 = BashOperator(
        task_id="sleep",
        depends_on_past=False,
        bash_command="sleep 5",
        retries=3,
    )
````

Note that the task have a operator. The name before `Operator` defines the way the task (node -- edge) will be executed. In this case, it'll be exececuted at the bash (`BashOperator` -> `Bash`)


```python
    t1 >> [t2, t3]
```
Use the operator `>>` to set the dependencies (edges). It means: first execute the t1 and after the t2 and t3 in paralel














## References 

- [Official tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/fundamentals.html)
- 