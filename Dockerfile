# Step 1: Use an official Python runtime as the base image
FROM python:3.9-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Step 4: Install dependencies from requirements.txt
RUN pip install -r /app/requirements.txt

# Step 5: Copy the rest of your application code into the container
COPY dbApplication/ /app/

# Step 6: Set environment variables for Flask
ENV FLASK_APP=dbApplication/run.py
ENV FLASK_ENV=production

# Step 7: Expose the port Flask will run on (default is 5000)
EXPOSE 5000

# Step 8: Run the application
CMD ["python", "dbApplication/run.py"]
