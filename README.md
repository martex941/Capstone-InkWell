# **InkWell**
<sub>by Kamil Wiśniewski</sub>

### **Languages used:**
- HTML
- CSS
- JavaScript
- Python (Django)

### **Packages used:**
- [django-quill-editor](https://pypi.org/project/django-quill-editor/)
- [Pillow](https://pypi.org/project/Pillow/)
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/)
- [jQuery](https://jquery.com/)
- [Bootstrap](https://getbootstrap.com/)

# **Overview**

## **0. Distinctiveness and Complexity**
With InkWell I wanted to create a website with some connection to books, similarily to my final project for CS50x where I made a website called ReadRoll. It recommended a random book to the user based on a chosen genre. This time I created a website that allows users to write books or any other body of writing, however, I did not think that writing text online was enough of a challenge. Therefore, I added a GitHub-like spin to it. Users can make "pull requests" which are called "Co-author requests" to suggest content changes for other authors. authors can then review these changes and see what content was added or deleted (akin to GitHub) and decide to "push" them into production, i.e., accept the Co-author request, change the content and permanently add that author to their list of Co-authors. That is the main premise of InkWell, however, there are many more features that make the website great, below is an extensive overview of these features.

## **1. Writing**

### 1.1 Inks and Chapters
Ink is a name for any body of writing on the website, whether it be a short story, a long novel, a public diary or even an essay. The ink model is the biggest of all in this project. It features a three ManyToManyFields one of which links users who are Co-authors, another that acts as a follower list and the last one is used for adding tags. It also has two BooleanField's which correspond to its privacy and update statuses. It has CharFields for description and title, DateTimeField as well as PositiveBigIntegerField for date and view count.

Inks are not divided by pages like typical pieces of writing, they are divided by chapters instead. The chapter model is a lot smaller than the ink model, however, it is the only model that features a QuillField to store its rich text contents. It also has basic fields that correspond to chapter numbers, titles and ForeignKey to its ink of origin.

### 1.2 Editing Chapters
InkWell utilizes [Django Quill](https://github.com/LeeHanYeong/django-quill-editor) to let writers edit chapters in their inks. Writers have a lot of freedom in chosing how their work is going to look. They can add images, change fonts, colors, background colors and even embed videos.

![Image showing author's point of view when editing a chapter](/capstone/media/readme/editing-chapter.png)

The form which is used for editing content is different for authors and Co-authors accordingly, for example only an author can change the title of a chapter and make immidiate changes to its contents as well as initiate deletion process and go through with it. Restrictions such as these have been applied throughout the project in order to not allow any malicious activity.
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
            <button class="btn btn-primary" type="submit">Send Co-Author request</button>
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

Changing the title and description is quite straightforward. Changing tags is quite trickier, this is where [BeautifulSoup](https://pypi.org/project/beautifulsoup4/) comes in. It helps us convert the tags from tagsData input in the form into a list of strings which are then used to find appropriate tag objects to assign them to the ink.
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

The UI is designed in the form of two containers. Upper one that constitutes of assigned tags and tags ready to be assigned, and lower which contains all tags that are not assigned yet and can be either dragged or clicked to be moved into the upper container.
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

All of it is possible thanks to the updateTags JavaScript function that utilizes [jQuery](https://jquery.com/). It handles positioning of the tags when they are dragged or clicked in both containers interchangeably which adds a nice responsive feel to the form.
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
It also assigns all the tags from the upper container into the tagData input after form submission.
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

Authors can also use the "Ink Settings" page to change the status of their ink to private or public and delete them.

![Image of ink deletion prompt screen](/capstone/media/readme/delete-ink-confirm.png)

### 1.3 Viewing Inks
Upon viewing an ink the user will see three distinct sections.
- ink info that features its title, views, author name, link to Co-author credit list, tags and ink contents divided into chapters 
- chapter navigation and buttons for editing and following the ink
- comment section where users can share their opinions

Firstly, the main ink container is quite straightforward as it just takes information from the server and serves it in a container. 
![Image of ink viewing container](/capstone/media/readme/ink-view.png)
Secondly, the chapter navigation is positioned on the left even if the user scrolls down (unless viewing in lower width resolution upon which it stays at the top).
![Gif showing changing resolution which results in UI shift.](/capstone/media/readme/window-resizing.gif)

## **2. Co-Authorship**

### 2.1 Who are Co-Authors?
Co-authors are users who have made at least one positively reviewed change in another author's chapter. There is no distinct Co-author model in the database as there is no need for one, there are just ManyToManyFields which link user objects referring to them as Co-authors. Co-authors play an important roll in InkWell, because they can contribute to any public ink. Anyone can open the Co-author list and see who contributed to a given ink.
![Image showing a list of Co-authors](/capstone/media/readme/ink-co-authors.png)

### 2.2 Co-author requests and review
Co-author requests are suggestions for content change made by authors who are not the original authors of the said content.

![Image showing Edit Chapter page for a Co-author](/capstone/media/readme/co-author-editing-chapter.png)

```python
if editingAsCoAuthor:
    form = CoAuthorRequestForm(request.POST)
    if form.is_valid():
        # Create new Co-Author request
        new_coAuthorRequest = CoAuthorRequest(coAuthor=current_user, requestedChapter=chapterInfo)
        new_coAuthorRequest.save()
        time.sleep(1)

        # Update the new Co-Author request using the form
        form = CoAuthorRequestForm(request.POST, instance=new_coAuthorRequest)
        form.save()
        time.sleep(1)

        # Create a notification for the author
        new_notification = Notification(
            notifiedUser=inkInfo.inkOwner, 
            contents=f'New Co-Author request from {current_user} regarding Chapter {chapterInfo.chapterNumber}: {chapterInfo.chapterTitle} of ink titled "{inkInfo.title}"', 
            url=f"coAuthorRequest/{chapterInfo.id}/{new_coAuthorRequest.id}")
        new_notification.save()
```
Sending a Co-author request creates a notification for the author who then can open the request review screen by clicking on it.

![Image of a Co-author request notification](/capstone/media/readme/co-author-request-notif.png)

On the Co-author request review page the author can then see what content was deleted, highlighted by red background, and what was added to their work, highlighted by green background, similarily to GitHub.
```javascript
function coAuthorRequestHighlight() {
    var originalText = document.getElementById("originalText").innerText;
    var modifiedText = document.getElementById("modifiedText").innerText;
    var deletedText = document.getElementById("whatWasDeleted").innerText;

    var result = "";
    
    for (var i = 0; i < modifiedText.length; i++) {
        if (modifiedText[i] !== originalText[i]) {
            result += '<span class="added">' + modifiedText[i] + '</span>';
        }
        else {
            result += modifiedText[i];
        }
    }
    document.getElementById("modifiedText").innerHTML = result;

    var deletedHighlight = "";
    for (var i = 0; i < deletedText.length; i++) {
        if (deletedText[i] !== modifiedText[i]) {
            deletedHighlight += '<span class="deleted">' + deletedText[i] + '</span>';
        }
        else {
            deletedHighlight += deletedText[i];
        }
    }
    document.getElementById("whatWasDeleted").innerHTML = deletedHighlight;
}
```
![Image of a Co-author request review page showing three containers, one with original content, another showing deleted content and the last one which displays added content](/capstone/media/readme/co-author-request-view.png)

If the author accepts the request then the change is instantaneous, if they decide to reject it however, then they will have to provide a reason as to why the suggested content change was not adequate for their work.
![Image showing request rejection screen](/capstone/media/readme/decline-request-reason.png)

## **3. Discoverability**

### 3.1 Timeline
The post timeline which is situated in the middle on the main page of InkWell shows all posts related to all public inks. It has a following filter which shows posts only made by the authors that the current user follows. Depending on the post they can have various information displayed; there are posts which display that an ink has been updated by the author themselves, other ones that show that another author updated it (which is a result of a successful Co-author request review) and lastly, posts which just display that an ink has been created (only if the author did not check the "Make Ink Private" checkmark during its creation). Aside from this every post always shows ink tags (if any were added), ink description, original author's name, ink title and creation date.
![Image showing the main timeline](/capstone/media/readme/main-timeline.png)
![Image of a post that shows a successful Co-author request](/capstone/media/readme/co-author-request-post.png)

The timeline also has infinite scroll function that loads the content as the user scrolls down.
```javascript
window.onscroll = () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        if (infiniteScrollSwitch == true) {
            page++;
            load(page, timeline);    
        }
    }
};    
```
It also shows a message once there is no more content to load and subsequently stops the infinite scroll function.
```javascript
else {
    infiniteScrollSwitch = false;
    const emptyPageDiv = document.createElement('div');
    emptyPageDiv.className = 'emptyPageDiv text-center';

    const emptyPageSpan = document.createElement('span');
    emptyPageSpan.className = 'emptyPageSpan';
    emptyPageSpan.innerHTML = "The end";

    emptyPageDiv.append(emptyPageSpan);

    document.querySelector("#timeline").append(emptyPageDiv);
}
```


### 3.2 Discover Authors
Discover authors section is also displayed on the main page and sits on the left side of the screen. It consists of several categories: popular authors, top authors, top Co-authors and discover authors. Let's break them down.

1. Popular authors are determined by combining author's readers (summed up amount of views from all inks) and followers. As the most popular authors are the ones that got the highest viewcounts and most followers.
2. Top authors are the ones who did the most amount of writing that week and had the highest amount of successful Co-author requests for their works.
3. Top Co-authors are determined by their amount of accepted Co-author requests to the works of others.
4. Discover authors are 10 randomly selected authors with no conditions other than luck.

The discover authors section is set to update at least every 7 days (if the server is up) where the start date is 1st of January 2024. The first time index page is loaded on the 7-day (or longer) period date, the global date sets itself and is triggered in another 7 days or more.
```python
startDate = UpdateAuthorsDate.objects.first()
if startDate is None:
    startDate = UpdateAuthorsDate(globalDate=datetime(2024, 1, 1))
    startDate.save()

currentDate = timezone.now()
timeDifference = currentDate - startDate.globalDate

if timeDifference >= timedelta(days=7):
    updateDiscoverAuthors(request)
    startDate.globalDate = currentDate
    startDate.save()
```

### 3.3 Search Function
The search function operates on every page that displays a lot of data. There are smaller search functions such as searching through author's follower list, Co-author list, ink followers or Co-author requests. All they do is filter the database using the string input from the search form.

For example: the coauthors view has a "searchQuery" argument which can be used for filtering but does not have to be.
```python
def coauthors(request, username, searchQuery):
```
In urls.py coauthors view is associated with three paths, first one that is default and has no filtering, second one that can be filtered and the last path which relates to the search function itself.
```python
path('well/<str:username>/coauthors', views.coauthors, {'searchQuery':''}, name='coauthors'),
path('well/<str:username>/coauthors/<str:searchQuery>', views.coauthors, name='coauthors'),
path('searchCoAuthors/<str:username>', views.searchCoAuthors, name="searchCoAuthors"),
```
In the search function view the query is used as an argument when redirecting to the "coauthors" view page.
```python
def searchCoAuthors(request, username):
    if request.method == "POST":
        query = request.POST.get("searchCoAuthorsQuery")
        return redirect('coauthors', username=username, searchQuery=query)
    else:
        return redirect('coauthors', username=username)
```

Although nearly all searches are done the same way, there is one that is distinct, that is the main search. Main search function is located in the navigation bar and can be used to search for authors and inks. It sends the user to a page that displays the search results. It is distinct as it is not associated with any other page that already displays data, such as followers or coauthors view pages that can work without their search functions.
![Image showing main search results page](/capstone/media/readme/main-search-results.png)

Every page that is capable of displaying large amounts of data is also split into multiple pages of data using django's Paginator. The user can navigate through the pages manually with the exception of main timeline and notifications column that have infinite scrolling.
```python
pag = Paginator(coauthors, 20)
page = request.GET.get('page')
try:
    pag_items = pag.page(page)
except PageNotAnInteger:
    pag_items = pag.page(1)
except EmptyPage:
    pag_items = pag.page(pag.num_pages)

pages = range(1, pag.num_pages+1)
```

## **Final Notes**
This was a big project for me and even though I consider it finished there is still much more than can be added on top of it. I have many plans and ideas to make it into a real website that is used by people to write, collaborate and share their literary works. If that does not come to fruition then perhaps something similar to it, under a different name. In any case, this project was really fun to create and plan out and I hope someone will be inspired enough to make something great based on this idea.
