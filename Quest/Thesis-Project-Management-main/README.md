# Thesis Project Management

## Overview

This project is aimed at transforming the thesis project management system at **Pulchowk Campus** by developing a dynamic web application using Django. The new system will replace the current, inefficient mix of email, Excel, and Word documents with a streamlined, interactive platform that enhances collaboration and efficiency for students, supervisors, and the Unit Coordinator.

## Table of Contents

- [Current System](#current-system)
- [Pain Points](#pain-points)
- [Key Functionalities](#key-functionalities)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Current System

The current thesis project management process involves:

- Emailing and updating spreadsheets for thesis topics.
- Manual email exchanges for topic selection and supervisor approvals.
- Submitting signed supervision agreements via Learnline.

## Pain Points

The current system has several key pain points:

1. **Inefficient Workflow**: Manual processes are repetitive and error-prone.
2. **Supervisor Capacity Blind Spot**: Students often face disappointments due to hidden limitations in supervisor capacity.
3. **Form Errors and Delays**: Frequent errors in standard forms require time-consuming corrections.
4. **Manual Data Management**: Redundant updates and double data entry create unnecessary complexity.

## Key Functionalities

1. **Enhanced Efficiency**: Centralized workflows and automation reduce manual tasks and errors.
2. **Improved Communication**: A shared platform fosters transparent communication among all stakeholders.
3. **Accessibility**: The web-based application can be accessed from anywhere, anytime, on various devices.
4. **Data Integrity**: Secure data storage and access controls protect student and project information.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/SusheelThapa/thesis.git
   ```

2. Navigate to `thesis`

   ```bash
   cd thesis
   ```

3. Create virtual environment and activate it.

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

4. Install the required dependencies:

   ```bash
   pip install -r requirements.tx
   ```

5. Apply migrations to set up the database

   ```bash
   python manage.py migrate
   ```

6. Start the Django development server"
   ```bash
   python manage.py runserver
   ```

## Usage

1. Access the website at `http://127.0.0.1:8000/login` to view available thesis topics.
2. For interactive functionalities, log in with your supervisor, student, or Unit Coordinator credentials.
3. Supervisors can manage thesis topics, students can apply for projects, and the Unit Coordinator can oversee the entire process.

## Demo

[Thesis Management System Demo](https://github.com/SusheelThapa/Thesis-Project-Management/assets/83917129/0d3a7cd8-5415-423e-885c-b8cf55b44a88)

The sequence of actions in the demo video is as follows:

1. Creation of Student user, Supervisor user and Coordinator user accounts from admin site.
2. Supervisor can add and view their projects.
3. Unit Coordinator can view all projects and can accept or reject them.
4. Status of project is updated in Supervisor's page according to the actions of Coordinator.
5. Student can create or join groups.
6. After joining a group they can apply to projects.
6. Supervisor can view all the applications to their project and can accept or reject those applications.
7. Supervisor can analyze the sentiment of the application and ask questions related to the application.
8. Students cannot apply to already accepted projects, or to the projects they were rejected from.


## Dependencies

- [Django==5.0.6](https://pypi.org/project/Django/5.0.6/)
- [llmware==0.2.14](https://pypi.org/project/llmware/0.2.14/)

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for review.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.