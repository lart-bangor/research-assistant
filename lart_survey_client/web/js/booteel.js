/**
 * Expose bootstrap functionality to Python eel.
 * 
 * This script will expose some of the bootstrap functionality to Python's Eel
 * module. It should be loaded after bootstrap and eel's own JavaScript modules.
 */

// Define booteel as static namespace
let booteel = {}

booteel.logger = {
    level: {
        CRITICAL: 50,
        ERROR: 40,
        WARNING: 30,
        INFO: 20,
        DEBUG: 10,
        NOTSET: 0,
    }
}

booteel.logger.pylog = function (level, message, ...args) {
    for (let i = 0; i < args.length; i++) {
        args[i] = args[i].toString();
    }
    eel._booteel_log(level, message, args)();
}

booteel.logger.debug = function (message, ...args) {
    console.debug(message, ...args);
    booteel.logger.pylog(booteel.logger.level.DEBUG, message, ...args);
}

booteel.logger.info = function (message, ...args) {
    console.info(message, ...args);
    booteel.logger.pylog(booteel.logger.level.INFO, message, ...args);
}

booteel.logger.warning = function (message, ...args) {
    console.warn(message, ...args);
    booteel.logger.pylog(booteel.logger.level.WARNING, message, ...args);
}

booteel.logger.error = function (message, ...args) {
    console.error(message, ...args);
    booteel.logger.pylog(booteel.logger.level.ERROR, message, ...args);
}

booteel.logger.critical = function (message, ...args) {
    console.error(message, ...args);  // There is no more severe level in JS, so use error again.
    booteel.logger.pylog(booteel.logger.level.CRITICAL, message, ...args);
}

// Log booteel.js load - cannot be done earlier due to programatic definitions
booteel.logger.debug("booteel.js loaded.")

/**
 * Modal response callbacks.
 * 
 * A callback that handles a user response on a modal dialog.
 * 
 * @callback booteel.modalResponseCB
 * @param {string} modal_id - The HTML/DOM id of the modal (can be used to obtain the
 *                            modal instance from bootstrap if desired).
 * @param {string} choice - The user's choice from the set of options on the modal.
 */

/**
 * Launch a dismissable modal in bootstrap to alert the user to something.
 * 
 * Currently no action is taken based on the choice where several options are provided. When
 * the user makes a choice a callback is triggered and can the event can be handled in line
 * with the choice made by the user.
 * 
 * A dismissable modal will always have at least one choice "dismiss" available. All other
 * choices are defined by the *options* parameter. The default is one button, with the choice
 * "ok" and the label "OK".
 * 
 * @todo: There is currently a 'bug' where dismissable modals that are dismissed with the ESC
 * key do not trigger a callback.
 * 
 * @param {string} title - A title for the modal (may contain HTML).
 * @param {string} body - A body (e.g. message) for the modal (may contain HTML).
 * @param {object} options - A dictionary of key-value pairs, where key is a choice and the
 *                           value is a label for an associated button. The choice will be
 *                           returned as one of the arguments to the callback, if given.
 * @param {string} primary - The key from *options* which should be highlighted and focused
 *                           as the primary button.
 * @param {bool} dismissable - Whether the modal should be dismissable (via 'X' or clicking
 *                             outside of the modal) or not. Default 'true'.
 * @param {booteel.modalResponseCB} callback - A callback function to be called when the user
 *                                             responds to the modal. The callback function
 *                                             will be passed the modal's ID and the label of
 *                                             the choice picked by the user.
 */
booteel.modal = function (title, body, options = { ok: 'OK' }, primary = 'ok', dismissable = true, callback = null) {
    booteel.logger.debug("Creating new modal with parameters:", title, body, options);

    // Generate an id for the modal, avoiding collisions of existing IDs
    booteel.logger.debug("Determining modal_id..");
    const stripped_title = title.replace(/\W/g, '')
    let modal_base = stripped_title;
    let counter = 0;
    while (document.getElementById(modal_base + "-modal") != null) {
        counter++;
        modal_base = stripped_title + counter.toString();
    }
    const modal_id = modal_base + "-modal";
    booteel.logger.debug(`Determined modal_id: ${modal_id}.`);


    // Set modal title and body (plain copies, allows HTML injection)
    booteel.logger.debug("Generating modal HTML...")
    const modal_title = title;
    const modal_body = body;

    // Generate buttons
    const buttons = [];
    for ([key, value] of Object.entries(options)) {
        // Determine button label and type
        const btn_type = (key === primary) ? 'btn-primary' : 'btn-secondary';
        const btn_label = value;
        buttons.push(`<button type="button" class="btn ${btn_type}" onclick="booteel.handleModal('${modal_id}', '${key}', ${callback});">${btn_label}</button>`);
    }
    const modal_buttons = buttons.join("\n");

    // Generate dismiss button if appropriate
    let dismiss_button = '';
    if (dismissable === true) {
        dismiss_button = `<button type="button" class="btn-close" onclick="booteel.handleModal('${modal_id}', 'dismiss', ${callback});" aria-label="Dismiss"></button>`;
    }

    //Build the HTML for the modal
    const modal_html = `      <div class="modal fade" id="${modal_id}" tabindex="-1" aria-labelledby="${modal_id}-label" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="${modal_id}-label">${modal_title}</h5>
                    ${dismiss_button}
                </div>
                <div class="modal-body">
                    ${modal_body}
                </div>
                <div class="modal-footer">
                    ${modal_buttons}
                </div>
                </div>
            </div>
        </div>`;

    // Append the HTML to the bottom of the the document's body
    booteel.logger.debug("Injecting modal with HTML:", modal_html);
    const div = document.createElement('div');
    div.innerHTML = modal_html;
    document.body.appendChild(div);

    // Launch the modal
    booteel.logger.debug(`Launching modal '${modal_id}'.`)
    const modal = new bootstrap.Modal(document.getElementById(modal_id), { backdrop: 'static', keyboard: dismissable });
    modal.show();
    return modal_id;
}
eel.expose(booteel.modal, "_booteel_modal");

booteel.handleModal = async function (modal_id, choice, callback = null) {
    booteel.logger.debug(`Modal response for '${modal_id}' received: ${choice}`)
    const modal = bootstrap.Modal.getInstance(document.getElementById(modal_id));
    modal.hide()
    if (callback === null) {
        result = await eel._booteel_handlemodal(modal_id, choice)();
        booteel.logger.debug(`Modal choice '${choice}' on '${modal_id}' handled in Python with result: ${result}.`)
    } else {
        result = await callback(modal_id, choice);
        booteel.logger.debug(`Modal choice '${choice}' on '${modal_id}' handled in JavaScript with result: ${result}.`)
    }
    if (result) {
        modal.dispose();
        booteel.logger.debug(`Modal disposed: '${modal_id}'.`);
    }
    return result;
}