# Judica - AI Judge
<p align="center">
    <img src="https://github.com/Adhivp/Judica/blob/master/Judica/static/images/logo.png" width=300 />
</p>
<p align="center">
    <p align="center">
        <a href="https://github.com/Adhivp/Judica" target="blank">
            <img src="https://img.shields.io/github/watchers/Adhivp/Judica?style=for-the-badge&logo=appveyor" alt="Watchers"/>
        </a>
        <a href="https://github.com/Adhivp/Judica/fork" target="blank">
            <img src="https://img.shields.io/github/forks/Adhivp/Judica?style=for-the-badge&logo=appveyor" alt="Forks"/>
        </a>
        <a href="https://github.com/Adhivp/Judica/stargazers" target="blank">
            <img src="https://img.shields.io/github/stars/Adhivp/Judica?style=for-the-badge&logo=appveyor" alt="Star"/>
        </a>
    </p>
    <p align="center">
        <a href="https://github.com/Adhivp/Judica/issues" target="blank">
            <img src="https://img.shields.io/github/issues/Adhivp/Judica?style=for-the-badge&logo=appveyor" alt="Issue"/>
        </a>
        <a href="https://github.com/Adhivp/Judica/pulls" target="blank">
            <img src="https://img.shields.io/github/issues-pr/Adhivp/Judica?style=for-the-badge&logo=appveyor" alt="Open Pull Request"/>
        </a>
    </p>
    <p align="center">
        <a href="https://github.com/Adhivp/Judica/blob/master/LICENSE" target="blank">
            <img src="https://img.shields.io/github/license/Adhivp/Judica?style=for-the-badge&logo=appveyor" alt="License" />
        </a>
    </p>
</p>

## Overview

Judica is an innovative platform that leverages advanced AI technology to deliver impartial and accurate judgments swiftly and efficiently. Designed to revolutionize the justice system, Judica provides a user-friendly interface, ensuring privacy and security for all users.

## Demo video
https://youtu.be/pJHGqlmsidE

## Features

- **AI-Powered Judgments**: Our cutting-edge AI system provides impartial and accurate judgments, revolutionizing the way justice is delivered.
- **User Disputes Resolved**: Easily file and manage disputes. Judica mediates and provides fair resolutions using advanced AI technology.
- **Secure and Private**: All data is encrypted to ensure privacy and security.
- **User-Friendly Interface**: A chat-like interface allows for smooth and intuitive navigation.

`AI_courtroom/views.py` file. This code handles the logic for AI-powered judgments(LLMWARE) and dispute resolutions.


## Getting Started

To get started with Judica, follow these steps:

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/Adhivp/Judica.git
    cd Judica
    ```

2. **Install Dependencies**:
    Ensure you have Python and pip installed, then run:
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Server**:
    Start the Django development server:
    ```bash
    python manage.py runserver
    ```
4. **makemigrations and migrate**:
    ```bash
    python manage.py makmigrations
    ```
    ```bash
    python manage.py migrate
    ```
5. **Access the Application**:
    Open your browser and navigate to \`http://localhost:8000\` to view the Judica homepage.

6. **Unexpected errors**
 - remove the -1(inside views.py in AI_courtroom 86 th line inside verdict_view funciton), if you're getting different case, verdict/object or page not found error in verdict_view funciton

    

## Usage

- **Login**: Users can log in via the login page.
- **Register**: New users can register through the registration page.
- **Dashboard**: Dashboard can be accesed after login
- **Courtroom**: You can enter a courtroom if a case is filed against/by you


## Contributing

We welcome contributions to enhance Judica. Please follow these steps:

1. Fork the repository.
2. Create a new branch:
    ```bash
    git checkout -b feature/your-feature-name
    ```
3. Commit your changes:
    ```bash
    git commit -m "Add new feature"
    ```
4. Push to the branch:
    ```bash
    git push origin feature/your-feature-name
    ```
5. Open a pull request.

## Screenshots

<img src="https://github.com/Adhivp/Judica/assets/92261845/054b4507-a944-4625-b854-53ea5df2089d" alt="Screenshot 2024-05-21 at 9 43 15 PM" width="770">
<img src="https://github.com/Adhivp/Judica/assets/92261845/7ec6fe3d-e031-4568-a9ab-0beee1e7fe19" alt="Image 1">
<img src="https://github.com/Adhivp/Judica/assets/92261845/a5315474-feb3-46ce-babb-3e60293dfd92" alt="Image 2">
<img src="https://github.com/Adhivp/Judica/assets/92261845/9773a4d4-2a13-4452-b6a8-66030b024f53" alt="Image 3">






## License

Judica is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

- The design and layout are inspired by modern web standards, providing a responsive and engaging user experience.
- Special thanks to all contributors and the open-source community for their continuous support.
