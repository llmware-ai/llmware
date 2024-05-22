document.addEventListener('DOMContentLoaded', function () {
    const groupSelect = document.getElementById('group-select');
    const joinGroupLink = document.getElementById('join-group-link');
    const joinGroupButton = document.getElementById('join-group-button');

    function updateJoinLink() {
        const selectedGroupId = groupSelect.value;
        const joinGroupUrl = `/student/join-group/${selectedGroupId}/`;  // Adjust the URL pattern to match your Django URL pattern
        joinGroupLink.href = joinGroupUrl;
    }

    // Update the link when the page loads
    updateJoinLink();

    // Update the link whenever the selection changes
    groupSelect.addEventListener('change', updateJoinLink);

    // Handle the button click
    joinGroupButton.addEventListener('click', function (e) {
        // Prevent the form from submitting if necessary
        e.preventDefault();
        // Navigate to the dynamically set href
        window.location.href = joinGroupLink.href;
    });
});
