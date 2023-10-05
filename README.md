# Run-Python-to-update-google-sheet

To set up this Python script in GitHub and run it every day, you can follow these steps:

1. **Create a GitHub Repository:**

   - Go to GitHub (https://github.com/) and log in to your account.
   - Click on the `+` sign in the top right corner and select "New repository."
   - Give your repository a name, choose visibility (public or private), and add a description if needed.
   - Click the "Create repository" button.

2. **Clone the Repository:**

   - On your local machine, open a terminal or command prompt.
   - Clone the GitHub repository to your local machine using the following command, replacing `<repository_url>` with your repository's URL:

     ```bash
     git clone <repository_url>
     ```

3. **Add Your Python Script:**

   - Move your Python script to the local repository directory.

4. **Create a Python Virtual Environment (Optional but recommended):**

   - Navigate to the repository directory in your terminal.
   - Create a virtual environment:

     ```bash
     python -m venv venv
     ```

   - Activate the virtual environment:

     - On Windows:

       ```bash
       venv\Scripts\activate
       ```

     - On macOS and Linux:

       ```bash
       source venv/bin/activate
       ```

5. **Install Dependencies:**

   - Install the required Python packages within your virtual environment:

     ```bash
     pip install gspread google-auth requests pandas
     ```

6. **Commit and Push to GitHub:**

   - Add your Python script and any other necessary files to the local repository.
   - Commit your changes:

     ```bash
     git add .
     git commit -m "Add Python script and dependencies"
     ```

   - Push your changes to the GitHub repository:

     ```bash
     git push origin master
     ```

7. **Create a GitHub Actions Workflow:**

   - In your GitHub repository, go to the "Actions" tab.
   - Click on "Set up a workflow yourself" to create a custom workflow.
   - Create a `.github/workflows` directory in your repository if it doesn't already exist.

   - Create a YAML workflow file (e.g., `daily_job.yml`) inside the `.github/workflows` directory. Here's an example of a basic workflow that runs your script daily:

     ```yaml
     name: Daily Job

     on:
       schedule:
         - cron: '0 0 * * *'  # Runs every day at midnight UTC

     jobs:
       build:
         runs-on: ubuntu-latest

         steps:
           - name: Checkout code
             uses: actions/checkout@v2

           - name: Set up Python
             uses: actions/setup-python@v2
             with:
               python-version: 3.x  # Replace with your Python version

           - name: Install dependencies
             run: |
               python -m pip install --upgrade pip
               python -m pip install gspread google-auth requests pandas

           - name: Run Python script
             run: |
               python your_script.py
     ```

     Replace `your_script.py` with the actual filename of your Python script.

8. **Commit and Push the Workflow:**

   - Commit the workflow file:

     ```bash
     git add .github/workflows/daily_job.yml
     git commit -m "Add daily job workflow"
     ```

   - Push the changes to GitHub:

     ```bash
     git push origin master
     ```

9. **GitHub Actions Setup Complete:**

   - GitHub Actions will now automatically run your Python script daily at midnight UTC.

10. **Monitor and Review:**

    - You can monitor the workflow's execution and review its logs in the "Actions" tab of your GitHub repository.

Make sure to replace `<repository_url>` with your actual repository's URL and adjust the Python version and schedule in the workflow YAML file as needed. Additionally, ensure that your service account JSON file (`expanse-simon-67cef9c9578b.json`) is securely stored in your GitHub repository if required for authentication.

No, you should not commit sensitive or confidential files, such as your service account JSON file (`expanse-simon-67cef9c9578b.json`), directly to your public GitHub repository. Committing such files to a public repository can pose a security risk because anyone with access to the repository can potentially view or misuse these credentials.

Instead, you should keep these sensitive files secure and use GitHub Secrets or other secure methods for managing and providing credentials to your GitHub Actions workflow.

Here's how you can handle sensitive files like your service account JSON file:

1. **Use GitHub Secrets:**

   GitHub provides a feature called "Secrets" that allows you to securely store sensitive information like API keys, credentials, or tokens. Follow these steps:

   - Go to your GitHub repository.
   - Click on "Settings" in the top menu.
   - In the left sidebar, click on "Secrets."
   - Click the "New repository secret" button.
   - Name your secret (e.g., `GOOGLE_SERVICE_ACCOUNT_KEY`) and paste the contents of your JSON file as the value.
   - Save the secret.

2. **Update Your GitHub Actions Workflow:**

   Modify your GitHub Actions workflow YAML file (e.g., `daily_job.yml`) to use the secret as an environment variable or configuration parameter. For example, if your script requires the service account key, you can pass it as an environment variable like this:

   ```yaml
   jobs:
     build:
       runs-on: ubuntu-latest

       steps:
         - name: Checkout code
           uses: actions/checkout@v2

         - name: Set up Python
           uses: actions/setup-python@v2
           with:
             python-version: 3.x

         - name: Install dependencies
           run: |
             python -m pip install --upgrade pip
             python -m pip install gspread google-auth requests pandas

         - name: Set up service account key
           run: |
             echo "$GOOGLE_SERVICE_ACCOUNT_KEY" > key.json

         - name: Run Python script
           env:
             GOOGLE_APPLICATION_CREDENTIALS: key.json
           run: |
             python your_script.py
   ```

   In this example, the secret is referenced as `"$GOOGLE_SERVICE_ACCOUNT_KEY"`, and it's saved to a temporary JSON file (`key.json`) that is then used as the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

By using GitHub Secrets and not committing sensitive files directly to your repository, you can keep your credentials secure while still allowing your GitHub Actions workflow to access them when needed.