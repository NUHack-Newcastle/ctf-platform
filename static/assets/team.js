$(function () {
    $('.leave-team').on('click', function () {
        Swal.fire({
            title: 'Are you sure you want to leave your team?',
            text: "Any challenges you have completed as part of this team will still count towards this team's totals.",
            icon: 'warning',
            confirmButtonText: 'Leave Team',
            showCancelButton: true,
            confirmButtonColor: '#dd6b55',
            reverseButtons: true,
            cancelButtonText: 'Go Back',
            showLoaderOnConfirm: true,
            preConfirm: async () => {
                const teamSize = parseInt(await (await fetch(teamSizeEndpoint)).text());
                if(teamSize === 1){
                    // team will be empty
                    const result = await (Swal.fire({
                        title: 'Are you sure?',
                        html: "You're the only person in this team. If you leave, users will be able to join this team without approval.<br><br>" +
                            `Keep a note of your team code <code>${teamSlug}</code> in case you want to re-join.`,
                        icon: 'warning',
                        showCancelButton: true,
                        confirmButtonText: 'Leave Team',
                        confirmButtonColor: '#dd6b55',
                        reverseButtons: true,
                        cancelButtonText: 'Go Back',
                    }));
                    return result.isConfirmed;
                }else if(teamSize === 2){
                    // team will only have 1
                    const result = await (Swal.fire({
                        title: 'Are you sure?',
                        text: "There's only one other person in your team. If you leave and they are waiting to join, they will be automatically approved.",
                        icon: 'warning',
                        showCancelButton: true,
                        confirmButtonText: 'Leave Team',
                        confirmButtonColor: '#dd6b55',
                        reverseButtons: true,
                        cancelButtonText: 'Go Back',
                    }));
                    return result.isConfirmed;
                }
            }
        }).then(async (result) => {
            if (result.isConfirmed) {
                const body = new FormData();
                body.set(leaveTeamCSRFName, leaveTeamCSRFToken);
                const response = await fetch(leaveTeamEndpoint, {
                    method: 'POST', body: body,
                });
                if (!response.ok) {
                    return Swal.showValidationMessage('An error occurred when attempting to leave your team.');
                }
                deferToast('success', 'Left team successfully');
            }
        });
    });
    $('.join-team').on('click', function () {
        Swal.fire({
            title: 'Join a Team',
            text: 'Please enter the team code of the team you want to join. Current team members can find their team code by going to the team page and clicking "Invite Member".',
            input: 'text',
            inputPlaceholder: 'Team Code',
            confirmButtonText: 'Join Team',
            showCancelButton: true,
            reverseButtons: true,
            cancelButtonText: 'Go Back',
            showLoaderOnConfirm: true,
            preConfirm: async (slug) => {
                var success = false;
                const body = new FormData();
                body.set(joinTeamCSRFName, joinTeamCSRFToken);
                body.set('slug', slug);
                const response = await fetch(joinTeamEndpoint, {
                    method: 'POST', body: body,
                });
                if (!response.ok) {
                    return Swal.showValidationMessage('An error occurred when attempting to join the team.');
                }
                return response.text();
            }
        }).then((result) => {
            if (result.isConfirmed) {
                deferToast('success', 'Joined team successfully');
            }
        });
    });
    $('.create-team').on('click', function () {
        Swal.fire({
            title: 'Create a Team',
            text: 'Event admins may change your team name if it is offensive or inappropriate.',
            input: 'text',
            inputPlaceholder: 'Team Name',
            confirmButtonText: 'Create Team',
            showCancelButton: true,
            reverseButtons: true,
            cancelButtonText: 'Go Back',
            showLoaderOnConfirm: true,
            preConfirm: async (name) => {
                var success = false;
                const body = new FormData();
                body.set(createTeamCSRFName, createTeamCSRFToken);
                body.set('name', name);
                const response = await fetch(createTeamEndpoint, {
                    method: 'POST', body: body,
                });
                if (!response.ok) {
                    return Swal.showValidationMessage('An error occurred when attempting to create your team.');
                }
                return response.text();
            }
        }).then((result) => {
            if (result.isConfirmed) {
                deferToast('success', 'Created team successfully');
            }
        });
    });
    $('.invite-member').on('click', function () {
        Swal.fire({
            title: 'Invite Member',
            html: `Your team code is <code>${teamSlug}</code>, it will be required by anyone who wants to join your team.`,
        });
    });
    $('.approve-member').on('click', async function () {
        const body = new FormData();
        const username = $(this).data('username');
        body.set(approveMemberCSRFName, approveMemberCSRFToken);
        body.set('username', username);
        const response = await fetch(approveMemberEndpoint, {
            method: 'POST', body: body,
        });
        if (!response.ok) {
            Toast.fire({
                icon: 'error', title: `An error occurred while approving "${username}" onto the team`
            });
        }else{
            deferToast('success', `Successfully approved "${username}" onto the team`);
        }
    });
    $('.reject-member').on('click', async function () {
        const body = new FormData();
        const username = $(this).data('username');
        body.set(rejectMemberCSRFName, rejectMemberCSRFToken);
        body.set('username', username);
        const response = await fetch(rejectMemberEndpoint, {
            method: 'POST', body: body,
        });
        if (!response.ok) {
            Toast.fire({
                icon: 'error', title: `An error occurred while rejecting "${username}" from the team`
            });
        }else{
            deferToast('success', `Successfully rejected "${username}" from the team`);
        }
    });
});