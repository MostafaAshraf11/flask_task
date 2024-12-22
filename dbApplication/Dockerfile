# Step 1: Use an official Python runtime as the base image
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
# Step 2: Set the working directory inside the container
WORKDIR /flask-app

# Step 3: Copy the requirements.txt file into the container
COPY requirements.txt /flask-app/

# Step 4: Install dependencies from requirements.txt
RUN pip install -r /flask-app/requirements.txt

# Step 5: Copy the rest of your application code into the container
COPY . .

# Set the working directory to where run.py is located


# Step 7: Expose the port Flask will run on (default is 5000)
EXPOSE 5000

# Step 8: Run the application
CMD ["python", "run.py"]
