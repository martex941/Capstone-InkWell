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
The form which is used for editing content is different for authors and co-authors accordingly, for example only an author can change the title of a chapter and make immidiate changes to its contents as well as initiate deletion process and go through with it. Restrictions such as these have been applied throughout the project in order to disallow any malicious activity.
```python
if "deleteChapter" in request.POST:
    subsequentChapters = Chapter.objects.filter(chapterNumber__gt=chapterInfo.chapterNumber)
    with transaction.atomic():
        chapterInfo.delete()
        for chapter in subsequentChapters:
            chapter.chapterNumber -= 1
            chapter.save()
    time.sleep(1)
    return HttpResponseRedirect(reverse("edit_ink", kwargs={'inkID': inkID}))
```
Deletion process also handles changing numbers of any subsequent chapters.
```python
form = ChapterForm(request.POST)
if form.is_valid():
    form = ChapterForm(request.POST, instance=chapterInfo)
    form.save()
    if inkInfo.updateStatus == False:
        inkInfo.updateStatus == True
    inkInfo.save()
    time.sleep(1)
    if inkInfo.privateStatus != True:
        new_post = Post(message=f'{current_user} updated their ink "{inkInfo.title}"', referencedPostInk=inkInfo)
        new_post.save()
    return HttpResponseRedirect(reverse("edit_ink", kwargs={'inkID': inkID}))
```
Successfully saving changes creates a new Post model which is displayed on the timeline, that is of course if the ink status is set to public at the time of the change.

### 1.3 Editing Inks
Editing an ink allows the author to change its title, description, tags and contents of individual chapters.
![Image of ink editing screen](/capstone/media/readme/editing-ink.png)
```python
newInkTitle = request.POST.get("title")
newTags = request.POST.get("tagsData").split(',')
newTags = [BeautifulSoup(tag, 'html.parser').get_text(strip=True) for tag in newTags]
newDescription = request.POST.get("descriptionEdit")

if editInk.updateStatus == False:
    editInk.updateStatus == True

editInk.title = newInkTitle
editInk.tags.clear()
if newTags:
    readyNewTags = Tag.objects.filter(tagName__in=newTags)
    editInk.tags.add(*readyNewTags)
editInk.description = newDescription
editInk.save()
```
Changing the title and description is quite straightforward. Changing tags though is quite trickier, this is where BeautifulSoup comes in. It helps us convert the tags from tagsData input in the form into a list of strings which are then used to find appropriate tag objects to assign them to the ink.
```html
<div class="tagsEdit-style mt-3" id="tagsEdit">
<div class="container p-2 pb-0">
    <div class="tagContainer" id="chosenTags">
        <h5>Tags:</h5>
        {% for tag in editInk.tags.all %}
            <div class="draggable tag" id="tag">
                {{ tag.tagName }}
            </div>
        {% endfor%}
    </div>
</div>
<hr>
<div class="container tagContainer pb-2" id="availableTags">
    {% for tag in tags %}
        {% if tag not in editInk.tags.all %}
            <div class="draggable tag pd-1" id="tagEdit">
                <span id="{{ tag.tagName }}">{{ tag.tagName }}</span>
            </div>
        {% endif %}
    {% endfor %}
</div>
</div>
<input type="hidden" name="tagsData" id="tagDataListField" value="">
```
The UI is designed in the form of two containers. Upper one that constitutes of assigned tags and tags ready to be assigned, and lower which contains all tags that are not assigned yet and can be either dragged or clicked to be moved into the upper container. All of it is possible thanks to the updateTags JavaScript function.
```javascript
$(document).ready(function() {
    $(".draggable").draggable({
        revert: "invalid",
        helper: "original",
        snap: ".tagContainer",
        snapMode: "inner",
        snapTolerance: 20
    });

    $(".tagContainer").droppable({
        accept: ".draggable",
        drop: function(event, ui) {
            handleDrop(ui.helper, $(this));
        }
    });

    $(".draggable").on("click", function() {
        var draggable = $(this);
        var currentContainer = draggable.parent();

        var targetContainer = currentContainer.attr("id") === "chosenTags" ? $("#availableTags") : $("#chosenTags");

        handleDrop(draggable, targetContainer);
    });

    function handleDrop(draggable, targetContainer) {
        var position = draggable.position();
        var containerPosition = targetContainer.offset();

        var left = position.left - containerPosition.left;
        var top = position.top - containerPosition.top;

        draggable.css({
            left: left,
            top: top
        });

        targetContainer.append(draggable);

        draggable.css({
            left: 0,
            top: 0
        });
    }
});
```
It handles positioning of the tags when they are dragged or clicked in both containers interchangeably.
```javascript
$(document).ready(function() {
    function updateHiddenField() {
        var tagDataList = $("#chosenTags .tag").map(function() {
            return $(this).text();
        }).get().join(',');

        $("#tagDataListField").val(tagDataList);
    }

    $(formID).submit(function() {
        updateHiddenField();
    });
});
```
It also assigns all the tags from the upper container into the tagData input after form submission.

Authors can also use ink settings page to change the status of their ink to private or public. The page is also where they can delete their inks 
![Image of ink deletion prompt screen](/capstone/media/readme/)

### 1.3 Viewing Inks
Upon viewing an ink the user will see three distinct sections.
- ink info that features its title, views, author name, link to co-author credit list, tags and ink contents divided into chapters 
- chapter navigation and buttons for editing and following the ink
- comment section where users can share their opinions

Firstly, the main ink container is quite straightforward as it just takes information from the server and serves it in a container. 
![Image of ink viewing container](/capstone/media/readme/)
Secondly, the chapter navigation is positioned on the left even if the user scrolls down (unless viewing in lower width resolution upon which it stays at the top).
![Gif showing changing resolution which results in UI shift.](/capstone/media/readme/)

## **2. Co-Authorship**

### 2.1 Who are Co-Authors?
Co-Authors are users who have made at least one positively reviewed change in another author's chapter. There is no distinct co-author model in the database as there is no need for one, there are just ManyToManyFields which link user objects referring to them as co-authors. Co-Authors play an important roll in InkWell, because they can contribute to any public ink. Then, if their contribution is accepted they are credited when anyone views the ink. Anyone can open the co-author list and see who contributed to a given ink. There is also an indicator that shows how many contributions, small or big, a co-author has made.
![Image showing a list of co-authors](/capstone/media/readme/)

### 2.2 Co-author requests and review
```python
if editingAsCoAuthor:
    form = CoAuthorRequestForm(request.POST)
    if form.is_valid():
        # Create new co-author request
        new_coAuthorRequest = CoAuthorRequest(coAuthor=current_user, requestedChapter=chapterInfo)
        new_coAuthorRequest.save()
        time.sleep(1)

        # Update the new co-author request using the form
        form = CoAuthorRequestForm(request.POST, instance=new_coAuthorRequest)
        form.save()
        time.sleep(1)

        # Create a notification for the author
        new_notification = Notification(
            notifiedUser=inkInfo.inkOwner, 
            contents=f'New co-author request from {current_user} regarding Chapter {chapterInfo.chapterNumber}: {chapterInfo.chapterTitle} of ink titled "{inkInfo.title}"', 
            url=f"coAuthorRequest/{chapterInfo.id}/{new_coAuthorRequest.id}")
        new_notification.save()
```
Sending a co-author request creates a notification for the author who then can open the request review screen by clicking on it.
![Image of co-author request notifications on the main page](/capstone/media/readme/)

On the co-author request review page the author can then see what content was deleted, highlighted by red background, and what was added to their work, highlighted by green background, similarily to github.
![Image of co-author request review page showing three containers, one with original content, another showing deleted content and the last one which displays added content](/capstone/media/readme/)

## **3. Discoverability**

### 3.1 Timeline

### 3.2 Discover Authors

### 3.3 Search Function
