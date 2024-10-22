function getCsrf(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function timeline() {

    mainTimelineBtn = document.querySelector("#mainTimelineBtn");
    mainTimelineBtnFooter = document.querySelector("#mainTimelineBtnFooter");
    followingTimelineBtn = document.querySelector("#followingTimelineBtn");
    followingTimelineBtnFooter = document.querySelector("#followingTimelineBtnFooter");

    mainTimelineBtn.style.display = 'none';
    mainTimelineBtnFooter.style.display = 'none';

    // Declare the page
    let page = 1;

    // Clear the timeline feed
    document.querySelector("#timeline").innerHTML = '';
    let infiniteScrollSwitch = true;
    
    function load(page, timeline) {
        fetch(`timeline/${page}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (Array.isArray(data[timeline])) {
                data[timeline].forEach(element => {
                    const ink_div = document.createElement('div');
                    ink_div.className = 'inkPostDiv';
    
                    const statusSpanDiv = document.createElement('div');
                    statusSpanDiv.className = '';
    
                    const statusSpan = document.createElement('span');
                    statusSpan.innerHTML = `${element.postMessage}`;
    
                    statusSpanDiv.append(statusSpan);
    
                    for (var i = 0; i < element.tags.length; i++) {
                        const tagDiv = document.createElement('div');
                        tagDiv.className = 'tag';
                        const tagSpan = document.createElement('span');
                        tagSpan.innerHTML = `${element.tags[i]}`;
                        tagDiv.append(tagSpan);
                        statusSpanDiv.append(tagDiv);
                    }
                    
                    ink_div.append(statusSpanDiv);
                    
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
            }
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
        })

        window.onscroll = () => {
            if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
                if (infiniteScrollSwitch == true) {
                    page++;
                    load(page, timeline);    
                }
            }
        };    
    }

    load(page, "allInks");

    mainTimelineBtn.addEventListener('click', () => {
        page = 1;
        mainTimelineBtn.style.display = 'none';
        followingTimelineBtn.style.display = 'block';
        mainTimelineBtnFooter.style.display = 'none';
        followingTimelineBtnFooter.style.display = 'block';
        // Clear the timeline feed
        document.querySelector("#timeline").innerHTML = '';
        load(page, "allInks");
    });

    followingTimelineBtn.addEventListener('click', () => {
        page = 1;
        mainTimelineBtn.style.display = 'block';
        followingTimelineBtn.style.display = 'none';
        mainTimelineBtnFooter.style.display = 'block';
        followingTimelineBtnFooter.style.display = 'none';
        // Clear the timeline feed
        document.querySelector("#timeline").innerHTML = '';
        load(page, "followedInks");
    });

    mainTimelineBtnFooter.addEventListener('click', () => {
        page = 1;
        mainTimelineBtn.style.display = 'none';
        followingTimelineBtn.style.display = 'block';
        mainTimelineBtnFooter.style.display = 'none';
        followingTimelineBtnFooter.style.display = 'block';
        // Clear the timeline feed
        document.querySelector("#timeline").innerHTML = '';
        load(page, "allInks");
    });

    followingTimelineBtnFooter.addEventListener('click', () => {
        page = 1;
        mainTimelineBtnFooter.style.display = 'block';
        followingTimelineBtnFooter.style.display = 'none';
        mainTimelineBtn.style.display = 'block';
        followingTimelineBtn.style.display = 'none';
        // Clear the timeline feed
        document.querySelector("#timeline").innerHTML = '';
        load(page, "followedInks");
    });
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

    const notiColumn = document.querySelector("#notifications-col");
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

    fetch(`${followee}/${command}`, { // command argument is either "follow" or "unfollow"
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

function followInk(command) {
    const csrftoken = getCsrf('csrftoken');
    const inkID = document.querySelector("#dataInkID").dataset.inkid;

    fetch(`${inkID}/${command}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        }
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

// Displaying messages, connected with checkAvailability function
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

function checkAvailability(fetchUrl, messageDivId, submitBtnId, checkInputId) {
    const checkInput = document.getElementById(`${checkInputId}`);
    const csrftoken = getCsrf('csrftoken');

    checkInput.addEventListener('input', () => {
        setTimeout(() => {
            fetch(fetchUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                body: JSON.stringify({
                    check: checkInput.value
                })
            })
            .then(response => response.json())
            .then(data => {
                if (checkInput.value.trim() === "") {
                    document.getElementById(messageDivId).style.display = 'none';
                }
                else {
                    document.getElementById(messageDivId).style.display = 'block';
                    displayMessage(messageDivId, data.message, data.color);
                }

                // Disable the submit button if the checked input is taken
                const submitButton = document.getElementById(submitBtnId);
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

function updatingTags(formID) {
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
            var currentContainer = draggable.parent(); // Get the current container

            // Determine the target container
            var targetContainer = currentContainer.attr("id") === "chosenTags" ? $("#availableTags") : $("#chosenTags");

            handleDrop(draggable, targetContainer);
        });

        function handleDrop(draggable, targetContainer) {
            // Calculate the position relative to the container
            var position = draggable.position();
            var containerPosition = targetContainer.offset();

            var left = position.left - containerPosition.left;
            var top = position.top - containerPosition.top;

            // Set the position relative to the container
            draggable.css({
                left: left,
                top: top
            });

            // Append the dragged div to the target container
            targetContainer.append(draggable);

            // Manually revert the dragged div to its original position
            draggable.css({
                left: 0,
                top: 0
            });
        }
    });

    $(document).ready(function() {
        // Update the hidden input field with a list of data from all the divs
        function updateHiddenField() {
            var tagDataList = $("#chosenTags .tag").map(function() {
                return $(this).text();
            }).get().join(',');

            $("#tagDataListField").val(tagDataList);
        }

        // Call the updateHiddenField function when the form is submitted
        $(formID).submit(function() {
            updateHiddenField();
        });
    });
}

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

function privatizeInk(inkID, command) {
    const csrftoken = getCsrf('csrftoken');

    fetch(`privatizeInk/${inkID}/${command}`, { // Command can be either "makePublic" or "makePrivate"
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        }
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
    }, 1000);
}

// Chapter buttons
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

function deleteChapterSwitch() {
    document.querySelector("#deleteChapterSwitch").style.display = 'none';
    document.querySelector("#deleteChapterConfirmationDiv").style.display = 'block';
    document.querySelector("#deleteChapterBtn").style.display = 'block';
}

function keepChapter() {
    document.querySelector("#deleteChapterSwitch").style.display = 'block';
    document.querySelector("#deleteChapterConfirmationDiv").style.display = 'none';
    document.querySelector("#deleteChapterBtn").style.display = 'none';
}

// Co Author request buttons
function declineRequest() {
    document.querySelector("#confirmDeclineBtn").style.display = 'block';
    document.querySelector("#declineMessageTextArea").style.display = 'block';
    document.querySelector("#go-backCARequestBtn").style.display = 'block';
    document.querySelector("#declineCARequestBtn").style.display = 'none';
    document.querySelector("#acceptCARequestBtn").style.display = 'none';
}

function goBackBtn() {
    document.querySelector("#confirmDeclineBtn").style.display = 'none';
    document.querySelector("#declineMessageTextArea").style.display = 'none';
    document.querySelector("#go-backCARequestBtn").style.display = 'none';
    document.querySelector("#declineCARequestBtn").style.display = 'block';
    document.querySelector("#acceptCARequestBtn").style.display = 'block';
}

// Comments buttons
function deleteCommentBtn() {
    document.querySelector("#deleteCommentButton").style.display = 'none';
    document.querySelector("#deleteCommentForm").style.display = 'block';
}

function dontDeleteComment() {
    document.querySelector("#deleteCommentButton").style.display = 'block';
    document.querySelector("#deleteCommentForm").style.display = 'none';
}

// Index notifications and discover authors buttons
function authorsBtn() {
    var authorsStyle = document.querySelector(".authors-style");
    var authorsCol = document.querySelector(".authors-col");

    var computedStyle = window.getComputedStyle(authorsStyle);

    if (computedStyle.display === 'none') {
        authorsStyle.style.display = 'block';
        authorsCol.style.display = 'block';
        authorsCol.style.width = '315px';
    } 
    else {
        authorsStyle.style.display = 'none';
        authorsCol.style.display = 'none';
        authorsCol.style.width = 'auto';
    }
}

function notificationsBtn() {
    var notificationsStyle = document.querySelector(".notifications-style");
    var notificationsColStyle = document.querySelector(".notifications-col-style");

    var computedStyle = window.getComputedStyle(notificationsStyle);

    if (computedStyle.display === 'none') {
        notificationsStyle.style.display = 'block';
        notificationsColStyle.style.display = 'block';
        notificationsColStyle.style.width = '300px';
        notificationsColStyle.style.border = 'var(--border-color) 1px solid';
    } 
    else {
        notificationsStyle.style.display = 'none';
        notificationsColStyle.style.display = 'none';
        notificationsColStyle.style.width = 'auto';
        notificationsColStyle.style.border = 'none';
    }
}
