{
    const avatarEditorModalElement = document.getElementById('avatarEditorModal');
    const avatarDivs = document.querySelectorAll('div.avatar.editable');

    if(avatarEditorModalElement){
        const avatarEditorModal = new bootstrap.Modal(avatarEditorModalElement, {});
        avatarDivs.forEach(avatarDiv => {
            const childDivs = avatarDiv.querySelectorAll('div');
            childDivs.forEach(childDiv => {
                childDiv.onclick = function () {
                    avatarEditorModal.show(childDiv.parentElement);
                };
            });
        });
    }else{
        avatarDivs.forEach(avatarDiv => {
            avatarDiv.classList.remove('editable');
            console.warn('Editable avatar element found, but no avatar editor modal is present!');
        });
    }
}
