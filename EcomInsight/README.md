![Demo design]([URL_to_image](https://1drv.ms/i/s!AlTBRgvLUJqxhN039vrbGTC6lYUpeQ?e=n7VEDS))

# Expense and Pricing Calculator WebApi

Welcome to the Expense and Pricing Calculator web application! This Django-based application is designed to assist you in managing your online product sales more effectively. It calculates expenses and recommends optimal pricing based on your desired profit margin. Additionally, you can store and modify records over time, making it a valuable tool for maintaining a profitable online business.

## Features

1. **Expense Calculation**: Easily calculate the expenses associated with your products. Input various costs such as manufacturing, shipping, and operational expenses to get a comprehensive view of your product costs.

2. **Recommended Pricing**: Set your desired profit margin, and the application will generate recommended prices for your products. This ensures your pricing aligns with your profit goals.

3. **Record Management**: Keep track of all your calculations and pricing decisions over time. Store and modify records to review and adjust your pricing strategies as needed.

## Getting Started

To run the Expense and Pricing Calculator application, follow these steps:

### Prerequisites

- Docker: Ensure you have Docker installed on your system.

### Installation and Setup

1. **Clone the repository**:

   ```
   git clone https://github.com/IamErol/EcomInsight.git
   ```

2. **Navigate to the project directory**:

   ```
   cd calculator-main
   ```

3. **Build the Docker image**:

   ```
   docker build -t calculator-main
   ```

4. **Run the Docker container**:

   ```
   docker run -p 8000:8000 calculator-main
   ```

5. **Access the application**:

   Open your web browser and go to [http://localhost:8000](http://localhost:8000) to access the application.

## Technologies Used

- **Django**: The web framework used to develop the application.
- **Django Rest Framework (DRF)**: A toolkit for building Web APIs.
- **Swagger**: A tool for generating interactive API documentation.
- **Nginx**: A web server used to serve the application and handle reverse proxy.

## Usage

1. **Expense Calculation**:
   - Navigate to http://127.0.0.1:8000/api/docs to see related documentation for api calls.
   - Input various expenses associated with your product.
   - The application will calculate the total expenses for the product and return Json response.

2. **Recommended Pricing**:
   - In the pricing section, input your desired profit margin.
   - The application will generate and display the recommended pricing for the product.

3. **Record Management**:
   - Store and modify records of calculations and pricing decisions over time.
   - Access these records to fine-tune your pricing strategies.

## Feedback and Support

For issues, questions, or feedback, please contact our team.

We hope you find the application valuable for your online business. Happy selling!

**Note**: New functionality will be added in upcoming releases.
