# Territorio silvestre
This web application that unifies and enhances the value of information on the threatened biodiversity of Spain. Through the compilation of data from different sources (see Annex), the application offers an integrated view on the species of birds and mammals in endangered in our country, the protected natural areas of Andalusia and recent observations of fauna in the province of Seville

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

![Captura de pantalla 2025-05-20 134459](https://github.com/user-attachments/assets/6c31d36b-eaee-4a6e-86d5-ecd0584cc8c8)
*Search engine for birds and mammals catalogued as endangered in Spain and their conservation status*
![Captura de pantalla 2025-05-20 131503](https://github.com/user-attachments/assets/07fbe431-656d-44f6-be9d-c2c103ff9dcc)
![Captura de pantalla 2025-05-20 132748](https://github.com/user-attachments/assets/78ad84f7-8077-4372-92e5-54ba9c3ca793)
![Captura de pantalla 2025-05-20 132846](https://github.com/user-attachments/assets/61a5f8fb-4f47-488f-b00b-6374a89c889b)<br><br>
*Allows us to make queries of animals that have been cataloged as threats in Spain. We can filter by common or scientific name and by their conservation status or, by clicking on the checkbox, we can enter keywords in the text field that will be searched in the different descriptions of the animals. In addition, you can list the entire database, which will allow the user to know which are all the animals that are present in our project*

![Captura de pantalla 2025-05-20 134539](https://github.com/user-attachments/assets/d3313576-26bb-4404-b3be-1095a78bb2f9)
*Search engine for areas catalogued as ZEC/ZEPA by the Junta de Andalucía (Regional Government of Andalusia)*
![Captura de pantalla 2025-05-20 132028](https://github.com/user-attachments/assets/0136186e-e6b0-4644-8170-f5e7501d2140)
![Captura de pantalla 2025-05-20 150802](https://github.com/user-attachments/assets/0bfad6da-c9fe-459e-863e-ee39b69638fb)
![Captura de pantalla 2025-05-20 150830](https://github.com/user-attachments/assets/bf0648b4-a0e5-407e-a6cf-aa9d31e1a7be)
![Captura de pantalla 2025-05-20 150932](https://github.com/user-attachments/assets/68e8b38d-da49-454c-9b56-eadf0f7e6fee)<br><br>
*Thanks to this functionality the user will be able to know and make searches related to areas protected by the Junta de Andalucía. The user will be able to list the entire database, as well as search by name of the area and a range of surface in hectares. The user will also be able to activate the sorting by surface and the fuzzy search*

![Captura de pantalla 2025-05-20 134601](https://github.com/user-attachments/assets/fab75565-1337-4cf5-97c3-c9845bd74f32)
*Search engine for bird and mammal sightings in the province of Seville*
![Captura de pantalla 2025-05-20 150501](https://github.com/user-attachments/assets/629fc763-f82b-463e-8153-7d6d77119c72)
![Captura de pantalla 2025-05-20 141150](https://github.com/user-attachments/assets/ace316b4-5428-44ac-b709-a6b9bc1331bd)
![Captura de pantalla 2025-05-20 150516](https://github.com/user-attachments/assets/e43f2545-89e8-446f-a0c0-f2fdd7ae2da3)
![Captura de pantalla 2025-05-20 150625](https://github.com/user-attachments/assets/3ac64a5c-358e-407b-b89c-038b4ac26236)<br><br>
*It is used to make searches related to species of birds and mammals that have been seen and previously registered in the web to which we do the scraping in the province of Seville. We can consult the species by listing them all or if we are looking for a specific animal, we can search by common or scientific name, and we can also search by date, which will show us all the animals that have been observed in the specified range. These actions can also be performed at the same time, since they are not restrictive and allow the user to narrow down his search. Not only that, we have a top observations that will allow the user to know which have been the 10 most viewed species of all*

### Websites used for scraping and websites of interest for the project:
https://es.wikipedia.org/wiki/Anexo:Especies_en_peligro_de_extinci%C3%B3n_en_Espa%C3%B1a <br><br>
https://www.juntadeandalucia.es/medioambiente/portal/areas-tematicas/espacios-protegidos/espacios-protegidos-red-natura-2000/relacion-espacios-protegidos-red-natura-2000-zec-zepa <br><br>
https://observation.org/ <br><br>
https://www.iucnredlist.org/es <br><br>
