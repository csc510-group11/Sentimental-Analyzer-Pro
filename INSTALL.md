# Installation Guide for SentiLLyzer

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/csc510-group11/SentiLLyzer.git
    cd SentiLLyzer
    ```

2. **Set Up Environment Variables:**  
   Create a `.env` file in the root directory with the following content (replace placeholders with your actual API keys):

    ```env
    GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
    GEMINI_MODEL_NAME=gemini-2.0-flash
    DJANGO_ALLOWED_HOSTS=0.0.0.0,localhost,127.0.0.1
    DEFAULT_ADMIN_USERNAME=admin
    DEFAULT_ADMIN_PASSWORD=admin
    # Add other secrets as necessary...
    ```

3. **Run the makefile:**

    ```bash
    make up
    ```

4. **Access the Application:**  
   Open your browser and navigate to [http://localhost:8000](http://localhost:8000).
