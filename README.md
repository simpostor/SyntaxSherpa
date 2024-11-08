# SyntaxSherpa

Welcome to **SyntaxSherpa**, your trusted companion for navigating the coding mountains! Whether you're trekking through complex algorithms or traversing the valleys of syntax errors, SyntaxSherpa is here to guide you every step of the way. With intuitive suggestions and expert knowledge, SyntaxSherpa helps you reach new heights in your coding journey. Say goodbye to getting lost in the code and hello to smooth sailing with SyntaxSherpa by your side.

---

## Description

SyntaxSherpa is an interactive coding assistant designed to assist developers with real-time syntax suggestions, best practices, and in-depth explanations of code. Using advanced natural language processing and language models, it can understand your code context, troubleshoot issues, and suggest improvements without needing external APIs. SyntaxSherpa is fully local, ensuring privacy and security for your coding projects.

---

## System Requirements

To run SyntaxSherpa, ensure your system meets the following requirements:

- **RAM:** Minimum of 8GB, though 16GB or more is recommended for large projects or complex tasks.
- **GPU:** A dedicated GPU is recommended for processing-intensive tasks and handling large codebases.
- **Python Version:** Python 3.11 (managed via conda).

---

## Steps to Run

Follow these steps to set up and run SyntaxSherpa:

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/simpostor/SyntaxSherpa.git
    cd SyntaxSherpa
    ```

2. **Set Up Environment Variables:**

    Rename `example.env` to `.env` and input any necessary environment variables:

    ```bash
    cp example.env .env
    ```

3. **Create and Activate Conda Environment:**

    ```bash
    conda create -n syntaxsherpa python=3.11
    conda activate syntaxsherpa
    ```

4. **Install Dependencies:**

    Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

5. **Run SyntaxSherpa:**

    Start the application with the following command:

    ```bash
    chainlit run app.py
    ```

---

## Authentication Setup (Optional)

If you wish to secure the application with user authentication, follow these steps:

1. **Generate a Secret Token:**

    ```bash
    chainlit create-secret
    ```

2. **Add Authentication Token:**

    Copy the generated token and paste it into the `.env` file.

3. **Add User Credentials:**

    Update `users.csv` with the authorized user details.

---

## Google Authentication Setup (Optional)

For Google OAuth setup:

1. **Create a Google Cloud Project**:
    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
  
2. **Set Up OAuth Credentials**:
    - Generate a client ID and client secret, then add them to your environment variables.

---

## GitHub Authentication Setup (Optional)

To set up GitHub OAuth, follow these steps:

1. **Create a GitHub OAuth App**:
    - Go to [GitHub Developer Settings](https://github.com/settings/developers).
    - Click on "New OAuth App" and fill out the required fields:
      - **Application Name**: SyntaxSherpa
      - **Homepage URL**: `http://localhost:8000` (or your app's URL)
      - **Authorization Callback URL**: `http://localhost:8000/callback` (or your app's callback URL)

2. **Save the Client ID and Client Secret**:
    - Copy the **Client ID** and **Client Secret** from GitHub and add them to your `.env` file as environment variables:
    
      ```plaintext
      GITHUB_CLIENT_ID=your_client_id
      GITHUB_CLIENT_SECRET=your_client_secret
      ```

3. **Update Application Code**:
    - Ensure your application references these environment variables for GitHub OAuth authentication.

---

## License

SyntaxSherpa is open-source and available under the [MIT License](LICENSE). 
