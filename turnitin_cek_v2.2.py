import tkinter as tk
from tkinter import filedialog, messagebox
import mysql.connector
import pandas as pd
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Connect to MySQL Database
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Ranggam04@",  # Replace with your MySQL root password
            database="turnitin_cek",   # Replace with your database name
            auth_plugin='mysql_native_password'
        )
        if connection.is_connected():
            print("Connected to MySQL database.")
            return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
    return None

# Function to preprocess the text
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    # Replace repeated characters with a single character
    text = re.sub(r'(.)\1+', r'\1', text)
    # Remove non-alphanumeric characters (except spaces and hyphens)
    text = re.sub(r'[^\w\s\-]', '', text)
    return text.strip()

# Preprocessing function for all articles
def preprocess_articles(articles):
    return [preprocess_text(article) for article in articles]

# Step 5: Compute Similarity Matrix
def compute_turnitin(Articles):
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), norm='l2', sublinear_tf=True, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(Articles)
    similarity_matrix = cosine_similarity(tfidf_matrix)
    return similarity_matrix

# Step 6: Assign Similarity Category Based on Percentiles
def categorize_similarity(turnitin_score, all_scores):
    # Compute percentiles to categorize
    high_threshold = np.percentile(all_scores, 90)  # 90th percentile
    fair_threshold = np.percentile(all_scores, 60)  # 60th percentile
    low_threshold = np.percentile(all_scores, 20)  # 20th percentile

    if turnitin_score >= high_threshold:
        return 'High'
    elif turnitin_score >= fair_threshold:
        return 'Fair'
    elif turnitin_score >= low_threshold:
        return 'Low'
    else:
        return 'Recommended'

# Step 7: Update Similarity Rates in the Database
def update_turnitin_scores(connection, similarity_matrix, ids):
    update_data = []
    cursor = connection.cursor()

    # Iterate through the similarity matrix and compute average similarity score
    for i, row in enumerate(similarity_matrix):
        # Calculate the average similarity score for the current title
        turnitin_score = float(sum(row) / len(row))  # Average score for this title
        turnitin_result = categorize_similarity(turnitin_score, [float(sum(row) / len(row)) for row in similarity_matrix])  # Categorize the similarity score

        # Debug print to check if the values are calculated correctly
        print(f"Updating Title ID {ids[i]}: Score = {turnitin_score}, Result = {turnitin_result}")
        
        # Ensure that turnitin_score is a float and turnitin_result is a string
        update_data.append((turnitin_score, turnitin_result, ids[i]))

    # Prepare update query
    for data in update_data:
        try:
            query = """UPDATE Articles 
                    SET turnitin_score = %s, turnitin_result = %s
                    WHERE id = %s"""
            cursor.execute(query, data)
            print(f"Updated Title ID {data[2]}: Score = {data[0]}, Result = {data[1]}")
        except mysql.connector.Error as err:
            print(f"Error updating Title ID {data[2]}: {err}")

    connection.commit()

# 3. Read Excel File and Insert Titles into Database
def read_excel_and_insert(file_path):
    try:
        # Read the Excel file
        data = pd.read_excel(file_path, sheet_name="Report")  # Adjust sheet name if needed
        print("Excel file read successfully.")
        print("Preview of the data being read:")
        print(data.head())

        connection = connect_to_db()
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            # Read titles from Excel and insert them into the database
            for index, row in data.iterrows():
                title = row["title"]  # Ensure the column name matches your Excel file
                try:
                    print(f"Inserting title: {title}")
                    cursor.execute(
                        "INSERT INTO Articles (title) VALUES (%s)",
                        (title,)
                    )
                    print(f"Successfully inserted title: {title}")
                except mysql.connector.Error as err:
                    print(f"Error inserting title '{title}': {err}")

            # Commit the inserted titles
            connection.commit()

            # Fetch all titles from the database and process similarity
            cursor.execute("SELECT id, title FROM Articles")
            titles = cursor.fetchall()
            if not titles:
                print("No titles found in the database after insertion.")
                return

            # Step 5: Compute Similarity Matrix
            title_list = [title['title'] for title in titles]
            preprocessed_titles = preprocess_articles(title_list)
            similarity_matrix = compute_turnitin(preprocessed_titles)

            # Update the database with similarity scores
            ids = [title['id'] for title in titles]
            update_turnitin_scores(connection, similarity_matrix, ids)

            # Commit the changes to the database
            connection.commit()

            # Close the connection
            cursor.close()
            connection.close()
        else:
            print("Failed to connect to the database.")
    except Exception as e:
        print(f"Error reading Excel file: {e}")

# Function to open a file dialog and select an Excel file
def open_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
    )
    if file_path:
        read_excel_and_insert(file_path)

# Create the Tkinter window
root = tk.Tk()
root.title("Turnitin Checker")

# Create buttons for each task
insert_button = tk.Button(root, text="Insert Titles from Excel", command=open_file)
insert_button.pack(pady=10)

root.mainloop()
