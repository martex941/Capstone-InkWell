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
                    statusSpan.innerHTML = `<a href="well/${element.inkOwner}"></a> posted a new Ink`;
                }
                else {
                    statusSpan.innerHTML = `<a href="well/${element.inkOwner}"></a> updated ${element.title}`;
                }
                ink_div.append(statusSpan);

                const contents = document.createElement('p');
                contents.className = 'inkPostDescription';
                contents.innerHTML = `${element.description}`;
                ink_div.append(contents);

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
                notiDiv.className = 'notificaiton-div';

                const link = document.createElement('a');
                link.className = 'notification-redirect';
                link.href = `${element.url}`;

                const notiMessage = document.createElement('p');
                notiMessage.className = 'nofitication-contents';
                notiMessage.innerHTML = `${element.contents}`;
                link.append(notiMessage);

                const date = document.createElement('span');
                date.className = 'notification-date';
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

document.addEventListener("DOMContentLoaded", () => {
    timeline();
    notifications();
});