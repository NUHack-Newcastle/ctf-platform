$(function(){
    function inputError(input, message) {
        const oldMsg = input.parentNode.querySelector('div.invalid-feedback');
        if(oldMsg !== null) oldMsg.remove();
        input.classList.add('is-invalid');
        const msg = document.createElement('div');
        msg.classList.add('invalid-feedback');
        msg.innerText = message;
        input.parentNode.append(msg);
        input.oninput = function () {
            this.oninput = null;
            this.classList.remove('is-invalid');
            msg.remove();
        }
    }


    $('button.submit-flag').each(function () {
        const submitButton = this;
        const form = this.closest('form');
        const flagInput = form.elements['flag'];
        flagInput.oninput = null;
        flagInput.classList.remove('is-invalid');
        const badMsg = flagInput.parentNode.querySelector('div.invalid-feedback');
        if(badMsg !== null) badMsg.remove();
        flagInput.addEventListener("keydown", function(event) {
            if (event.keyCode === 13) {
                event.preventDefault();
                $(submitButton).click();
            }
        });
    });

    $('button.submit-flag').on('click', async function(){
        const form = this.closest('form');
        const fieldset = this.closest('fieldset');
        const flagInput = form.elements['flag'];
        const button = form.querySelector('button.submit-flag');
        flagInput.value = flagInput.value.trim().toLowerCase();
        // validate flag
        if(flagInput.value === ''){
            // no flag given
            inputError(flagInput, 'Nice try, but you need to enter a flag first!');
        }else if(!/flag{.*}/.test(flagInput.value)){
            // not format flag{}
            if(/(?:\d|[a-f]){16}/.test(flagInput.value)){
                inputError(flagInput, "Not quite - don't take the digits out of the flag{} container.");
            }else{
                inputError(flagInput, "That doesn't look right. Flags should always begin with flag{ and end with a }.");
            }
        }else if(!/flag{(?:\d|[a-f]){16}}/.test(flagInput.value)){
            // not format flag{16-lowercase-hex}
            inputError(flagInput, "That doesn't look right. Flags should always be in the format flag{xxxxxxxxxxxxxxxx}, where x is a digit 0-9 or letter a-f. That's 16 hexadecimal digits.");
        }else{
            fieldset.disabled = true;var buttonOldContent = null;
            if(button !== undefined){
                buttonOldContent = button.innerHTML;
                button.innerHTML = '';
                const spinner = document.createElement('div');
                spinner.classList.add('spinner-border', 'spinner-border-sm', 'text-light');
                spinner.role = 'status';
                button.appendChild(spinner);
            }
            const body = new FormData(form);
            const response = await fetch(form.action, {
                method: form.method, body: body,
            });
            fieldset.disabled = false;
            if(button !== undefined){
                button.innerHTML = buttonOldContent;
            }
            if (!response.ok) {
                if (response.status === 410) {
                    if (response.headers.get("Content-Type").split(';')[0] === "text/plain"){
                        deferToast('warning',  await response.text());
                    }else{
                        deferToast('warning', "The server isn't accepting flags for this challenge at this time.");
                    }
                }else{
                    Toast.fire({
                        icon: 'error', title: "Flag was rejected by the server"
                    });
                    if(response.headers.get("Content-Type").split(';')[0] === "text/plain"){
                        inputError(flagInput, await response.text());
                    }else{
                        inputError(flagInput, "The flag was rejected by the server.");
                    }
                }
            }else{
                deferToast('success', 'Flag was accepted!');
            }
        }
    });
});