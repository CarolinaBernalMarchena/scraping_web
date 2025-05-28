# Territorio silvestre
This web application that unifies and enhances the value of information on the threatened biodiversity of Spain. Through the compilation of data from different sources (see Annex), the application offers an integrated view on the species of birds and mammals in endangered in our country, the protected natural areas of Andalusia and recent observations of fauna in the province of Seville.

### Technologies:
- **Python**
- **BeautifulSoup**
- **Whoosh**
- **Django**

### How to start the project locally:
#### The user will need to have installed:
- **Python**
- **pip (Python package manager)**
#### Once the project is downloaded, the user through a console will have to enter the folder where the project has been downloaded using the command “cd” so that the user's path should look like this:
folder_where_the_project_is_hosted_locally/Project/django_project
#### Now we will install the dependencies using the command:
pip install -r requirements.txt
#### Finally, we will open the local web server with the command:
Python manage.py runserver
#### Once everything is ready, we will open a browser and access:
http://127.0.0.1:8000

### Some screenshots from the project:
![Captura de pantalla 2025-05-20 134214](https://github.com/user-attachments/assets/b071e168-bf0a-49be-8f15-c86d67ddc5f3)
![Captura de pantalla 2025-05-20 134420](https://github.com/user-attachments/assets/8b9a884d-3d91-44e9-b976-15e65715edaa)
*Home pages with and without the data loaded in the whoosh index*
