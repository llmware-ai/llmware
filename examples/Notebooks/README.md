# Understanding Python notebooks

Welcome to our project documentation! A common point of confusion among developers new to data science and machine learning workflows is the relationship and differences between popular Python notebooks, including Google Colab and Jupyter Notebooks. This README aims to clarify these parts to ensure everyone is on the same page.

## What are Jupyter Notebooks?

Jupyter Notebooks is an open-source web application that lets you create and share documents that have live code, equations, visualizations, and narrative text. Uses include: data cleaning and transformation, numerical simulation, statistical modeling, data visualization, machine learning, and much more.

## What is Google Colab?

Google Colab (or Colaboratory) is a free Jupyter notebook environment that requires no setup and runs in the cloud. It offers a similar interface to Jupyter Notebooks and lets users write and execute Python in a web browser. Google Colab also provides free access to computing resources, including GPUs and TPUs, making it highly popular for machine learning and data analysis projects.

## What are marimo notebooks?

[marimo](https://github.com/marimo-team) is a new open-source Python notebook
that is an alternative to Jupyter notebooks. Unlike Jupyter notebooks, marimo
has interactive UI elements built-in, letting you transform dataframes and
otherwise explore data in a low-code environment. Unlike Jupyter, marimo
notebooks are reusable artifacts: they can be deployed as interactive web apps
and even executed as scripts.

You can learn more by playing with an [online interactive tutorial](https://marimo.app/?slug=c7h6pz).


## Key Similarities

- **Interface:** All three platforms use a similar user interface, which supports mixing executable code, equations, visualizations, and narrative text in a single document.
- **Language Support:** Primarily, all three notebooks are used for executing Python code. However, Jupyter Notebooks support other languages such as R and Julia.
- **Use Cases:** They are widely used for data analysis, machine learning, and education, allowing for easy sharing of results and methodologies. Additionally, marimo lets data scientists build and share interactive web apps, without requiring any familiarity with frontend development.

## Key Differences

- **Execution Environment:** Jupyter and marimo notebooks can be run locally on your machine or on a server, but Google Colab is hosted exclusively in the cloud.
- **Execution Style.** Jupyter notebooks and Google Colab have no understanding of the code in your notebook, and when you run
one cell you must manually run affected cells. marimo notebooks understand the relationship between code cells, similar to a spreadsheet, and can automatically update outputs when a cell is run. 
- **Access to Resources:** Google Colab provides free access to hardware accelerators (GPUs and TPUs) which is not inherently available in Jupyter and marimo unless specifically set up by the user on their servers.
- **Collaboration:** Google Colab offers easier collaboration features, similar to Google Docs, letting multiple users work on the same notebook simultaneously. marimo provides an [online playground](https://marimo.app) that runs entirely in your browser.

## Conclusion

While Google Colab and Jupyter Notebooks might seem different they are built on the same idea and offer similar functionalities with a few distinctions, mainly in execution environment and access to computing resources. Marimo notebooks feel similar to Jupyter
and Google Colab notebooks, but they can also be used as interactive web apps and reusable Python scripts.

Understanding these platforms' capabilities can significantly enhance your data science and machine learning projects.

We hope this guide has helped clarify the similarities and differences between Google Colab and Jupyter Notebooks. Happy coding!

