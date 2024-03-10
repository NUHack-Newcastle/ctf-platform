$(document).ready(function () {
    const defaultStyleSchema = {
        "$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "properties": {
            "seed": {
                "type": "string"
            }, "flip": {
                "type": "boolean", "default": false
            }, "rotate": {
                "type": "integer", "minimum": 0, "maximum": 360, "default": 0
            }, "scale": {
                "type": "integer", "minimum": 0, "maximum": 200, "default": 100
            }, "radius": {
                "type": "integer", "minimum": 0, "maximum": 50, "default": 0
            }, "size": {
                "type": "integer", "minimum": 1
            }, "backgroundColor": {
                "type": "array",
                "items": {
                    "type": "string", "pattern": "^(transparent|[a-fA-F0-9]{6})$"
                },
                "default": ["ffe082", "90caf9", "80deea", "ffab91", "b39ddb", "a5d6a7", "9fa8da", "81d4fa", "c5e1a5", "e6ee9c", "ffcc80", "f48fb1", "ce93d8", "ef9a9a", "80cbc4"]
            }, "backgroundType": {
                "type": "array", "items": {
                    "type": "string", "enum": ["solid", "gradientLinear"]
                }, "default": ["solid"]
            }, "backgroundRotation": {
                "type": "array", "items": {
                    "type": "integer", "minimum": -360, "maximum": 360
                }, "default": [0, 360]
            }, "translateX": {
                "type": "integer", "minimum": -100, "maximum": 100, "default": 0
            }, "translateY": {
                "type": "integer", "minimum": -100, "maximum": 100, "default": 0
            }, "clip": {
                "type": "boolean", "default": true
            }, "randomizeIds": {
                "type": "boolean", "default": false
            }
        }
    };
    const avatarEditorModalElement = document.getElementById('avatarEditorModal');
    const avatarStyleLicenseText = document.getElementById('avatarStyleLicenseText');
    const avatarOptionContainerScale = document.getElementById('avatarOptionContainerScale');
    const avatarOptionContainerRotate = document.getElementById('avatarOptionContainerRotate');
    const avatarOptionContainerTranslateX = document.getElementById('avatarOptionContainerTranslateX');
    const avatarOptionContainerTranslateY = document.getElementById('avatarOptionContainerTranslateY');
    const avatarOptionContainerFlip = document.getElementById('avatarOptionContainerFlip');
    const avatarOptions = document.getElementById('avatarOptions');
    const modalBody = avatarEditorModalElement.querySelector('.modal-body');
    const previewImage = modalBody.querySelector('div.avatar img');
    const cachedImages = document.createElement('span');
    var lastPreviewImage = '#';
    var avatarStyleSchemas = {};
    cachedImages.style.display = 'none';
    document.body.appendChild(cachedImages);

    avatarEditorModalElement.addEventListener('show.bs.modal', function (event) {
        event.relatedTarget.classList.add('update-on-edit');
    });

    avatarEditorModalElement.addEventListener('hidden.bs.modal', function (event) {
        document.querySelector('div.avatar.editable.update-on-edit').classList.remove('update-on-edit');
    });

    var randomButton = document.getElementById('avatarSeedRandomise');
    var avatarForm = avatarEditorModalElement.querySelector('form');

    avatarForm.addEventListener('submit', (event) => {
        event.preventDefault();
        // TODO disable form items while loading?
        previewImage.setAttribute('src', '#');
        previewImage.parentElement.classList.add('loading');
        previewImage.onload = function () {
            previewImage.parentElement.classList.remove('loading');
            previewImage.onload = null;
        };
        //
        fetch(event.target.action, {
            method: event.target.method, body: new FormData(event.target),
        }).then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json(); // or response.text() or whatever the server sends
        }).then((body) => {
            previewImage.setAttribute('src', body.avatar);
            document.querySelector('div.avatar.editable.update-on-edit img').setAttribute('src', body.avatar);
            avatarForm.elements[avatarEditorCSRFName].value = body.csrf;
        }).catch((error) => {
            previewImage.setAttribute('src', lastPreviewImage);
            alert("error");
        });
    });

    var selectElement = document.getElementById('avatarStyleSelector');
    for (var i = 0; i < selectElement.options.length; i++) {
        const style = selectElement.options[i].value;
        avatarStyleSchemas[style] = defaultStyleSchema;
        // fetch schema for this style
        fetch(`https://api.dicebear.com/7.x/${style}/schema.json`).then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        }).then((body) => {
            avatarStyleSchemas[style] = body;
            if(style === selectElement.options[selectElement.selectedIndex].value)
                updateAvatarOptions(style);
        }).catch((error) => {
        });
        // preload preview image
        var image = new Image();
        image.src = `https://api.dicebear.com/7.x/${style}/svg?seed=JD`;
        cachedImages.appendChild(image);
    }

    function formatStyle(option) {
        if (!option.id) {
            return option.text;
        }
        return $(`<span><img class="img-option" src="https://api.dicebear.com/7.x/${$(option.element).val()}/svg?seed=JD" />${option.text}</span>`);
    }

    $(selectElement).select2({
        templateResult: formatStyle,
        templateSelection: formatStyle,
        dropdownParent: avatarEditorModalElement,
        theme: 'bootstrap-5'
    });

    $(selectElement).val($(selectElement).data('existing'));
    $(selectElement).trigger('change');

    function setTransformOrigin() {
        const x = (avatarEditorOptions.translateX !== undefined ? avatarEditorOptions.translateX : 0);
        const y = (avatarEditorOptions.translateY !== undefined ? avatarEditorOptions.translateY : 0);
        previewImage.style.transformOrigin = `${50 + (x / 1)}% ${50 + (y / 1)}%`;
    }

    function valueHumanise(str){
        return str.replace(/([A-Z]|(?<![0-9])[0-9](?=[0-9]*))/g, ' $1').replace(/\w\S*/g, w => w[0].toUpperCase() + w.substr(1).toLowerCase()).trim();
    }

    function updateAvatarOptions(style) {
        const schema = avatarStyleSchemas[style];
        avatarOptions.replaceChildren();
        for (const c of document.getElementsByClassName('avatar-option')){
            c.replaceChildren();
        }
        var probabilities = {};
        for (const [key, value] of Object.entries(schema.properties)) {
            if (key === "seed" || key === "radius" || key === "size" || key === "clip" || key === "randomizeIds") continue; // we don't let the user change these
            if (key === "scale" && value.type === "integer") {
                const input = document.createElement('input');
                input.type = 'range';
                input.classList.add('form-range');
                input.min = value.minimum;
                input.max = value.maximum;
                input.name = key;
                input.title = key;
                if (avatarEditorOptions[key] !== undefined) input.value = avatarEditorOptions[key]; else input.value = value.default;
                input.addEventListener('input', function () {
                    var currentScale = value.default;
                    if (avatarEditorOptions[key] !== undefined) currentScale = avatarEditorOptions[key];
                    previewImage.style.transform = `scale(${input.value / currentScale})`;
                });
                input.addEventListener('change', function () {
                    previewImage.onload = function () {
                        previewImage.style.transform = null;
                        previewImage.onload = null;
                    }
                    avatarEditorOptions['scale'] = input.value;
                    updatePreviewImage(null);
                });
                if(avatarOptionContainerScale !== undefined){
                    if(avatarOptionContainerScale.parentElement.children[1] !== avatarOptionContainerScale){
                        input.setAttribute('orient', 'vertical');
                        // noinspection JSSuspiciousNameCombination
                        input.style.width = window.getComputedStyle(previewImage).height;
                    }
                    avatarOptionContainerScale.appendChild(input);
                }else{
                    avatarOptions.appendChild(input);
                }
            } else if ((key === "translateX" || key === "translateY") && value.type === "integer") {
                const input = document.createElement('input');
                input.type = 'range';
                input.classList.add('form-range');
                input.min = value.minimum;
                input.max = value.maximum;
                input.name = key;
                input.title = key;
                if (avatarEditorOptions[key] !== undefined) input.value = avatarEditorOptions[key]; else input.value = value.default;
                input.addEventListener('input', function () {
                    var current = value.default;
                    if (avatarEditorOptions[key] !== undefined) current = avatarEditorOptions[key];
                    previewImage.style.transform = `${key}(${(input.value - current)}%)`;
                });
                input.addEventListener('change', function () {
                    previewImage.onload = function () {
                        previewImage.style.transform = null;
                        previewImage.onload = null;
                    }
                    avatarEditorOptions[key] = input.value;
                    setTransformOrigin();
                    updatePreviewImage(null);
                });
                const container = (key === "translateX" ? avatarOptionContainerTranslateX : avatarOptionContainerTranslateY);
                if(container !== undefined){
                    if(container.parentElement.children[1] !== container) {
                        input.setAttribute('orient', 'vertical');
                        // noinspection JSSuspiciousNameCombination
                        input.style.width = window.getComputedStyle(previewImage).height;
                    }
                    container.appendChild(input);
                }else{
                    avatarOptions.appendChild(input);
                }
            } else if (key === "rotate" && value.type === "integer") {
                const input = document.createElement('input');
                input.type = 'range';
                input.classList.add('form-range');
                input.min = value.minimum;
                input.max = value.maximum;
                input.name = key;
                input.title = key;
                if (avatarEditorOptions[key] !== undefined) input.value = avatarEditorOptions[key]; else input.value = value.default;
                input.addEventListener('input', function () {
                    var current = value.default;
                    if (avatarEditorOptions[key] !== undefined) current = avatarEditorOptions[key];
                    previewImage.style.transform = `${key}(${(input.value - current)}deg)`;
                });
                input.addEventListener('change', function () {
                    previewImage.onload = function () {
                        previewImage.style.transform = null;
                        previewImage.onload = null;
                    }
                    avatarEditorOptions[key] = input.value;
                    updatePreviewImage(null);
                });
                if(avatarOptionContainerRotate !== undefined){
                    if(avatarOptionContainerRotate.parentElement.children[1] !== avatarOptionContainerRotate) {
                        input.setAttribute('orient', 'vertical');
                        // noinspection JSSuspiciousNameCombination
                        input.style.width = window.getComputedStyle(previewImage).height;
                    }
                    avatarOptionContainerRotate.appendChild(input);
                }else{
                    avatarOptions.appendChild(input);
                }
            } else {
                // for all others
                switch (value.type) {
                    case "integer": {
                        if(!key.endsWith('Probability')) {
                            const inputGroup = document.createElement('div');
                            inputGroup.classList.add('input-group');
                            inputGroup.classList.add('mb-2');
                            const label = document.createElement('label');
                            label.classList.add('form-label');
                            label.setAttribute('for', `avatarOptionInput-${key}`);
                            label.innerText = valueHumanise(key);
                            inputGroup.appendChild(label);
                            const input = document.createElement('input');
                            input.type = 'range';
                            input.classList.add('form-range');
                            input.min = value.minimum;
                            input.max = value.maximum;
                            input.name = key;
                            input.title = key;
                            input.id = `avatarOptionInput-${key}`;
                            if (avatarEditorOptions[key] !== undefined) input.value = avatarEditorOptions[key]; else input.value = value.default;
                            input.addEventListener('change', function () {
                                avatarEditorOptions[key] = input.value;
                                updatePreviewImage(null);
                            });
                            inputGroup.appendChild(input);
                            avatarOptions.appendChild(inputGroup);
                            break;
                        }
                        if(schema.properties.hasOwnProperty(key.substring(0, key.indexOf('Probability')))){
                            probabilities[key.substring(0, key.indexOf('Probability'))] = {
                              probabilityKey: key,
                              probabilityValue: value
                            };
                            break;
                        }
                    }
                    case "boolean": {
                        const input = document.createElement('input');
                        input.type = 'checkbox';
                        input.classList.add('form-check-input');
                        input.name = key;
                        input.title = key;
                        if(value.type === "integer"){
                            if (avatarEditorOptions[key] !== undefined){
                                if(avatarEditorOptions[key] === value.minimum || avatarEditorOptions[key] === value.maximum)
                                    input.checked = avatarEditorOptions[key] === value.maximum;
                                else
                                    input.indeterminate = true;
                            }else{
                                if(value.default === value.minimum || value.default === value.maximum)
                                    input.checked = value.default === value.maximum;
                                else
                                    input.indeterminate = true;
                            }
                            input.addEventListener('change', function () {
                                avatarEditorOptions[key] = (input.checked ? value.maximum : value.minimum);
                                updatePreviewImage(null);
                            });
                        }else{
                            if (avatarEditorOptions[key] !== undefined) input.checked = avatarEditorOptions[key]; else input.checked = value.default;
                            input.addEventListener('change', function () {
                                avatarEditorOptions[key] = input.checked;
                                updatePreviewImage(null);
                            });
                        }
                        if(key === 'flip' && avatarOptionContainerFlip !== undefined)
                            avatarOptionContainerFlip.appendChild(input);
                        else
                            avatarOptions.appendChild(input);
                        break;
                    }
                    case "array": {
                        switch (value.items.type) {
                            case "string": {
                                if (value.items.pattern === "^(transparent|[a-fA-F0-9]{6})$") {
                                    const colorsContainer = document.createElement('div');
                                    colorsContainer.classList.add('form-group');
                                    colorsContainer.classList.add('p-2');
                                    const colorsLabel = document.createElement('label');
                                    colorsLabel.innerText = valueHumanise(key);
                                    colorsLabel.classList.add('d-block');
                                    colorsContainer.appendChild(colorsLabel);
                                    const value_list = value.default ?? ['ffffff', '000000'];
                                    const default_value = avatarEditorOptions[key] ?? "";
                                    const input_n = document.createElement('input');
                                    input_n.type = 'radio';
                                    input_n.classList.add('form-check-input');
                                    input_n.classList.add('color-selection');
                                    input_n.classList.add('me-3');
                                    input_n.name = key;
                                    input_n.value = '';
                                    input_n.checked = input_n.value === default_value;
                                    input_n.title = 'Randomise';
                                    $(input_n).on('input', function () {
                                        delete avatarEditorOptions[key];
                                        updatePreviewImage(null);
                                    });
                                    colorsContainer.appendChild(input_n);
                                    for (const v of value_list) {
                                        const input = document.createElement('input');
                                        input.type = 'radio';
                                        input.classList.add('form-check-input');
                                        input.classList.add('color-selection');
                                        input.classList.add('me-1');
                                        input.name = key;
                                        input.value = v;
                                        input.checked = input.value === default_value;
                                        input.title = `#${v}`;
                                        input.style.backgroundColor = `#${v}`;
                                        $(input).on('input', function () {
                                            avatarEditorOptions[key] = this.value;
                                            updatePreviewImage(null);
                                        });
                                        colorsContainer.appendChild(input);
                                    }
                                    const input_t = document.createElement('input');
                                    input_t.type = 'radio';
                                    input_t.classList.add('form-check-input');
                                    input_t.classList.add('color-selection');
                                    input_t.classList.add('ms-2');
                                    input_t.classList.add('me-1');
                                    input_t.name = key;
                                    input_t.value = 'transparent';
                                    input_t.checked = input_t.value === default_value;
                                    input_t.title = 'Transparent';
                                    $(input_t).on('input', function () {
                                        avatarEditorOptions[key] = this.value;
                                        updatePreviewImage(null);
                                    });
                                    colorsContainer.appendChild(input_t);
                                    const input_c = document.createElement('input');
                                    input_c.type = 'radio';
                                    input_c.classList.add('form-check-input');
                                    input_c.classList.add('color-selection');
                                    input_c.classList.add('custom-color');
                                    input_c.name = key;
                                    input_c.value = '000000';
                                    if (!(value_list.includes(default_value) || default_value === '' || default_value === 'transparent')) {
                                        input_c.value = default_value;
                                        input_c.checked = true;
                                    }
                                    input_c.title = 'Custom';
                                    $(input_c).on('input', function () {
                                        avatarEditorOptions[key] = this.value;
                                        updatePreviewImage(null);
                                    });
                                    colorsContainer.appendChild(input_c);
                                    const input_ch = document.createElement('input');
                                    input_ch.type = 'color';
                                    input_ch.style.opacity = input_ch.style.width = input_ch.style.height = input_ch.style.border = input_ch.style.padding = '0';
                                    input_ch.style.position = 'relative';
                                    input_ch.style.right = window.getComputedStyle(input_c).width;
                                    input_ch.style.top = `calc(${window.getComputedStyle(input_c).height} / 2)`;
                                    input_ch.value = input_c.value;
                                    input_ch.onchange = function(){
                                        if(input_c.value !== input_ch.value.replace('#', '')){
                                            input_c.value = input_ch.value.replace('#', '');
                                            avatarEditorOptions[key] = input_c.value;
                                            updatePreviewImage(null);
                                        }
                                    }
                                    input_c.onclick = function(){
                                        input_ch.click();
                                    }
                                    colorsContainer.appendChild(input_ch);
                                    avatarOptions.appendChild(colorsContainer);
                                    break;
                                }else if(value.items.enum !== undefined) {
                                    const inputGroup = document.createElement('div');
                                    inputGroup.classList.add('input-group');
                                    inputGroup.classList.add('mb-2');
                                    const label = document.createElement('label');
                                    label.classList.add('input-group-text');
                                    label.setAttribute('for', `avatarOptionInput-${key}`);
                                    label.innerText = valueHumanise(key);
                                    inputGroup.appendChild(label);
                                    const select = document.createElement('select');
                                    select.classList.add('form-select');
                                    select.name = key;
                                    select.title = valueHumanise(key);
                                    select.id = `avatarOptionInput-${key}`;
                                    const r = document.createElement('option');
                                    r.value = '<random>';
                                    r.innerText = '(randomise)';
                                    if(avatarEditorOptions[key] === undefined)
                                        r.selected = 'selected';
                                    select.appendChild(r);
                                    for(const v of value.items.enum){
                                        const o = document.createElement('option');
                                        o.value = v;
                                        o.innerText = valueHumanise(v);
                                        if(avatarEditorOptions[key] === v)
                                            o.selected = 'selected';
                                        select.appendChild(o);
                                    }
                                    inputGroup.appendChild(select);
                                    avatarOptions.appendChild(inputGroup);
                                    if(value.items.enum.length <= 1){
                                        inputGroup.style.display = 'none';
                                    }else{
                                        $(select).select2({
                                            dropdownParent: avatarEditorModalElement,
                                            theme: 'bootstrap-5'
                                        });
                                    }
                                    $(select).on('change', function(){
                                        if(select.value === '<none>')
                                            avatarEditorOptions[probabilities[key].probabilityKey] = probabilities[key].probabilityValue.minimum;
                                        else if(select.value === '<random>'){
                                            if(probabilities[key] !== undefined)
                                                avatarEditorOptions[probabilities[key].probabilityKey] = probabilities[key].probabilityValue.default;
                                            delete avatarEditorOptions[key];
                                        }
                                        else{
                                            if(probabilities[key] !== undefined)
                                                avatarEditorOptions[probabilities[key].probabilityKey] = probabilities[key].probabilityValue.maximum;
                                            avatarEditorOptions[key] = select.value;
                                        }
                                        updatePreviewImage(null);
                                    });
                                    if (avatarEditorOptions[key] !== undefined){
                                        select.value = avatarEditorOptions[key];
                                        $(select).trigger('change');
                                    }
                                }else{
                                    console.warn(`[AvatarEditor] Unable to process property "${key}" with unknown array item format`);
                                }
                                break;
                            }
                            default:
                                console.warn(`[AvatarEditor] Unable to process property "${key}" with unknown array item type "${value.items.type}"`);
                        }
                        break;
                    }
                    default:
                        console.warn(`[AvatarEditor] Unable to process property "${key}" with unknown type "${value.type}"`);
                }
            }
        }
        for (const [key, p] of Object.entries(probabilities)){
            const propElement = avatarOptions.querySelector(`select[name=${key}]`);
            if(propElement === undefined){
                console.warn(`[AvatarEditor] Could not find property "${key}" for probability`);
                continue;
            }
            const newOption = document.createElement('option');
            newOption.value = '<none>';
            newOption.innerText = 'None';
            if(avatarEditorOptions[p.probabilityKey] === p.probabilityValue.minimum)
                newOption.selected = 'selected';
            propElement.insertBefore(newOption, propElement.firstChild);
        }
    }

    function updatePreviewImage(e) {
        var optionsString = Object.entries(avatarEditorOptions)
            .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
            .join('&');
        previewImage.setAttribute('src', `https://api.dicebear.com/7.x/${selectElement.value}/svg?seed=${$(randomButton).data('seed')}&${optionsString}`);
    }

    function updateStylePreview(e) {
        updatePreviewImage(e);
        var selectedStyle = $(selectElement.options[selectElement.selectedIndex]);
        avatarStyleLicenseText.innerHTML = `Based on
<a href="${selectedStyle.data('source')}">${selectedStyle.data('title').split(' by')[0].split(' -')[0]}</a>
by <a href="${selectedStyle.data('homepage')}">${selectedStyle.data('creator').split(' by')[0].split(' -')[0]}</a>`;
        if (!selectedStyle.data('license-name').toLowerCase().startsWith('free')) {
            avatarStyleLicenseText.innerHTML += ` under license <a href="${selectedStyle.data('license-url')}">${selectedStyle.data('license-name')}</a>`;
        }
        avatarStyleLicenseText.innerHTML += '.';
        updateAvatarOptions(selectedStyle.val());
    }

    $(selectElement).on('change', updateStylePreview);
    $(randomButton).on('click', function () {
        $(randomButton).data('seed', Math.floor(Math.random() * 0xffffffff).toString(16) + Math.floor(Math.random() * 0xffffffff).toString(16));
        updatePreviewImage(null);
    });

    $('#avatarEditorSave').on('click', function () {
        avatarForm.elements['style'].value = selectElement.value;
        avatarForm.elements['seed'].value = $(randomButton).data('seed');
        avatarForm.elements['options'].value = JSON.stringify(avatarEditorOptions);
        avatarForm.requestSubmit();
    });

    setTransformOrigin();
    updateStylePreview();
});