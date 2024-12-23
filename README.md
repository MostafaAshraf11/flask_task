# Flask Application

## Overview
This application is built using Flask to create a scalable and maintainable web application. It incorporates a range of libraries and tools to handle various functionalities such as database management, image processing, data analysis, and cloud integration.

---
## Time Allocation  

This project was developed over three days, starting Friday at 5 PM and concluding Monday. Below is a detailed breakdown of time spent on various activities, divided by tasks and days.  

### **Day 1: Friday**  
- **Research and Initial Setup**: 5-6 hours  
  - Researched Flask and its integration with SQLAlchemy for database management.  
  - Created the Flask application and generated the first database model, `loan_approval`.  
  - Developed and tested the CRUD API for the loan approval model.  
  - Successfully completed the first day with the initial CRUD functionality in place.  

---

### **Day 2: Saturday**  
- **Advanced API Development**: 5 hours  
  - Spent 3 hours creating additional features, including CSV file uploads, chart generation, and filters for data visualization.  
  - Dedicated 2 hours to testing these APIs, handling errors, and debugging issues encountered during development.  

- **Cloud Integration**: 2-3 hours  
  - Setting up Cloudinary for image management was straightforward and took only 30 minutes.  
  - Implemented CRUD operations for image management in about 2 hours.  
  - Advanced image manipulation APIs, such as segmentation masks, cropping, and resizing, required 4-5 hours to complete.  

The second day concluded with robust image management and advanced API features implemented.  

---

### **Day 3: Sunday**  
- **NLP Service Development**: 8 hours  
  - Attempted to use Gensim for text analysis but encountered issues with NLTK installation.  
  - Transitioned to SpaCy and TextBlob for implementation.  
  - Spent a significant amount of time (about 6 hours) researching NLP libraries and techniques due to limited prior experience.  
  - The actual implementation, leveraging SpaCy and TextBlob, was completed in 2 hours.  

The third day ended with a fully functional NLP service integrated into the application.  

---

### **Day 4: Monday**  
- **Movies Table Development**: 2-3 hours  
  - Created the `movies` table and its CRUD API.  
  - Repurposed functionality from the `loan_approval` module for tasks like filtering and categorization.  
  - The familiarity with the CRUD patterns from previous days expedited the process.  

---

**Total Time Spent**: ~31-32 hours  

### **Time Division Summary**
- **Research and Setup**: ~6 hours  
- **Development**: ~18 hours (CRUD, APIs, cloud integration, NLP, and movies table)  
- **Testing and Debugging**: ~4 hours  
- **Deployment and Finalization**: ~3 hours  


## Application Functionality

This Flask application provides several functionalities, organized into various modules:

### **Loan Approval Management**
- **CRUD Operations**: Users can create a new loan, update loan status, delete loans, and retrieve a loan or all loans.
- **Advanced Queries**: Perform filtering, generate statistics for specific columns, and generate graphs and charts to visualize data.

### **Movies Database Management**
- **CRUD Operations**: The user can perform all CRUD operations on the movies table.
- **Search Functionality**: Users can search for movies by title or director.
- **Categorization**: Movies can be filtered based on various criteria, such as genre, revenue, or release date.

### **Image Management with Cloudinary**
- **CRUD Operations**: Users can upload, retrieve, update, and delete images in Cloudinary.
- **Advanced Image Manipulation**: The app supports API features like cropping, format transformation, resizing, and generating segmentation masks for images.

### **Natural Language Processing (NLP) Service**
- **Text Analysis**: Users can input text and perform the following operations:
  - **Text Summary**: Automatically generate a summary of the input text.
  - **Keyword Extraction**: Extract relevant keywords from the input text.
  - **t-SNE Visualization**: Generate a t-SNE plot for text data to visualize similarities between documents.


## Methodology

### Development Methodology
The application follows the **MVC (Model-View-Controller)** design pattern. This approach promotes a clear separation of concerns:
- **Model**: Handles data and business logic.
- **View**: Manages the presentation layer (routes and responses).
- **Controller**: Acts as an intermediary between the Model and View, managing user input and data updates.

This structure ensures that the code is easier to maintain, test, and scale.

### Selection of Technologies, Libraries, and Frameworks
1. **Flask**: 
   - Used for creating the core web application.
   - Lightweight, easy to use, and suitable for small to medium-sized applications.

2. **SQLAlchemy**:
   - For database creation and management.
   - Used with SQLite for its lightweight nature, making it ideal for this project as no additional installation or external connections are required.

3. **Flask-Migrate**:
   - Simplifies database migration.

4. **Flask Blueprints**:
   - Enables modularization of routing.
   - Advantages: Enhances code organization, simplifies testing, and improves scalability by allowing routes to be grouped logically.

5. **Cloudinary**:
   - Modules used: `cloudinary.uploader.upload` and `cloudinary.uploader.destroy`.
   - Purpose: To save images on the cloud, ensuring scalability and avoiding local storage limitations.

6. **Werkzeug's secure_filename**:
   - Ensures secure handling of uploaded file names to prevent potential security risks.

7. **PIL (Python Imaging Library)**:
   - Module used: `PIL.Image`.
   - Purpose: Provides advanced image manipulation capabilities, such as resizing and cropping.

8. **SciPy**:
   - Module used: `scipy.stats`.
   - Purpose: Used for advanced statistical calculations, enhancing data analysis capabilities.
9. **Postman**:
   - Purpose: Used for API testing and documentation due to its user-friendly interface and comprehensive features.
   - Advantages: Allowed efficient testing of API routes, ensuring backend functionality was robust.
10. **Frontend Decision**:
    -Due to time constraints, development efforts were focused on the backend and testing processes.
    -This decision ensured the project met its deadlines without compromising core functionality
---

### Libraries Used

1. **Pandas**:
   - Purpose: For reading CSV files and data manipulation.
   - Advantages: Popular, well-documented, and efficient for handling structured data.

2. **Matplotlib.pyplot**:
   - Purpose: For creating dynamic and static data visualizations like bar charts and line graphs.
   - Advantages: Extensive documentation and support for customizations.

3. **OpenCV (cv2)**:
   - Purpose: For advanced image processing tasks such as color-based segmentation and histogram generation.
   - Advantages: Robust library for computer vision tasks with a large community and resources.

4. **NumPy**:
   - Purpose: For numerical operations and efficient handling of multi-dimensional arrays during image processing.
   - Advantages: Highly optimized for mathematical computations.

5. **BytesIO**:
   - Purpose: For managing in-memory byte streams, especially useful for handling image data without saving it to disk.
   - Advantages: Lightweight and seamlessly integrates with file-like operations.
6. **Scappy**:
   - For NLP functionality in this application, spaCy was chosen because:
        - It has a wealth of documentation available online, including articles and videos.
        - It is lightweight, making it suitable for this application.
        - It does not require installing additional dependencies like PyTorch, simplifying integration
    - Initially, I experimented with Gensim for NLP tasks, but encountered errors and difficulties when working with NLTK. These   challenges led to the decision to switch to spaCy, which provided a smoother development experience.
    - The model "en_core_web_sm" was used for processing natural language data in the application.
---

## Advantages of Selected Libraries and Frameworks
- **Flask and Flask Blueprints**: Modular and easy to scale.
- **SQLite with SQLAlchemy**: Lightweight and no need for additional setup.
- **Cloudinary**: Seamless image storage and scalability.
- **Pandas, Matplotlib, OpenCV, NumPy, PIL, and SciPy**: Reliable, efficient, and widely supported libraries for data manipulation, visualization, and image processing.
---
## Instructions for Running the Application

### Option 1: Using Virtual Environment (Windows)
1. Clone the repository.
2. Open a command prompt and navigate to the project directory.
3. Create a virtual environment:
   ```cmd
   python -m venv venv
   ```
4. Activate the virtual environment:
   ```cmd
   venv\Scripts\activate
   ```
5. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
6. Run the application:
   ```cmd
   python run.py
   ```

### Option 2: Using Docker
1. Create a `Dockerfile` in the project directory with the following content:
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY . /app

   RUN pip install --no-cache-dir -r requirements.txt

   CMD ["flask", "run", "--host=0.0.0.0"]
   ```
2. Build the Docker image:
   ```bash
   docker build -t flask-app .
   ```
3. Run the Docker container:
   ```bash
   docker run -p 5000:5000 flask-app
   ```

---



