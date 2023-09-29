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
                inkLink.href = `{% url 'ink_view' inkID=${element.id} %}`;

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
        if (notiColumn.innerHeight + notiColumn.scrollY >= notiColumn.offsetHeight) {
            loadNotifications();
            page++;
        }
    };
}

function follow(fetch) {
    const csrftoken = getCsrf('csrftoken');
    const followee = document.querySelector("#well-username").dataset.name;

    fetch(fetch, {
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
    if (following_check === "True") {
        document.querySelector("#followBtn").style.display = 'none';
        document.querySelector("#unfollowBtn").style.display = 'block';
    }
    else if (following_check === "False") {
        document.querySelector("#follow-btn").style.display = 'block';
        document.querySelector("#unfollow-btn").style.display = 'none';
    }
}

document.querySelector("#followBtn").addEventListener('click', follow("follow"));
document.querySelector("#unfollowBtn").addEventListener('click', follow("unfollow"));

document.addEventListener("DOMContentLoaded", () => {
    timeline();
    notifications();
    following_switch();
});