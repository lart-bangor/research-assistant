booteel.logger.debug("lart-forms.js loaded.");

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
function requireFormValidation(novalidate = false) {
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
 * validate (e.g. `requireFormValidation`), then you should register the validation function *before*
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
function registerFormPipeline(form_id, receiver) {
    const form = document.getElementById(form_id);
    if (form) {
        form.addEventListener(
            'submit',
            function (event) {
                pipeFormData(event, receiver);
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
function pipeFormData(event, receiver) {
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
    const data = getFormData(form);
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
function getFormData(form) {
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