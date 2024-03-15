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

$(async () => {
    const orchStaticCard = document.getElementById('orchStaticCard');
    switch(orchStaticState){
        case "OrchestrationStaticState.NOT_STARTED":
            orchStaticCard.innerText = "The challenge server has not built this challenge for you yet. Please refresh the page in a few minutes.";
            break;
        case "OrchestrationStaticState.STARTED":
            orchStaticCard.innerText = "The challenge server has started building this challenge for you. Please refresh the page in a few minutes.";
            break;
        case "OrchestrationStaticState.BUILDING":
            orchStaticCard.innerText = "The challenge server is currently building this challenge for you. Please refresh the page in a few minutes.";
            break;
        case "OrchestrationStaticState.UPLOADING":
            orchStaticCard.innerText = "The challenge server has built this challenge for you and is now uploading it. Please refresh the page in a few minutes.";
            break;
        case "OrchestrationStaticState.COMPLETE":
            switch(orchStaticResources.type){
                case null:
                    orchStaticCard.innerText = "This challenge does not have any files to download.";
                    break;
                case "azure_blob_container":
                    fetch(`${orchStaticResources.default_endpoints_protocol}://${orchStaticResources.account_name}.blob.${orchStaticResources.endpoint_suffix}/${orchStaticResources.container_name}?restype=container&comp=list`).then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.text();
                    })
                    .then(xmlText => {
                        // Parse the XML string into an XML Document
                        const parser = new DOMParser();
                        const xmlDoc = parser.parseFromString(xmlText, 'text/xml');

                        orchStaticCard.innerHTML = '';

                        xmlDoc.querySelectorAll('Blob').forEach(blobElement => {
                            // Get the name, URL, and other properties of the Blob
                            const name = blobElement.querySelector('Name').textContent;
                            const url = blobElement.querySelector('Url').textContent;
                            const lastModified = blobElement.querySelector('Last-Modified').textContent;
                            const etag = blobElement.querySelector('Etag').textContent;

                            const link = document.createElement('a');
                            link.href = url;
                            link.innerText = name;
                            orchStaticCard.appendChild(link);
                        });
                    })
                    .catch(error => {
                        orchStaticCard.innerText = "There was an error listing your challenge files from Azure. Please refresh the page and try again.";
                        console.error('There was a problem with the fetch operation:', error);
                    });
                    break;
                default:
                    orchStaticCard.innerText = "Unexpected error parsing challenge files.";
            }
            break;
        case "OrchestrationStaticState.FAILED":
            orchStaticCard.innerText = "The challenge server failed to build this challenge for you. Please report it to an event admin.";
            break;
        default:
            orchStaticCard.innerText = "Unexpected error parsing challenge files.";
    }
});