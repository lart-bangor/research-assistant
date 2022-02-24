booteel.logger.debug("lart.js loaded.");

let lart = {}

lart.forms = {}

lart.forms.searchParams = new URLSearchParams(window.location.search)

lart.forms.util = {}

lart.forms.util.getSelectValues = function (selectNode) {
    values = []
    for(const option of selectNode.selectedOptions) {
        values.push(option.value);
    }
    return values;
}

lart.forms.util.getFormFieldValue = function(fieldNode) {
    if ( fieldNode instanceof HTMLInputElement ) {
        if(['radio', 'checkbox'].includes(fieldNode.type) ) {
            if( fieldNode.checked ) {
                return fieldNode.value;
            }
        } else {
            return fieldNode.value;
        }
    } else if( fieldNode instanceof HTMLSelectElement ) {
        values = lart.forms.util.getSelectValues(fieldNode);
        switch(values.length) {
            case 0:
                return null;
            case 1:
                return values[0];
            default:
                return values;
        }
    } else if ( 'value' in fieldNode ) {
        return fieldNode.value;
    }
    return null;
}



lart.forms.util.inputConditionMatcher = function (nodes, comparisonValue, condition) {
    if( nodes instanceof NodeList && nodes.length > 1 ) {
        return function () {
            const testValues = [];
            for(const node of nodes) {
                testValues.concat(lart.forms.util.getFormFieldValue(node));
            }
            switch(condition) {
                case 'equal':
                    return (testValues.includes(comparisonValue));
                case 'not-equal':
                    return (!testValues.includes(comparisonValue));
                case 'smaller':
                    for(const testValue of testValues) {
                        if( parseInt(testValue) < parseInt(comparisonValue) ) {
                            return true;
                        }
                    }
                    return false;
                case 'greater':
                    for(const testValue of testValues) {
                        if( parseInt(testValue) > parseInt(comparisonValue) ) {
                            return true;
                        }
                    }
                    return false;
                case 'match':
                    for(const testValue of testValues) {
                        if( testValue.match(comparisonValue) ) {
                            return true;
                        }
                    }
                    return false;
            }
            return null;
        }
    }
    if ( nodes instanceof NodeList && nodes.length == 1 ) {
        nodes = nodes[0];
    }
    if( nodes instanceof HTMLElement ) {
        return function () {
            const testValue = lart.forms.util.getFormFieldValue(nodes);
            switch(condition) {
                case 'equal':
                    return (testValue == comparisonValue);
                case 'not-equal':
                    return (testValue != comparisonValue);
                case 'smaller':
                    return parseInt(testValue) < parseInt(comparisonValue);
                case 'greater':
                    return parseInt(testValue) > parseInt(comparisonValue);
                case 'match':
                    if( testValue.match(comparisonValue) ) {
                            return true;
                    }
                    return false;
            }
            return null;
        }
    }
    return null;
}

lart.forms.conditionalRequire = function (fieldName, targetId, value, condition = 'equal') {
    const collection = document.getElementsByName(fieldName);
    const target = document.getElementById(targetId);
    // Multiselect elements (radio, checkbox, select(?))
    for(const node of collection) {
        const matchesCondition = lart.forms.util.inputConditionMatcher(node, value, condition);
        node.addEventListener('input',
            function (event) {
                if(matchesCondition()) {
                    target.required = true;
                } else {
                    target.required = false;
                }
            }
        );
    }
}
lart.forms.conditionalDisplay = function (fieldName, targetId, value, condition = 'equal') {
    const collection = document.getElementsByName(fieldName);
    const target = document.getElementById(targetId);
    // Multiselect elements (radio, checkbox, select(?))
    for(const node of collection) {
        const matchesCondition = lart.forms.util.inputConditionMatcher(node, value, condition);
        target.classList.add("invisible")
        target.classList.add("collapse");
        node.addEventListener('input',
            function (event) {
                if(matchesCondition()) {
                    target.classList.remove("invisible");
                    target.classList.add("show");
                } else {
                    setTimeout(function () { target.classList.add("invisible") }, 100);
                    target.classList.remove("show");
                }
            }
        );
    }
}

lart.forms.repeatBlocks = {}

lart.forms.repeatBlock = function(containerId, pattern) {
    const root = document.getElementById(containerId);
    let code = root.firstElementChild.outerHTML;
    if (containerId in lart.forms.repeatBlocks) {
        lart.forms.repeatBlocks[containerId]++;
    } else {
        lart.forms.repeatBlocks[containerId] = parseInt(code.matchAll(pattern).next().value[2]);
        if(typeof(lart.forms.repeatBlocks[containerId]) != 'number') {
            lart.forms.repeatBlocks[containerId] = 0;
        }
    }
    n = lart.forms.repeatBlocks[containerId];
    code = code.replaceAll(pattern, `$1-${n}`);
    root.insertAdjacentHTML('beforeend', code);    
}

/**
 * Require all forms marked .needs-validation to pass client-side validation before submitting.
 * 
 * This function will register an event on all forms with the CSS class .needs-validation to prevent
 * submission if there are invalid fields according to the JavaScript Validation API. Forms will be marked
 * by adding the class .was-validated after the first attempt to submit, which will enable Bootstrap to
 * show custom user feedback messages. If the option novalidate is set to true (default false) then the
 * function will automatically set the attribute 'novalidate' on all the forms it attaches to. This is
 * needed to display Bootstrap form validation feedback instead of the browser's built-in feedback.
 * 
 * @param {bool} novalidate - Whether to mark affected forms 'novalidate' to suppress browsers' built-in feedback.
 */
lart.forms.requireValidation = function (novalidate = false) {
    // Fetch all the forms that need validation
    const forms = document.querySelectorAll('.needs-validation');
    booteel.logger.debug(`Setting up form validation listener on ${forms.length} forms:`, forms);

    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
        .forEach(
            function (form) {
                if (novalidate) {
                    console.debug(`Setting form ${form.id} to novalidate.`);
                    form.setAttribute('novalidate', true);
                }
                console.debug(`Adding 'submit' event listener to ${form.id}.`);
                form.addEventListener(
                    'submit',
                    function (event) {
                        if (!form.checkValidity()) {
                            console.debug(`Form ${form.id} has failed validation.`);
                            event.preventDefault();
                            event.stopPropagation();
                        } else {
                            console.debug(`Form ${form.id} has passed validation.`);
                        }
                        form.classList.add('was-validated');
                    },
                    false
                )
            }
        )
}

/**
 * Register a pipeline to submit a form's data to a JavaScript function instead of a HTTP request.
 * 
 * Registers an event handler on the form specified by `form_id` so that the data inside the form
 * will be piped to the function specified by `receiver` and the further propagation of the
 * submission event will be halted. Thus, no HTTP request will be issued and the page with the
 * form won't advance to the specified target or reload; if this is desired then the receiver of the
 * data should manually direct the user to the new page.
 * 
 * Data will only be piped to the receiver if the form passes client-side validation via the JavaScript
 * validation API. If you intend to also register a custom function to the submit event of the form to
 * validate (e.g. `requireValidation`), then you should register the validation function *before*
 * registering the pipeline, so that a failure to pipe an invalid form won't block the validation
 * function callback.
 * 
 * Normally the function as written here will be used to pipe data to a function exposed via Python's
 * eel module (marked @eel.expose in Python) via a JS wrapper, but it could of course also be used in
 * other scenarios where it is desirable to simply process the submitted data client-side in JS.
 * 
 * @param {string} form_id 
 * @param {CallableFunction} receiver 
 */
lart.forms.registerPipeline = function (form_id, receiver) {
    const form = document.getElementById(form_id);
    if (form) {
        form.addEventListener(
            'submit',
            function (event) {
                lart.forms.pipeData(event, receiver);
            },
            false
        )
        booteel.logger.debug(`Registered form pipeline from form '${form_id}' to callback:`, receiver)
    } else {
        booteel.logger.debug(`Failed to register form pipeline. No form with id '${form_id}'.`)
    }
}

/**
 * Form submission event callback to validate a form and pipe data to another function.
 * 
 * @param {Event} event - An event (typically 'submit') on a form element, e.g. as issued by .addEventListener().
 * @param {CallableFunction} receiver - A callable to which the form data will be passed as a dictionary.
 * @returns {bool} - Returns `true` if the receiver function returns a truthy value, false if validation fails or the receiver
 *                   function returns a falsy value.
 */
lart.forms.pipeData = function (event, receiver) {
    // Retrieve form element
    const form = event.currentTarget;

    // Stop forms whose data is sent to a receiver from actually submitting via an http request
    event.preventDefault();
    event.stopPropagation();

    // Check that client-side validation of form has succeeded
    if (!form.checkValidity()) {
        return false;
    }

    // Get form data and pipe it to the receiver
    const data = lart.forms.getData(form);
    if (receiver(data)) {
        return true;
    }
    return false;
}

/**
 * Assemble all data from a specified form into a dictionary of key-value pairs.
 * 
 * @param {*} form - A form element to extract data from.
 * @returns {object} - Returns a dictionary of key-value pairs, where key is the name (or id as fallback) and value the
 *                     value of each data field within the specified form.
 */
lart.forms.getData = function (form) {
    const data = {};
    const target_elements = ["input", "textarea", "select", "datalist"];
    const selector = "#" + form.id + " " + target_elements.join(", #" + form.id + " ");
    const fields = document.querySelectorAll(selector);
    for (const field of fields) {
        let ref = '';
        if (field.hasAttribute("name")) {
            ref = field.getAttribute("name");
        } else {
            ref = field.id;
        }
        // Convert checkboxes to booleans
        if (field.getAttribute("type") === "checkbox") {
            if (field.value === "on") {
                data[ref] = true;
            } else {
                data[ref] = false;
            }
        } else {
            data[ref] = field.value;
        }
    }
    return data;
}