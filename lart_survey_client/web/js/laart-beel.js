/**
 * Expose bootstrap functionality to Python eel.
 * 
 * This script will expose some of the bootstrap functionality to Python's Eel
 * module. It should be loaded after bootstrap and eel's own JavaScript modules.
 */


eel.expose(bootstrap_modal);
/**
 * Launch a dismissable modal in bootstrap to alert the user to something.
 * 
 * Currently no action is taken based on the choice where several options are provided,
 * but this could be usefully expanded in the future (requiring an async / await implementation
 * on the bootstrap interface or something similar) to have a way to return the choice to
 * the user (and even make the modal non-dismissable).
 * 
 * @param {string} title - A title for the modal (may contain HTML).
 * @param {string} body - A body (e.g. message) for the modal (may contain HTML).
 * @param {object} options - A dictionary of key-value pairs, where key is a specific function and
 *                           value is either a label, or a 2-member array of a label and the keyword
 *                           'primary' or 'secondary' to mark a button as such (default 'secondary').
 */
function bootstrap_modal(title, body, options = {'close': ['Close', 'primary']}) {
    // Generate an id for the modal, avoiding collisions of existing IDs
    const stripped_title = title.replace(/\W/g, '')
    let modal_id = stripped_title;
    let counter = 0;
    while(!document.getElementById(modal_id)) {
        counter++;
        modal_id = stripped_title + counter.toString();
    }

    // Set modal title and body (plain copies, allows HTML injection)
    const modal_title = title;
    const modal_body = body;

    // Generate buttons
    const buttons = [];
    let modal_close_label = 'Close'; // Default if no 'close' option specified
    for([key, value] in Object.entries(options)) {
        // Determine button label and type
        let btn_type = 'btn-secondary';
        let btn_label = '';
        if(Array.isArray(value)) {
            btn_label = value[0];
            if(value[1] == 'primary') {
                btn_type = 'btn-primary';
            }
        } else {
            btn_label = value;
        }
        // Close buttons should dismiss, others may do something else (TODO)
        if(key === 'close') {
            buttons.push(`<button type="button" class="btn ${btn_type}" data-bs-dismiss="modal">${btn_label}</button>`);
            modal_close_label = btn_label;
        } else {
            // Currently all buttons are dismissing, this should be implemented later with some type of callback or similar..
            buttons.push(`<button type="button" class="btn ${btn_type}" data-bs-dismiss="modal">${btn_label}</button>`);
            // buttons.push(`<button type="button" class="btn ${btn_type}">${btn_label}</button>`);
        }
    }
    const modal_buttons = buttons.join("\n");

    //Build the HTML for the modal
    const modal_html = `      <div class="modal fade" id="${modal_id}-modal" tabindex="-1" aria-labelledby="${modal_id}-modal-label" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="${modal_id}-modal-label">${modal_title}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="${modal_close_label}"></button>
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
    const tmp_div = document.createElement('div');
    tmp_div.innerHTML = modal_html;
    document.body.appendChild(tmp_div.firstChild);
}