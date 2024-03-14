$(function(){
    $('button.submit-email').each(function () {
        const submitButton = this;
        const form = this.closest('form');
        const emailInput = form.elements['email'];
        emailInput.addEventListener("keydown", function(event) {
            if (event.keyCode === 13) {
                event.preventDefault();
                $(submitButton).click();
            }
        });
    });

    $('button.submit-email').on('click', async function(){
        const form = this.closest('form');
        const fieldset = this.closest('fieldset');
        const emailInput = form.elements['email'];
        const tokenOutput = document.getElementById('token-output');
        const button = form.querySelector('button.submit-email');
        emailInput.value = emailInput.value.trim().toLowerCase();

        const body = new FormData(form);
        fieldset.disabled = true;
        var buttonOldContent = null;
        if(button !== undefined){
            buttonOldContent = button.innerHTML;
            button.innerHTML = '';
            const spinner = document.createElement('div');
            spinner.classList.add('spinner-border', 'spinner-border-sm', 'text-light');
            spinner.role = 'status';
            button.appendChild(spinner);
        }
        const response = await fetch(form.action, {
            method: form.method, body: body,
        });
        fieldset.disabled = false;
        if(button !== undefined){
            button.innerHTML = buttonOldContent;
        }
        if (!response.ok) {
            Toast.fire({
                icon: 'error', title: "Error generating token"
            });
        }else{
            // print url
            Toast.fire({
                icon: 'success', title: "Generated token successfully"
            });
            var currentURL = new URL(window.location.href);
            tokenOutput.value =  currentURL.protocol + "//" + currentURL.host + await response.text();
        }
    });
});