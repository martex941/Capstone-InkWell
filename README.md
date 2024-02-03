# **InkWell**
<sub>by Kamil Wiśniewski</sub>

## **What is InkWell?**
InkWell is a website for writers to write and collaborate on their projects. It features a rich text editor using [Django Quill by LeeHanYeong](https://github.com/LeeHanYeong/django-quill-editor). The idea behind InkWell was to create a basic version of GitHub but for people who write books, short stories or anything similarily related. 


### **Featuring:**
- [django-quill-editor](https://pypi.org/project/django-quill-editor/) for text editing.
- [Pillow](https://pypi.org/project/Pillow/) for profile pictures.
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/) for tags.

# **Overview**

## **1. Writing**

### 1.1 Inks and Chapters
Ink is a name for any body of writing on the website, whether it be a short story, a long novel, a public diary or even an essay. The ink model is the biggest of all in this project. It features a three ManyToManyFields one of which links users who are co-authors, another that acts as a follower list and the last one is used for adding tags. It also has two BooleanField's which correspond to its privacy and update statuses. Lastly, it obviously has CharFields for description and title and DateTimeField as well as PositiveBigIntegerField for date and view count.

Inks are not divided by pages like typical pieces of writing, they are divided by chapters instead. The chapter model is a lot smaller than ink model, however, it is the only model that features a QuillField to store its rich text contents. It also has basic fields that correspond to chapter numbers, titles and ForeignKey to its ink of origin.

### 1.2 Editing Chapters
InkWell utilizes [Django Quill](https://github.com/LeeHanYeong/django-quill-editor) to let writers edit chapters in their inks.
![Image of Django Quill editor while editing a chapter](/capstone/media/readme/)
Writers have a lot of freedom in chosing how their work is going to look. They can add images, change fonts, colors, background colors and even embed videos.

```html
<form class="form editChapterForm" action="{% url 'edit_chapter' chapterID=chapterInfo.id inkID=inkID %}" method="post">
    {% csrf_token %}
    {{form.media}}
    <div>
        {% if editingAsCoAuthor %}
            <span class="fw-bold">Editing Chapter {{ chapterInfo.chapterNumber }}: {{chapterInfo.chapterTitle}}</span>
        {% else %}
            <span class="fw-bold">Editing Chapter {{ chapterInfo.chapterNumber }}: {{form.chapterTitle}}</span>
        {% endif %}
    </div>
    <div class="row d-flex justify-content-between p-0">
        {% if editingAsCoAuthor %}
            <button class="btn btn-primary" type="submit">Send co-author request</button>
        {% else %}
            <button class="btn btn-primary m-2" type="submit">Save Changes</button>
            <button class="btn btn-danger m-2" id="deleteChapterBtn" type="submit" name="deleteChapter" style="display: none;">DELETE</button>
        {% endif %}
    </div>
    <div>
        {{form.chapterContents}}
        {% if editingAsCoAuthor %}
            {{form.requestedContentChange}}
        {% endif %}
    </div>
</form>
```
The form which is used for editing content is different for authors and co-authors accordingly, for examply only an author can change the title of a chapter and made immidiate changes to its contents as well as initiate deletion process and go through with it. Restrictions such as these have been applied throughout the project in order to disallow any malicious activity.


### 1.3 Editing Inks
Editing an ink allows the author to change its title, description, tags and contents of individual chapters.
![Image of ink editing screen](/capstone/media/readme/)

Authors can also use ink settings page to change the status of their ink to private or public. The page is also where they can delete their inks 
![Image of ink deletion prompt screen](/capstone/media/readme/)

## **2. Co-Authorship**

### 2.1 Who are Co-Authors?
Co-Authors are users who have made at least one positively reviewed change in another author's chapter. 
They are credited when you view an ink.
![Image showing ink title, credited author and link to a list of co-authors](/capstone/media/readme/)
![Image showing a list of co-authors](/capstone/media/readme/)


### 2.2 Co-author requests and review

## **3. Discoverability**

### 3.1 Timeline
### 3.2 Discover Authors
### 3.3 Viewing Inks