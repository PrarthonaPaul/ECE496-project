ECE496 Capstone Project
Task Management AI tool

The primary objective of this capstone project is to substantially enhance the task distribution process within a team structure. This enhancement is designed with the specific intention of promoting not just the prompt delivery of project components, but also significantly mitigating stress levels within the team while ensuring the achievement of critical project milestones.

In order to effectively implement this process, a key strategy we propose is the division of a large project deliverable into more manageable and smaller parts. This approach is not only more efficient but also allows for a more streamlined integration of tasks into the daily work routine of each team member.

The overarching goal here is to amplify group efficiency by ensuring that each team member's work schedule is optimized. This optimization will not only guarantee the completion of individual tasks but will also ensure that the entire team is making consistent progress towards the project's overarching objectives.

Moreover, this system of efficient task distribution and careful integration into the team's daily routine will create a mechanism that keeps the entire group on track. This not only fosters a sense of shared responsibility and commitment but also ensures the successful and timely completion of the project.

---
## How to run the project

To run the backend of the project locally, follow the following instructions: 

1. Start the virtual environment for python:
```
source .venv/bin/activate
```

2. Use pip to install all the packages needed for the project: 
```
python -m pip install --upgrade pip
pip install -r /path/to/requirements.txt
```

3. (Optional) Apply the migrations needed for the project:
```
python manage.py makemigrations projectPath
python manage.py migrate
```

4. Run the backend project: 
```
python manage.py runserver
```
You can now access the backend by sending requests to http://localhost:8080

---

## Key Objectives for the Project:

For this project, we aim to accomplish several significant objectives to enhance task management and distribution within team structures:

1. **Information Extraction from PDF Documents:** One of our primary objectives is to extract crucial information such as project deliverables, the weightage of assignments, the description of tasks, and the scoring criteria from PDF documents. This will help in better understanding the tasks, their importance, and the criteria for successful completion.
2. **Task Classification and Timeline Assignment:** We aim to classify tasks and allocate suitable timelines for each one. This will be accomplished by using a combination of the task description, the potential steps involved in reaching the milestone, and the marks associated with the task. By doing so, we will be able to establish a clear roadmap for each task, thereby facilitating smoother execution.
3. **Sub-task Suggestion Feature Development:** We plan to develop a sub-task suggestion feature. In this, the larger deliverables will be further divided into smaller, more manageable tasks based on the task description. This will allow us to keep track of each task in accordance with its timeline and urgency, thus ensuring that no task or subtask is overlooked or delayed.
4. **Integration with Team Members' Calendars:** Finally, we intend to integrate our system with the calendars of individual team members. This will enable automatic allocation of tasks or sub-tasks to team members based on their indicated availability. This feature will ensure that each task is being actively worked on, and helps to maintain the momentum of the project.

By achieving these objectives, we aim to enhance the efficiency of task distribution, promote a sense of shared responsibility, and ensure the successful and timely completion of the project.

---

## Technologies to be used in this project:

As shown above, our project consists of four main tasks. Each is crucial for delivering a comprehensive end product that can achieve meaningful goals. Therefore, the technology for each task must be thoroughly researched, scientifically backed, and data-driven. Here is a list of the proposed technologies for our project:

- **Information extraction from PDFs**: (Laura)
    
    This task consists of two components: converting the PDF into a format that can be parsed and extracting the necessary information from the converted format. Let's discuss a few methods for accomplishing both, as we'll need to justify our choice of method for each task.
    
    - **Converting PDF into Parsable format:**
        
        Generally, PDFs are the most common format for sharing files and documents online. However, they are notably difficult to extract and parse data from automatically. Given our goal to extract as much contextual information as possible from the PDF, we must approach this task efficiently and swiftly.
        
    - **Applying NLP to converted PDF to extract information:**
        
        Now that we have a file which is parsable, we would want to apply some form of natural language processing to extract the information that we need from it. Here, we would want to compare different available methods for doing this, weighing their pros and cons and choosing the one that we feel most suits our use case.
        
- **Task Classification of extracted data:(Prarthona)**
    
    This task involves the classification of all the milestones and deliverables listed out in the provided syllabus into brackets that we have decided; such as presentations, software frontend, software backend, and other such decided categories. We then project a timeline for each task classification, dependent on the task description and category.
    
    - **Main Task Classification:**
        
        This would involve classifying the main deliverables into pre-determined brackets that we want to support. The current plan for this is to train a pre-existing transformer such as Llama 2 to do this for us. We want to train it with a high-quality dataset of at least 1000 PDFs.
        
    - **Task Duration Deduction:**
        
        We would like to adjust the task duration for the tasks that we classify. This task duration should be decided based on multiple criteria such as task description, task category that we have assigned and the mark weightage. On the basis of this calculated task duration, we create a layout a timeline for the project, in a form similar to a gantt chart. This task would need some form of regression to calculate the task duration, some form of dataset training which we can get some existing engines to generate, and a UI to display all this information.
        
    - **Reinforcement Learning:**
        
        We want to give the user to correct our predicted tasks and durations. When they adjust this on the basis of what is reflected, we should use these corrections to better our predictions. Hence, we should also build in some form of reinforcement learning into our tool to do this.
        
- **Task Assignment and allocation:(Anipreet)**
    
    This task involves gathering when individuals of the team would be free, and assigning them existing tasks on the basis of how much time they have. This would involve having a greedy algorithm or a dynamic programming algorithm which would maximize the hours available for work to get the tasks running. This would need a front-end  similar to when2meet to collect weekly available hours for each teammate, and the algorithm to do the task allocation.
    
- **Sub-task generation:(Anushka)**
    
    Here are some ideas we can use to do this particular task:
    
    1. **Natural Language Processing (NLP):**
        - Utilize NLP techniques to analyze task descriptions and identify key phrases, action verbs, and nouns that indicate sub-tasks.
        - Techniques like sentence segmentation, tokenization, and part-of-speech tagging can help break down task descriptions into meaningful units
        - Named Entity Recognition (NER) can identify entities mentioned in the task descriptions, which can serve as potential sub-tasks.
    2. **Text Summarization:**
        - Apply text summarization techniques to condense lengthy task descriptions into shorter, more concise summaries.
        - Extractive summarization methods, such as TF-IDF or TextRank, can identify important sentences or phrases in the task description to serve as sub-tasks.
    3. **Topic Modeling:**
        - Utilize topic modelling algorithms like Latent Dirichlet Allocation (LDA) or Non-Negative Matrix Factorization (NMF) to identify themes or topics within task descriptions.
        - Sub-tasks can be generated based on the identified topics, with each topic representing a cluster of related tasks.
    4. **Sequence-to-Sequence Models:**
        - Train sequence-to-sequence models, such as Recurrent Neural Networks (RNNs) or Transformer models, to generate sub-tasks from task descriptions.
        - The model can be trained on pairs of task descriptions and corresponding sub-tasks, learning to map input descriptions to output sub-tasks.
    5. **Hierarchical Clustering:**
        - Apply hierarchical clustering algorithms to group similar task descriptions together based on their semantic similarity.
        - Sub-tasks can be generated by splitting each cluster into smaller clusters, with each cluster representing a set of related sub-tasks.
    6. **Rule-based Systems:**
        - Develop rule-based systems that use predefined patterns or heuristics to identify common structures in task descriptions and generate sub-tasks accordingly.
        - Rules can be based on linguistic patterns, syntactic structures, or domain-specific knowledge.
    7. **Feedback-based Learning:**
        - Implement feedback mechanisms where users can provide input on suggested sub-tasks, allowing the system to learn and improve over time based on user feedback.
        - Techniques like reinforcement learning can be used to optimize the sub-task suggestion process based on user preferences and task outcomes.
