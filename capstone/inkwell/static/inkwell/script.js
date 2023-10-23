function getCsrf(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function timeline() {

    document.querySelector("#mainTimelineBtn").style.display = 'none';

    // Clear the timeline feed
    document.querySelector("#timeline").innerHTML = '';

    // Declare the page
    let page = 1;
    
    function load(page, timeline) {
        fetch(`timeline/${page}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            data[timeline].forEach(element => {
                const ink_div = document.createElement('div');
                ink_div.className = 'inkDiv';

                const statusSpan = document.createElement('span');
                if (!element.updateStatus) {
                    statusSpan.innerHTML = `<a href="well/${element.inkOwner}">${element.inkOwner}</a> posted a new Ink`;
                }
                else {
                    statusSpan.innerHTML = `<a href="well/${element.inkOwner}">${element.inkOwner}</a> updated ${element.title}`;
                }
                ink_div.append(statusSpan);
                
                const inkLink = document.createElement('a');
                inkLink.className = 'inkLink';
                inkLink.href = `ink_view/${element.id}`;

                const contents = document.createElement('p');
                contents.className = 'inkPostDescription';
                contents.innerHTML = `${element.description}`;

                inkLink.append(contents);
                ink_div.append(inkLink);

                const date = document.createElement('span');
                date.className = 'date';
                date.innerHTML = `Created: ${element.creation_date}`;
                ink_div.append(date);

                document.querySelector("#timeline").append(ink_div);
            });
        })
    }

    load(page, "allInks");

    function infiniteScroll (timeline) {
        window.onscroll = () => {
            if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
                load(page, timeline);
                page++;
            }
        };
    }

    function mainTimelineBtn () {
        page = 1;
        document.querySelector("#mainTimelineBtn").style.display = 'block';
        document.querySelector("#followingTimelineBtn").style.display = 'none';
        load(page, "allInks");
        infiniteScroll("allInks");
    }
    function followingTimelineBtn () {
        page = 1;
        document.querySelector("#mainTimelineBtn").style.display = 'none';
        document.querySelector("#followingTimelineBtn").style.display = 'block';
        load(page, "followedInks");
        infiniteScroll("followedInks");
    }
    document.querySelector("#mainTimelineBtn").addEventListener('click', mainTimelineBtn);
    document.querySelector("#followingTimelineBtn").addEventListener('click', followingTimelineBtn);
}

function notifications() {
    let page = 1;

    function loadNotifications () {
        fetch(`notifications/${page}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            data.forEach(element => {
                const notiDiv = document.createElement('div');
                notiDiv.className = 'notiDiv';

                const link = document.createElement('a');
                link.className = 'notiRedirect';
                link.href = `${element.url}`;

                const notiMessage = document.createElement('p');
                notiMessage.className = 'nofiContents';
                notiMessage.innerHTML = `${element.contents}`;
                link.append(notiMessage);

                const date = document.createElement('span');
                date.className = 'notiDate';
                date.innerHTML = `${element.date}`;
                link.append(date);

                notiDiv.append(link);

                document.querySelector("#notifications").append(notiDiv);
            });
        })
    }

    loadNotifications();

    const notiColumn = document.querySelector("#notifications_col");
    notiColumn.onscroll = () => {
        if (notiColumn.clientHeight + notiColumn.scrollTop >= notiColumn.scrollHeight) {
            page++;
            loadNotifications();
        }
    };
}

function follow(command) {
    const csrftoken = getCsrf('csrftoken');
    const followee = document.querySelector("#well-username").dataset.name;

    fetch(`${followee}/${command}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify({
            followee: followee
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error(error);
    });
    setTimeout(() => {
        location.reload();
    }, 50);
}

// Changes the follow/unfollow button
function following_switch() {
    const following_check = document.querySelector("#following-check").dataset.following;
    console.log(following_check);
    if (following_check === "True") {
        document.querySelector("#followBtn").style.display = 'none';
        document.querySelector("#unfollowBtn").style.display = 'block';
    }
    else if (following_check === "False") {
        document.querySelector("#followBtn").style.display = 'block';
        document.querySelector("#unfollowBtn").style.display = 'none';
    }
}

function displayMessage(messageDivID, message, color) {
    const messageDiv = document.getElementById(`${messageDivID}`);
    messageDiv.innerHTML = ''; // Clear the message div
    if (color == "red") {
        messageDiv.className = 'alert alert-danger';
        messageDiv.role = 'alert';
    }
    else if (color == "green") {
        messageDiv.className = 'alert alert-success';
        messageDiv.role = 'alert';
    }
    const messageContent = document.createElement('h5');
    messageContent.className = 'message text-center';
    messageContent.innerHTML = `${message}`;
    messageDiv.append(messageContent);
}

function checkTitleAvailability() {
    const title = document.getElementById("title");
    const csrftoken = getCsrf('csrftoken');

    title.addEventListener('input', () => {
        setTimeout(() => {
            fetch("checkNewInkTitle", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                body: JSON.stringify({
                    title: title.value
                })
            })
            .then(response => response.json())
            .then(data => {
                if (title.value.trim() === "") {
                    document.getElementById("messageNewInk").style.display = 'none';
                }
                else {
                    document.getElementById("messageNewInk").style.display = 'block';
                    displayMessage("messageNewInk", data.message, data.color);
                }

                // Disable the submit button if the title is taken
                const submitButton = document.getElementById("createInk");
                if (data.color == "red") {
                    submitButton.disabled = true;
                }
                else if (data.color == "green") {
                    submitButton.disabled = false;
                }
            })
            .catch(error => {
                console.error(error);
            });
        }, 500);
    });
}

function loadQuillEditors() {
    const editors = document.querySelectorAll(".editor");
    for (var index = 0; index < editors.length; index++) {
        var editorDiv = editors[index];
        var contents = editorDiv.dataset.contents;
        var initialDelta = [{insert: contents}];
        var quill = new Quill('#editor-' + (index+1), {
            theme: 'snow'
        });
        quill.setContents(initialDelta);
    }
}

function addChapter () {
    document.querySelector("#addChapterBtn").style.display = 'none';
    document.querySelector("#cancelAddingNewChapter").style.display = 'block';
    document.querySelector("#addChapterForm").style.display = 'block';
}

function cancelAddingNewChapter() {
    document.querySelector("#addChapterBtn").style.display = 'block';
    document.querySelector("#cancelAddingNewChapter").style.display = 'none';
    document.querySelector("#addChapterForm").style.display = 'none';
}