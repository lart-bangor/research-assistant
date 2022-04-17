booteel.logger.debug("lsbq-rml.js loaded.");

/**
 * Namespace object for LSBQ-RML specific functionality.
 */
let lsbqRml = {};

/**
 * Namespace object for LSBQ-RML instance information.
 */
lsbqRml.instance = {};

/**
 * Retrieve the instance id of the current LSBQ-RML instance (if specified via search parameter).
 * 
 * @returns {str} - The integer version id, or null of not specified.
 */
lsbqRml.instance.getId = function() {
    if ("_instanceId" in lsbqRml.instance) {
        return lsbqRml.instance._instanceId;
    }
    instanceId = lart.forms.searchParams.get('instance');
    if (lart.forms.util.isUUID(instanceId)) {
        lsbqRml.instance._instanceId = instanceId;
        return instanceId;
    }
    lsbqRml.instance._versionId = null;
    return null;
}

/**
 * Namespace object for LSBQ-RML version-translation functionality.
 */
lsbqRml.tr = {};

/**
 * Associative array holding translation identifiers and translations.
 */
lsbqRml.tr.strings = {};

/**
 * Associative array of trId's and innerHTML for missing translation items.
 */
lsbqRml.tr.missing = {};

lsbqRml.tr.getMissing = function() {
    buf = {}
    for (trId in lsbqRml.tr.missing) {
        [key, subkey] = trId.split(".", 2);
        if (key in buf) {
            buf[key][subkey] = [lsbqRml.tr.missing[trId]];
        } else {
            buf[key] = {};
            buf[key][subkey] = [lsbqRml.tr.missing[trId]];
        }
    }
    return JSON.stringify(buf, null, 4);
}

/**
 * Get a translation string by its trId.
 * 
 * @param {string} trId - The translation identifier string.
 * @returns {string} - The translated string for the identifier, or null if no string for the
 *                     trId could be found.
 */
lsbqRml.tr.get = function(trId) {
    [key, subkey] = trId.split(".", 2);
    booteel.logger.debug(`Fetching translation string with trId '${trId}' ['${key}', '${subkey}'].`);
    if (key in lsbqRml.tr.strings && subkey in lsbqRml.tr.strings[key]) {
        tr = lsbqRml.tr.strings[key][subkey];
        if (tr instanceof Array && tr.length < 3) {
            if (tr.length > 1) {
                return tr[1];
            }
            return tr[0];
        }
        return tr;
    }
    if (!(trId in lsbqRml.tr.missing)) {
        lsbqRml.tr.missing[trId] = "???";
    }
    booteel.logger.debug(`No translation with trId '${trId}' found.`);
    return null;
}

/**
 * Load translation/adaptation strings for a specific LSBQ-RML version.
 * 
 * @param {string} instanceId - The LSBQ-RML instance identifier for which translation strings
 *                             should be loaded.
 * @param {array} sections - A list of sections for which the strings should be loaded. Note
 *                           that 'base' and 'meta' are always added, even if not specified.
 */
lsbqRml.tr.load = function(instanceId, sections) {
    sections.push('meta');
    sections.push('base');
    booteel.logger.debug(`Loading translation strings for instance '${instanceId}' with keys `, sections);
    eel._lsbqrml_load_version(instanceId, sections)(lsbqRml.tr._addStrings);
}

/**
 * Add translation strings from array to `lsbqRml.tr.strings`.
 * 
 * @param {object} strings - An associative array with translation strings labelled
 *                           by section. Each section contains an associative array
 *                           with a translation-string id, and a list of [1] the
 *                           original untranslated string, and [2] the version-specific
 *                           translation/adaptation.
 */
 lsbqRml.tr._addStrings = function(strings) {
    for (key in strings) {
        if (key in lsbqRml.tr.strings) {
            for (subkey in strings[key]) {
                lsbqRml.tr.strings[key][subkey] = strings[key][subkey];
            }
        } else {
            lsbqRml.tr.strings[key] = strings[key];
        }
    }
    booteel.logger.debug('Loaded translation strings:', lsbqRml.tr.strings);
    lsbqRml.tr._activateObservers();
}

/**
 * List of Node Id's that should be observed for string translation after loading strings.
 */
lsbqRml.tr.observerQueue = [];

/**
 * List of Node Id's that are being actively observed for string translation.
 */
lsbqRml.tr.activeObservers = [];

/**
 * Register a Node for translation observation by Id.
 * 
 * @param {*} nodeId - The Id of the Node to be observed.
 */
lsbqRml.tr.registerObserver = function(nodeId) {
    booteel.logger.debug(`Registering translation observer for node with id #${nodeId}.`);
    if ("meta" in lsbqRml.tr.strings) {
        lsbqRml.tr.observe(nodeId);
    } else {
        if (!lsbqRml.tr.observerQueue.includes(nodeId)) {
            lsbqRml.tr.observerQueue.push(nodeId);
        }
    }
}

/**
 * Activate translation observers currently held in the queue.
 * 
 * Cycles through queued Node Id's for translation observation. If the
 * translation strings have been loaded already cycles through the nodes
 * to translate them and then registers a MutationObserver on the node
 * to monitor for changes. If translation strings are not available yet
 * a timeout is set for 100ms, and translation and observer registration
 * is done once the translation strings have been loaded.
 * 
 * @returns {null}
 */
lsbqRml.tr._activateObservers = function() {
    booteel.logger.debug('Activating queued translation observers...');
    if (!("meta" in lsbqRml.tr.strings)) {
        booteel.logger.debug('Translation strings not loaded yet, trying again in 100ms.')
        setTimeout(lsbqRml.tr._activateObservers, 100); // Try again in 100ms
        return;
    }
    while (nodeId = lsbqRml.tr.observerQueue.pop()) {
        booteel.logger.debug(`Activating observer for Node with id #${nodeId}.`);
        node = document.getElementById(nodeId);
        if (!node) {
            booteel.logger.error(`Could not retreive node with id #${nodeId}.`);
            continue;
        }
        lsbqRml.tr._translateNode(node);
        if (!(lsbqRml.tr.activeObservers.includes(nodeId))) {
            const observer = new MutationObserver(
                function (mutationList, observer) {
                    for (const mutation of mutationList) {
                        if ( mutation.target instanceof HTMLElement ) {
                            lsbqRml.tr._translateNode(mutation.target);
                        }
                    }
                }
            );
            observer.observe(
                node,
                {
                    subtree: true,
                    childList: true,
                    attributeFilter: ['data-lsbq-tr']
                }
            );
            lsbqRml.tr.activeObservers.push(nodeId);
        }
    }
}

/**
 * Traverse through a DOM Node and translate all applicable HTMLElements.
 * 
 * @param {Node} node - A DOM Node to be traversed and translated. 
 */
lsbqRml.tr._translateNode = function(node) {
    booteel.logger.debug('Translating node:', node);
    lsbqRml.tr._translateElement(node);
    translatables = node.querySelectorAll("[data-lsbq-tr]");
    for (translatable of translatables) {
        lsbqRml.tr._translateElement(translatable);
    }
}

/**
 * Check, and if applicable, substitute a HTMLElement's innerHTML with version-specific string.
 * 
 * @param {HTMLElement} element 
 */
lsbqRml.tr._translateElement = function(element) {
    if (element instanceof HTMLElement && "lsbqTr" in element.dataset) {
        booteel.logger.debug('Translating element:', element);
        const trId = element.dataset.lsbqTr;
        const trString = lsbqRml.tr.get(trId);
        if (trString) {
            element.innerHTML = trString;
            element.dataset.lsbqTrOrigin = trId;
            delete element.dataset.lsbqTr; // Avoid repeatedly targeting same string
        } else {
            lsbqRml.tr.missing[trId] = element.innerHTML;
        }
    } else {
        booteel.logger.debug('Skipping untranslatable element:', element);
    }
}

/**
 * Translate an attribute on one or more elements specified by their id.
 * 
 * @param {object} attrs - An associative array with Element Ids as key, and a two-member list
 *                         as values, where the first is the attribute name and the second the trId.
 * @returns {null}
 */
lsbqRml.tr.translateAttrs = function(attrs) {
    if("meta" in lsbqRml.tr.strings) {
        for (const elementId in attrs) {
            const element = document.getElementById(elementId);
            if (!element) {
                booteel.logger.error(`Could not retreive element with id #${elementId}.`);
                continue;
            }
            const trString = lsbqRml.tr.get(attrs[elementId][1]);
            if (trString) {
                element.setAttribute(attrs[elementId][0], trString);
            }
        }
        return;
    }
    setTimeout(lsbqRml.tr.translateAttrs, 250, attrs);
}