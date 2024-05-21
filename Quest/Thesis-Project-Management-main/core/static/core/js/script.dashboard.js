document.addEventListener('DOMContentLoaded', function () {
    const projectStatusList = document.querySelectorAll('.project-status');

    projectStatusList.forEach((status) => {
        status.addEventListener('click', () => {

            // Removal and Addition of bold class
            projectStatusList.forEach(item => {
                item.classList.remove('bold')
            })

            status.classList.add('bold')

            // Fetching the updated project list
            const status_information = status.innerText.toLowerCase()
            fetch(`/update-project-list/?status_filter=${status_information}`)
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    const table_row = document.querySelectorAll(".table-row")

                    // Removing the existing row from the table
                    table_row.forEach(row => row.remove())
                    console.log(data.project_list);
                    data.project_list.forEach(project => {

                        const row = document.createElement('tr')
                        row.className = 'table-row';

                        row.innerHTML = `
                            <td>
                                <a href="/${project.get_role.toLowerCase()}/project/${project.topic_number}">
                                    ${project.title}
                                </a>
                            </td>
                            <td>${project.categories.join(', ')}</td>
                            <td>
                                <span class="status-badge ${project.is_approved ? 'status-approved' : (project.is_rejected ? 'status-rejected' : 'status-pending')}">
                                    ${project.is_approved ? 'Approved' : (project.is_rejected ? 'Rejected' : 'Pending')}
                                </span>
                            </td>
                        `
                        row.innerHTML += (project.get_role == 'Supervisor') ?
                            (
                                project.total_application_count > 0 ?
                                    `
                                    <td>
                                        <a href="/supervisor/project/${project.id}/applications/">
                                            View Application(${project.total_application_count})
                                        </a>
                                    </td>
                                    `
                                    : `
                                    <td>
                                        No Application
                                    </td>
                                    `)
                            : "";

                        row.innerHTML += (project.get_role == "Coordinator") ?
                            `
                            <td>${project.supervisor}</td>
                            `: "";

                        row.innerHTML += (project.get_role == "Coordinator" && !project.is_approved && !project.is_rejected) ?
                            `
                            <td>
                                <a href="/approve/${project.topic_number}" id="approve-action" class="action-button">Approve</a>
                                <a href="#" id="reject-action" class="action-button">Reject</a>
                            </td>    
                        `: '';

                        document.querySelector('.project-table tbody').appendChild(row)
                    })

                }).catch(error => console.log('Error: ', error))

        })
    })

    // Tooltip for logout feature
    const profileInfo = document.getElementById("profile-info");
    const tooltip = document.getElementById("logout-tooltip");

    profileInfo.addEventListener("click", function () {
        if (tooltip.classList.contains("hidden")) {
            tooltip.classList.remove("hidden");
            tooltip.classList.add("visible");
        } else {
            tooltip.classList.remove("visible");
            tooltip.classList.add("hidden");
        }
    });

    // Hide the tooltip if clicking outside the profile div
    document.addEventListener("click", function (event) {
        if (!profileInfo.contains(event.target)) {
            tooltip.classList.remove("visible");
            tooltip.classList.add("hidden");
        }
    });
});

const table = document.getElementsByClassName("project-table")[0]
const numColumns = table.querySelector('tr').querySelectorAll('th').length;
table.style.setProperty('--num-columns', numColumns)