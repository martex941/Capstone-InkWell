# **InkWell**
<sub>by Kamil Wiśniewski</sub>

## **What is InkWell?**
InkWell is a website for writers to write and collaborate on their projects. It features a rich text editor using [Django Quill by LeeHanYeong](https://github.com/LeeHanYeong/django-quill-editor). My idea behind it was a basic version of GitHub but for people who write books, short stories or anything similarily related. 


### **Important packages:**
- [django-quill-editor](https://pypi.org/project/django-quill-editor/)
- [Pillow](https://pypi.org/project/Pillow/)
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/)

# **Overview**

## **1. Writing**

### 1.1 Inks and Chapters
Ink is a name for any body of writing on the website, whether it be a short story, a long novel, a public diary or even an essay. Inks are not divided by pages like typical pieces of writing, they are divided only by chapters. 

### 1.2 Text Editor
InkWell utilizes [Django Quill](https://github.com/LeeHanYeong/django-quill-editor) to let writers edit chapters in their inks.
![Image of Django Quill editor while editing a chapter](/capstone/media/readme/)
The editor is configured to be slightly strict in its function variety in order to preserve an original feeling 

### 1.3 Editing Inks
Editing an ink allows the author to change its title, description, tags and contents of individual chapters.
![Image of ink editing screen](/capstone/media/readme/)

Authors can also use ink settings page to change the status of their ink to private or public. Ink settings also allows them do delete inks ![Image of ink deletion prompt screen](/capstone/media/readme/)

## **2. Co-authorship**

### 2.1 Who are Co-Authors?
### 2.2 Co-author requests and review

## **3. Discoverability**

### 3.1 Timeline
### 3.2 Discover Authors
### 3.3 Viewing Inks