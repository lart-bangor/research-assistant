/**
 * @file LART Research Client JavaScript Library.
 * 
 * This library implements interfaces and utility functions designed to simplify
 * common tasks for the LART Research Client frontend. It's designed to work
 * together with Python eel and booteel.js.
 * 
 * @author Florian Breit <f.breit@bangor.ac.uk>
 * @requires 'eel.js'
 * @requires 'booteel.js'
 */
'use strict';
booteel.logger.debug("lart.js loaded.");

/**
 * The LART Research Client JavaScript Library.
 * 
 * @namespace
 */
const lart = {};

//
// App Locking state management.
//

/**
 * App locking state management.
 * 
 * @namespace
 */
lart.appLock = {};

lart.appLock.switches = new Set();

lart.appLock.state = 'locked';

setTimeout(
    () => {
        if (sessionStorage.getItem('lart.appLock.state') === 'unlocked') {
            lart.appLock.unlock();
        } else {
            lart.appLock.lock();
        }
    }
);

lart.appLock.lock = function() {
    console.log("Locking app...")
    lart.appLock.state = 'locked';
    sessionStorage.setItem('lart.appLock.state', lart.appLock.state);
    for (const element of lart.appLock.switches) {
        lart.appLock._setSwitchState(element);
    }
    document.querySelector('html').addEventListener('contextmenu', lart.appLock._contextMenuHandler);
}

lart.appLock.unlock = function() {
    console.log("Unlocking app...")
    lart.appLock.state = 'unlocked';
    sessionStorage.setItem('lart.appLock.state', lart.appLock.state);
    for (const element of lart.appLock.switches) {
        lart.appLock._setSwitchState(element);
    }
    document.querySelector('html').removeEventListener('contextmenu', lart.appLock._contextMenuHandler);
}

lart.appLock._contextMenuHandler = function(event) {
    event.preventDefault();
}

lart.appLock.toggleState = function() {
    if (lart.appLock.state == 'locked') {
        lart.appLock.unlock();
    } else {
        lart.appLock.lock();
    }
}

lart.appLock.registerSwitch = function (switchElementOrId, eventType = 'click') {
    const element = lart.forms.getElementByGreed(switchElementOrId);
    lart.appLock.switches.add(element);
    element.addEventListener(
        'click',
        () => {
            lart.appLock.toggleState();
        }
    );
    lart.appLock._setSwitchState(element);
}

lart.appLock._setSwitchState = function(element) {
    if (lart.appLock.state == 'unlocked') {
        element.innerHTML = '<i class="bi bi-unlock"></i> Lock app';
    } else {
        element.innerHTML = '<i class="bi bi-lock"></i> Unlock app';
    }
}

//
// LART Utilities
//

/**
 * LART utilities.
 * 
 * @namespace
 */

lart.utils = {};

/**
 * Extract ISO 639-2 3-letter language code from a version string.
 * 
 * Given an input of the form "XxxYyy_Zzz_CC" where Xxx, Yyy, and Zzz are three-letter
 * ISO 639-2 language codes, and CC and country code, will return the string Zzz, which
 * is used in the LART app to identify the primary langauage of a test version.
 * 
 * @param {String} version - LART test version string of the form "XxxYyy_Zzz_CC".
 * @returns {String|null} Returns three letter language code representing the primary language
 *      of a LART test version, or null if the supplied string doesn't validly encode one.
 */
lart.utils.extractLanguageFromVersion = function (version) {
    const parts = version.split("_")
    if (parts.length > 1 && parts[1].length == 3) {
        return parts[1]
    }
    return null;
}

/**
 * Shortcut to the URLSearchParams for the current page.
 * 
 * @readonly
 * @type {URLSearchParams}
 * @see {@link https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams MDN Documentation for `URLSearchParams`}
 */
lart.utils.searchParams = new URLSearchParams(window.location.search);

/**
 * LART utilities for working with UUIDs.
 * 
 * @namespace
 */
lart.utils.UUID = {};

/**
 * RegEx pattern for identifying valid hex-format UUIDs.
 * 
 * @type {RegExp}
 */
lart.utils.UUID.pattern = /^[0-9a-f]{8}-?(?:[0-9a-f]{4}-?){3}[0-9a-f]{12}$/i;

/**
 * Nil UUID as hex-string with separators.
 * 
 * @readonly
 * @default
 * @type {String}
 */
lart.utils.UUID.nilUUID = '00000000-0000-0000-0000-000000000000';

/**
 * Nil UUID as hex-string without separators.
 * 
 * @readonly
 * @default
 * @type {String}
 */
lart.utils.UUID.plainNilUUID = '00000000000000000000000000000000';

/**
 * Check whether a string is a valid UUID in hex format.
 * 
 * @param {String} identifier 
 * @returns {Boolean} Boolean indicating whether the provided identifier is a valid
 *          hex-formated UUID or not, with or without separators.
 */
lart.utils.UUID.isUUID = function(identifier) {
    return lart.utils.UUID.pattern.test(identifier);
}

/**
 * Check whether a UUID in hex format is the Nil UUID.
 * 
 * @param {String} identifier 
 * @returns {Boolean} Boolean indicating whether the provided identifier is the *Nil
 *          UUID* (~UUID equivalent of *null*), with or without separators.
 */
lart.utils.UUID.isNilUUID = function(identifier) {
    return (identifier == lart.utils.UUID.nilUUID || identifier == lart.utils.UUID.plainNilUUID);
}

//
// LART Forms
//

/**
 * LART utilities for working with HTML forms.
 * 
 * @namespace
 */
lart.forms = {};

/**
 * Greedily and flexibly try to get an element from the DOM.
 * 
 * This function allows for the flexible retrieval of an element from the DOM.
 * It is primarily meant to be called inside other functions needing a reference
 * to an element and there facilitates a more flexible calling pattern to those
 * functions, allowing the element to be referenced either directly as a HTMLElement
 * or RadioNodeList, or by its `id` or `name` attribute.
 * 
 * The procedure followed to find an element is as follows:
 * - If the passed argument is a HTMLElement or RadioNodeList, return it unchanged.
 * - If the passed argument is a string:
 *      - If *root* implements *.getElementById*, call `root.getElementById(ref)` and return the
 *        HTMLElement, if any.
 *      - If *root* implements *.getElementsByName*, call `root.getElementsByName(ref)`.
 *        If the returned NodeList contains only HTMLInputElements of type radio which
 *        have both the same name and belong to the same HTMLForm (i.e. that form a radio
 *        group), then obtain the relevant RadioNodeList and return it.
 *        Otherwise, if the NodeList contains only a single HTMLElement, return it.
 *      - If *root* implements *.querySelector*, call `root.querySelector(ref)` and return the
 *        HTMLElement, if any. Note that this will be the *first* element inside *root* which
 *        satisfies the *ref* passed to *querySelector*.
 * - If no HTMLElement or RadioNodeList could be found following the above procedure, return `null`.
 * 
 * The *root* argument is optional, and can be either a {@link Document} root or a {@link HTMLElement}
 * node to be used as the root. Note that *HTMLElements* don't implement all the supported query methods
 * and will typically default to the {@link HTMLElement.querySelector} method. Where *root* is not
 * specified, it defaults to the global {@link document} object. The *root* is not used where the *ref*
 * argument already is a *HTMLElement* or *RadioNodeList*.
 * 
 * @param {(HTMLElement|RadioNodeList|String)} ref - A reference to the HTMLElement which should be
 *          obtained from the DOM. Can be either a JavaScript object directly representing it, or a
 *          string which identifies the element via its `id` or `name` attribute, or a string which
 *          identifies the element using the *querySelector* syntax. 
 * @param {(Document|HTMLElement)} [root=document] - A Document or HTMLElement to be used as the root
 *          for querying. Ignored if *ref* already is a HTMLElement or RadioNodeList.
 * @returns {(HTMLElement|RadioNodeList|null)}
 */
lart.forms.getElementByGreed = function (ref, root = null) {
    if (!root) {
        root = document;
    }
    // Just return argument if it already is an HTMLElement or RadioNodeList
    if (ref instanceof HTMLElement || ref instanceof RadioNodeList) {
        return ref;
    }
    let tmp = null;
    // Try to get element by id
    if('getElementById' in root) {
        tmp = root.getElementById(ref);
        if (tmp) {
            return tmp;
        }
    }
    // Try to get single element or RadioNodeList by name
    if('getElementsByName' in root) {
        tmp = root.getElementsByName(ref);
        if (tmp.length > 0 && tmp[0] instanceof HTMLInputElement && tmp[0].type == 'radio' && tmp[0].form) {
            const parentForm = tmp[0].form;
            let allCongruent = true;
            for (const node of tmp) {
                if (!(node instanceof HTMLInputElement) || node.type != 'radio' || node.form !== parentForm) {
                    allCongruent = false;
                    break;
                }
            }
            if (allCongruent) {
                return lart.forms.getRadioNodeList(tmp[0]);
            }
        }
        if (tmp.length == 1) {
            return tmp[0];
        }
    }
    // Try to get single element by querySelector
    if('querySelector' in root) {
        return root.querySelector(ref);
    }
    return null;
}

/**
 * A HTML form control element.
 * 
 * @see {@link lart.forms.HTMLFormControlElementTypes}
 * @see {@link lart.forms.isHTMLFormControlElement}
 * @typedef {(HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement|RadioNodeList|HTMLMeterElement|HTMLProgressElement|HTMLOutputElement)} HTMLFormControlElement
 */

/**
 * Set containing all the types recognised as {@link HTMLFormControlElement}.
 * 
 * @see {@link HTMLFormControlElement}
 * @see {@link lart.forms.isHTMLFormControlElement}
 * @readonly
 * @default
 * @type {Set}
 */
lart.forms.HTMLFormControlElementTypes = new Set([
    HTMLInputElement,
    HTMLSelectElement,
    HTMLTextAreaElement,
    RadioNodeList,
    HTMLMeterElement,
    HTMLProgressElement,
    HTMLOutputElement
]);

/**
 * Check whether an element is a {@link HTMLFormControlElement}.
 * 
 * @see {@link HTMLFormControlElement}
 * @see {@link lart.forms.HTMLFormControlElementTypes}
 * @param {Object} element - The object to be checked for implementation of a relevant prototype.
 * @returns {Boolean} Whether the object is a {@link lart.forms.HTMLFormControlElementTypes HTMLFormControlElement}
 */
lart.forms.isHTMLFormControlElement = function (element) {
    for (const controlElementType of lart.forms.HTMLFormControlElementTypes) {
        if (element instanceof controlElementType) {
            return true;
        }
    }
    return false;
}

/**
 * Obtain the selected option values of an HTMLSelectElement.
 * 
 * @param {(HTMLSelectElement|String)} selectElement The HTMLSelectElement whose values shall be optained,
 *          or a string with the HTMLSelectElement's id or name.
 * @returns {Array<String>} A list of values of all selected options inside the select element.
 */
lart.forms.getSelectValues = function (elementOrId) {
    const selectElement = lart.forms.getElementByGreed(elementOrId);
    if (!(selectElement instanceof HTMLSelectElement)) {
        booteel.logger.error("Cannot get select values on object that is not HTMLSelectElement:", elementOrId);
        throw new TypeError(
            `The passed argument elementOrId=${elementOrId} does not refer to a HTMLSelectElement, but ${selectElement}.`
        );
    }
    const values = []
    for(const option of selectElement.selectedOptions) {
        values.push(option.value);
    }
    return values;
}

/**
 * Obtain the value of an {@link HTMLFormControlElement}.
 * 
 * @param {HTMLFormControlElement} controlElement The form control element
 *          for which the value should be optained.
 * @returns {(String|Array<String>|null)} The value of the passed form control element, if any.
 */
lart.forms.getControlValue = function(elementOrId) {
    const controlElement = lart.forms.getElementByGreed(elementOrId);
    if (controlElement instanceof HTMLInputElement) {
        if(['radio', 'checkbox'].includes(controlElement.type) ) {
            if( controlElement.checked ) {
                return controlElement.value;
            }
        } else {
            return controlElement.value;
        }
    } else if( controlElement instanceof HTMLSelectElement ) {
        const values = lart.forms.getSelectValues(controlElement);
        switch(values.length) {
            case 0:
                return null;
            case 1:
                return values[0];
            default:
                return values;
        }
    } else if ( 'value' in controlElement ) {
        return controlElement.value;
    } else {
        booteel.logger.error("Attempted to obtain value from an non-HTMLFormControlElement:", controlElement);
        throw new TypeError(
            `The passed argument elementOrId=${elementOrId} does not refer to a HTMLFormControlElement, but ${controlElement}.`
        );
    }
}

/**
 * Enum of conditions for {@link lart.forms.conditionMatcherFactory}.
 * 
 * Five *condition* values are supported:
 *  - EQUAL is equivaluent to `actualValue == comparisonValue`.
 *  - NOT_EQUAL is equivalent to `actualValue != comparisonValue`.
 *  - SMALLER is equivalent to `actualValue < comparisonValue`.
 *  - GREATER is equivalent to `actualValue > comparisonValue`.
 *  - MATCH is equivalent to `actualValue.match(comparisonValue)`, where *comparisonValue* is a `RegExp`.
 * 
 * @readonly
 * @enum {String}
 */
lart.forms.conditionMatcherCondition = {
    /** Compare values with the `==` operator. */
    EQUAL: 'equal',
    /** Compare values with the `!=` operator. */
    NOT_EQUAL: 'not-equal',
    /** Compare values with the `<` operator. */
    SMALLER: 'smaller',
    /** Compare values with the `>` operator. */
    GREATER: 'greater',
    /** Compare values by calling the `.match()` method on the first value. */
    MATCH: 'match'
}

/**
 * Check whether a HTMLElement is a radio input control.
 * 
 * @param {HTMLElement} element - The Element to be checked.
 * @returns {Boolean} Whether the element is a HTMLInputElement of type 'radio'.
 */
lart.forms.isHTMLRadioInputElement = function(element) {
    return (element instanceof HTMLInputElement && element.type == 'radio');
}

/**
 * Get the RadioNodeList associated with a radio input control.
 * 
 * @param {HTMLInputElement} radioElement - The radio input control for which the RadioNodeList should be obtained.
 * @returns {RadioNodeList}
 * @throws {TypeError} Throws *TypeError* if the passed element is not a radio element, not attached to a form, or doesn't
 *          have a `name` attribute.
 */
lart.forms.getRadioNodeList = function (radioElement) {
    const name = radioElement.name;
    const form = radioElement.form;
    if (!name || !form || !lart.forms.isHTMLRadioInputElement(radioElement)) {
        booteel.logger.error('Attempted to obtain RadioNodeList on invalid or stray object:', radioElement);
        throw TypeError(
            `The provided argument ${radioElement} is either not a HTMLInputElement of type 'radio', missing the 'name' attribute, or is not attached to a HTMLFormElement.`
        );
    }
    return form.elements.namedItem(name);
}

/**
 * Get a pre-processed collection of a form's control elements.
 * 
 * Convenience function, which obtains a {@link HTMLFormElement}'s {@link HTMLFormControlElement HTMLFormControlElements}.
 * In contrast to a `HTMLFormControlsCollection`, this function returns a `Set` in which each control is only present
 * once, and where `HTMLInputElements` of type *radio* are represented by a `RadioNodeList`, rather
 * than the `HTMLInputElements` themselves. Further, `HTMLFieldSetElements` have been removed.
 * 
 * @param {(HTMLFormElement|String)} formOrId - The HTMLFormElement (or a string with it's `id` attribute)
 *          for which the HTMLFormControlCollection should be obtained.
 * @returns {Set<HTMLFormControlElement>}
 */
lart.forms.getFormControlElements = function (formOrId) {
    const formElement = lart.forms.getElementByGreed(formOrId);
    if( !(formElement instanceof HTMLFormElement) ) {
        booteel.logger.error("Attempted to obtain HTMLFormControlsCollection from non-HTMLFormElement:", formElement);
        throw new TypeError(
            `Passed argument formOrId=${formOrId} does not refer to a HTMLFormElement, but ${formElement}.`
        )
    }
    const rawControls = formElement.elements;
    const filteredControls = new Set();
    for (const control of rawControls) {
        if (control instanceof HTMLFieldSetElement) {
            // Skip HTMLFieldSetElements: their children are included in parent HTMLFormControlsCollections.
            continue;
        }
        if (lart.forms.isHTMLRadioInputElement(control)) {
            // Add the RadioNodeList instead of the Radio Control itself.
            filteredControls.add(lart.forms.getRadioNodeList(control));
            continue;
        }
        filteredControls.add(control);
    }
    return filteredControls;
}

/**
 * Condition matching function factory.
 * 
 * Generates a function which checks whether the value of one or more form fields (specified by
 * the *nodes* argument) evaluates to true or false compared to *comparisonValue* under *condition*.
 * 
 * *comparisonValue* should be a string or number for all *condition* types *except
 * {@linkcode lart.forms.conditionMatcherCondition.MATCH MATCH}*, for which a {@link RegExp} object
 * should be supplied. If the *condition* is `MATCH` and the *comparisonValue* is not a *RegExp*
 * object, it will be implicitly converted (i.e. `comparisonValue = RegExp(comparisonValue);`).
 * 
 * For the supported *condition* types, see {@link lart.forms.conditionMatcherCondition}.
 * 
 * Where *controls* is a HTMLForm or an iterable of more than a single HTMLElement, the functions is true
 * whenever *any* of the HTMLFormControlElement elements in *nodes* satisfy the test condition.
 * 
 * @param {(HTMLFormElement|HTMLFormControlElement|Array<HTMLFormControlElement>|Set<HTMLFormControlElement>|HTMLCollection|NodeList)} controls -
 *          The HTMLElement or NodeList of HTMLElement targets for which the generated function should check the provided condition.
 * @param {(String|Number|RegExp)} comparisonValue The value to which the target should be compared.
 * @param {lart.forms.conditionMatcherCondition} condition The type of condition to be applied in comparing
 *          the actual value of the node(s) to *comparisonValue*.
 * @returns {lart.forms.conditionMatcherFactory~conditionMatcher} A function which returns true when the condition is met,
 *          false otherwise.
 */

lart.forms.conditionMatcherFactory = function (controls, comparisonValue, condition) {
    // Make a set of the HTMLFormControlElements to be tested
    const testControls = new Set();
    if (controls instanceof HTMLFormElement) {
        controls = lart.forms.getFormControlElements(controls);
    } else if (controls instanceof Set || controls instanceof Array || controls instanceof HTMLCollection || controls instanceof NodeList) {
        for (const control of controls) {
            if (lart.forms.isHTMLFormControlElement(control)) {
                testControls.add(control);
            }
        }
    } else if (lart.forms.isHTMLFormControlElement(controls)) {
        testControls.add(controls);
    } else {
        booteel.logger.error("Attempted to make condition matcher on object that isn't a form control:", controls);
        throw new TypeError(
            `The provided argument controls=${controls} is not HTMLFormControlsCollection or HTMLFormControlElement.`
        );
    }

    // Pre-construct a function to test the condition on a Set of test-values
    if (condition == lart.forms.conditionMatcherCondition.MATCH && !(comparisonValue instanceof RegExp)) {
        comparisonValue = RegExp(comparisonValue);
    }
    let testCondition;
    switch (condition) {
        case lart.forms.conditionMatcherCondition.EQUAL:
            testCondition = function (testValues) {
                return testValues.has(comparisonValue);
            }
            break;
        case lart.forms.conditionMatcherCondition.NOT_EQUAL:
            testCondition = function (testValues) {
                return !testValues.has(comparisonValue);
            }
            break;
        case lart.forms.conditionMatcherCondition.SMALLER:
            testCondition = function (testValues) {
                for (const testValue of testValues) {
                    if( parseFloat(testValue) < parseFloat(comparisonValue) ) {
                        return true;
                    }
                }
                return false;
            }
            break;
        case lart.forms.conditionMatcherCondition.GREATER:
            testCondition = function (testValues) {
                for (const testValue of testValues) {
                    if( parseFloat(testValue) > parseFloat(comparisonValue) ) {
                        return true;
                    }
                }
                return false;
            }
            break;
        case lart.forms.conditionMatcherCondition.MATCH:
            testCondition = function (testValues) {
                for (const testValue of testValues) {
                    if( testValue.match(comparisonValue) ) {
                        return true;
                    }
                }
                return false;
            }
            break;
        default:
            booteel.logger.error("Attempted to construction conditionMatcher with unknown condition:", condition);
            throw new TypeError(
                `Passed argument condition=${condition} is not a valid conditionMatcherCondition.`
            );
    }

    // Build and return the conditionMatcher based on the pre-built testCondition() and the testControls.
    /**
     * Form control condition matcher.
     * 
     * A closure generated by {@link lart.forms.conditionMatcherFactory} which returns `true` whenever the
     * conditions specified on the *conditionMatcherFactory* are true for any of the
     * {@link HTMLFormControlElement HTMLFormControlElements} supplied to the *conditionMatcherFactory*,
     * `false` otherwise.
     * 
     * The returned closure function evaluates the truth across the set of controls each time it is called, meaning
     * it can be checked repeatedly to monitor whether the state of the controls has changes such that the condition's
     * truth has changed.
     * 
     * @inner
     * @returns {Boolean} Whether the condition is met on at least one of the form control elements or not.
     */
    function conditionMatcher() {
        // Collect the values to test against
        const testValues = new Set();
        for (const testElement of testControls) {
            testValues.add(lart.forms.getControlValue(testElement));
        }
        return testCondition(testValues);
    }
    return conditionMatcher;
}

/**
 * Auto-fill a form with data from the URL's query string/search params.
 * 
 * This function will wait for *delay* ms before attempting to fill all
 * HTMLInputElement, HTMLSelectElement, and HTMLTextAreaElement elements
 * attached to the HTMLForm specified by *formOrId*.
 * 
 * If the query string/search params include a field called `${formId}.submit`
 * (where *formId* is the HTMLFormElement's `id` attribute) and its value is
 * either the string `true` or `1`, then the wait again for *delay* ms before
 * simulating a click on the first HTMLElement with a `type="submit"` attribute
 * attached to the HTMLForm.
 * 
 * @param {(HTMLFormElement|String)} formOrId - A HTMLFormElement or a string which
 *          identifies a HTMLFormElement by its `id` attribute.
 * @param {Number} [delay=500] - The delay in milliseconds before autoFilling the form,
 *      and if applicable, again before submitting it.
 */
lart.forms.autoFill = function(formOrId, delay=500) {
    const form = lart.forms.getElementByGreed(formOrId);
    const fields = lart.forms.getFormControlElements(form);
    const submitButton = form.querySelector('*[type="submit"]');
    window.setTimeout(
        function () {
            for (const field of fields) {
                // Get the field's name (with fallback to id)
                let fieldName = '';
                if (field.hasAttribute('name' )) {
                    fieldName = field.name;
                } else if (field.hasAttribute('id') ) {
                    fieldName = field.id;
                } else {
                    continue;
                }
                // Obtain field value from search params
                const fieldValue = lart.forms.searchParams.get(fieldName);
                if (fieldValue === null) {
                    continue;
                }
                // Try to set field to value
                if( field instanceof HTMLSelectElement ) {
                    const targetOption = field.querySelector(`option[value="${fieldValue}"]`);
                    if (targetOption === null) {
                        continue;
                    }
                    field.value = fieldValue;
                } else if ( field instanceof HTMLTextAreaElement ) {
                    field.value = fieldValue;
                } else if ( field instanceof HTMLInputElement ) {
                    switch(field.type) {
                        case 'checkbox':
                            if( parseInt(fieldValue) ) {
                                field.checked = true;
                            } else {
                                field.checked = false;
                            }
                            break;
                        case 'range':
                        case 'number':
                            field.value = parseFloat(fieldValue);
                            break;
                        case 'text':
                        case 'password':
                        case 'search':
                        case 'email':
                        case 'tel':
                        case 'url':
                            field.value = fieldValue;
                            break;
                    }
                }
            }
            if ( ['true', '1'].includes(lart.forms.searchParams.get(`${form.id}.submit`)) && submitButton ) {
                window.setTimeout(
                    function () {
                        submitButton.click();
                    },
                    delay
                );
            }
        },
        delay
    );
}

/**
 * Conditionally require a form control depending on the value of a different control.
 * 
 * Observe and conditionally set the required attribute on a HTMLFieldControlElement depending on
 * the value of a different HTMLFieldControlElement.
 * 
 * @param {String} observedControlName - The name of the HTMLFormControlElement whose value shall be observed.
 * @param {String} targetControlName - The name of the HTMLFormControlElement which shall be conditionally required.
 * @param {String} value - The value of the observed field at which the target element shall be marked required.
 * @param {lart.forms.conditionMatcherCondition} condition - The condition used to compare *value* with the
 *          observed field's value.
 */
lart.forms.conditionalRequire = function (observedControlName, targetControlName, value, condition = lart.forms.conditionMatcherCondition.EQUAL) {
    const collection = document.getElementsByName(observedControlName);
    const targets = document.getElementsByName(targetControlName);
    booteel.logger.debug(`Adding conditional requirement: If ${observedControlName}.value ${condition}s ${value} -> require ${targetControlName}.`);
    booteel.logger.debug("    Observed controls:", collection);
    booteel.logger.debug("    Target control:", targets);
    // Multiselect elements (radio, checkbox, select(?))
    for(const node of collection) {
        booteel.logger.debug("    Adding condition matcher for control:", node);
        const matchesCondition = lart.forms.conditionMatcherFactory(node, value, condition);
        node.addEventListener(
            'input',
            (event) => {
                console.log(`Checking conditional require condition for ${observedControlName}...`);
                console.log('...input event evaluates to:', matchesCondition());
            }
        );
        node.addEventListener('input',
            function (event) {
                console.debug(`Checking conditional require condition for ${observedControlName}...`);
                if(matchesCondition()) {
                    for(const target of targets) {
                        console.debug(`Control ${target.name} now required.`);
                        target.required = true;
                    }
                } else {
                    for(const target of targets) {
                        console.debug(`Control ${target.name} now NOT required.`);
                        target.required = false;
                    }
                }
            }
        );
        // Trigger the input event now to get the setting consistent for default values
        // const event = new Event('input');
        // node.dispatchEvent(event);
    }
}

/**
 * Conditionally display an element depending on the value of a form control.
 * 
 * Observe and conditionally set the display property on a HTMLElement depending on
 * the value of a HTMLFieldControlElement.
 * 
 * @param {String} observedControlName - The name of the HTMLFormControlElement whose value shall be observed.
 * @param {String} targetElementOrId - The HTMLElement (or a string with its `id` attribute) which shall be conditionally displayed.
 * @param {String} value - The value of the observed field at which the target element shall be displayed.
 * @param {lart.forms.conditionMatcherCondition} condition - The condition used to compare *value* with the
 *          observed field's value.
 */
lart.forms.conditionalDisplay = function (observedControlName, targetElementOrId, value, condition = lart.forms.conditionMatcherCondition.EQUAL) {
    const collection = document.getElementsByName(observedControlName);
    const target = lart.forms.getElementByGreed(targetElementOrId);
    // Multiselect elements (radio, checkbox, select(?))
    for(const node of collection) {
        const matchesCondition = lart.forms.conditionMatcherFactory(node, value, condition);
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

/**
 * Conditionally disable an element depending on the value of a form control.
 * 
 * Observe and conditionally set the disabled attribute on a HTMLElement depending on
 * the value of a HTMLFieldControlElement.
 * 
 * @param {String} observedControlName - The name of the HTMLFormControlElement whose value shall be observed.
 * @param {String} targetElementOrId - The HTMLElement (or a string with its `id` attribute) which shall be conditionally disabled.
 * @param {String} value - The value of the observed field at which the target element shall be disabled.
 * @param {lart.forms.conditionMatcherCondition} condition - The condition used to compare *value* with the
 *          observed field's value.
 */
lart.forms.conditionalDisable = function (observedControlName, targetElementOrId, value, condition = lart.forms.conditionMatcherCondition.EQUAL) {
    const collection = document.getElementsByName(observedControlName);
    const target = document.getElementById(targetElementOrId);
    // Multiselect elements (radio, checkbox, select(?))
    for(const node of collection) {
        const matchesCondition = lart.forms.conditionMatcherFactory(node, value, condition);
        node.addEventListener('input',
            function (event) {
                if(matchesCondition()) {
                    if( 'disabled' in target ) {
                        target.disabled = true;
                    } else {
                        target.dataset.lartDisabled = true;
                    }
                } else {
                    if( 'disabled' in target ) {
                        target.disabled = false;
                    } else {
                        delete target.dataset.lartDisabled;
                    }
                }
            }
        );
    }
}

/**
 * Counter to keep track of the number of repeats of a block.
 * 
 * @private
 */
lart.forms._repeatBlockCounter = {}

/**
 * Repeat a HTMLElement and use a regular expression to replace strings inside with a running counter.
 * 
 * @param {(HTMLElement|String)} elementOrId A HTMLElement or a string with an id or unique name attribute
 *          to identify a HTMLElement which shall be repeated. Usually this is a block-level element.
 * @param {RegExp} pattern A regular expression pattern to match which will be appended with a counter
 *          for each repetition of the block.
 * @deprecated It's better to use HTMLTemplateElements for this functionality.
 */
lart.forms.repeatBlock = function(elementOrId, pattern) {
    const root = lart.forms.getElementByGreed(elementOrId);
    if (!(root instanceof HTMLElement) ) {
        booteel.logger.error("Attempted to repeat non-existant HTMLElement:", elementOrId);
        throw new TypeError(
            `Passed argument elementOrId=${elementOrId} does not refer to a HTMLElement, but ${root}.`
        );
    }
    if (!root.id) {
        // Element doesn't have an id, but we need it for reference. Assign a random UUID instead.
        root.id = crypto.randomUUID();
    }
    let code = root.firstElementChild.outerHTML;
    if (root.id in lart.forms._repeatBlockCounter) {
        lart.forms._repeatBlockCounter[root.id]++;
    } else {
        lart.forms._repeatBlockCounter[root.id] = parseInt(code.matchAll(pattern).next().value[2]);
        if(typeof(lart.forms._repeatBlockCounter[root.id]) == 'number') {
            lart.forms._repeatBlockCounter[root.id]++;
        } else {
            lart.forms._repeatBlockCounter[root.id] = 1;
        }
    }
    const n = lart.forms._repeatBlockCounter[root.id];
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
 * Add validation to HTMLInputElements of type `range`.
 * 
 * Attach a validation observer to all HTMLInputElements of type `range` which are
 * children of the HTMLElement indicated by *targetZoneElementOrId* and which have
 * the `required` attribute set.
 * 
 * The observed range inputs will pass (client-side) validation only if their slider
 * has been moved at least once, irrespective of their value.
 *
 * The method employed to do this involves setting a custom data attribute
 * (`data-lart-range-moved`) on the HTMLInputElement and checking this as part of
 * the elements custom validation. An event listener is attached to the element to
 * monitor for input and adjust the data attribute accordingly. A MutatioObserver
 * is further attached to the target zone to monitor for the insertion of any
 * further range controls.
 *  
 * @param {(HTMLElement|String)} targetZoneElementOrId - A HTMLElement, or a string
 *          refering to an `id` or `name` attribute identifying an HTMLElement which
 *          is the parent of the range input controls to be validated.
 */
lart.forms.validateRangeInputs = function (targetZoneElementOrId) {
    const targetZone = lart.forms.getElementByGreed(targetZoneElementOrId);
    const inputFields = targetZone.querySelectorAll('input[type="range"]');
    const dataAttributeSetter = function(field) {
        if( !field.hasAttribute('data-lart-range-moved') ) {
            field.setAttribute('data-lart-range-moved', 'false');
            field.addEventListener(
                'input',
                function (event) {
                    event.target.setAttribute('data-lart-range-moved', 'true');
                    event.target.setCustomValidity('');
                },
                { once: true }
            );
            if (field.hasAttribute('required') && field.required ) {
                field.setCustomValidity('You must move the slider at least once.');
            }
            // Add monitor for "required attribute" (don't flag up non-required sliders...)
            function rangeRequiredMonitor(mutationList, observer) {
                for (const mutation of mutationList) {
                    if ( mutation.type == 'attributes' && mutation.attributeName == 'required' ) {
                        const moved = mutation.target.getAttribute('data-lart-range-moved');
                        if ( mutation.target.required && moved == 'false' ) {
                            field.setCustomValidity('You must move the slider at least once.');
                        } else {
                            field.setCustomValidity('');
                        }
                    }
                }
            }
            const rangeRequiredObserver = new MutationObserver(rangeRequiredMonitor);
            rangeRequiredObserver.observe(field, {attributeFilter: ['required']});
            // Should be taken care of by just setting it with the "once" eventListener above
            // field.addEventListener(
            //     'input',
            //     function (event) {
            //         event.target.setCustomValidity('');
            //     }
            // );
        }
    }
    // Set data attribute on existing range inputs
    for (const field of inputFields) {
        dataAttributeSetter(field);
    }
    // Monitor for new range inputs
    const observerCallback = function(mutationList, observer) {
        function recursiveDataAttributeSetter(node) {
            if (node instanceof HTMLInputElement && node.type == 'range') {
                dataAttributeSetter(node);
            }
            if ( node.hasChildNodes() ) {
                for (const child of node.childNodes) {
                    recursiveDataAttributeSetter(child);
                }
            }
        }
        for (const mutation of mutationList) {
            for (const node of mutation.addedNodes) {
                recursiveDataAttributeSetter(node);
            }
        }
    }
    const observer = new MutationObserver(observerCallback);
    observer.observe(targetZone, {childList: true, subtree: true});
}

/**
 * Register a pipeline to submit a form's data to a JavaScript function instead of a HTTP request.
 * 
 * Registers an event handler on the form specified by `formElementOrId` so that the data inside the form
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
 * @param {(HTMLFormElement|String)} formElementOrId - A HTMLFormElement or it's `id` for which
 *          data is to be piped to *receiver*.
 * @param {Callback} receiver - The callback function that should receive the the form data upon submission.
 */
lart.forms.registerPipeline = function (formElementOrId, receiver) {
    const form = lart.forms.getElementByGreed(formElementOrId);
    if (form instanceof HTMLFormElement) {
        form.addEventListener(
            'submit',
            function (event) {
                lart.forms.pipeData(event, receiver);
            },
            false
        )
        booteel.logger.debug(`Registered form pipeline from form '${formElementOrId}' to callback:`, receiver);
    } else {
        booteel.logger.debug(`Failed to register form pipeline. No such form:`, formElementOrId);
    }
}

/**
 * Form submission event callback to validate a form and pipe data to another function.
 * 
 * @param {Event} event - An event (typically 'submit') on a form element, e.g. as issued by .addEventListener().
 * @param {Callback} receiver - A callable to which the form data will be passed as a dictionary.
 * @returns {Boolean} Returns `true` if the receiver function returns a truthy value, false if validation fails or the receiver
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
    const data = lart.forms.getFormData(form);
    if (receiver(data)) {
        return true;
    }
    return false;
}

/**
 * Assemble all data from a specified form into a dictionary of key-value pairs.
 * 
 * @param {(HTMLFormElement|String)} formElementOrId - A form element to extract data from.
 * @returns {object} - Returns a dictionary of key-value pairs, where key is the name (or id as fallback) and value the
 *                     value of each data field within the specified form.
 * @todo Re-implement with {@link lart.forms.getFormControlElements}.
 */
lart.forms.getFormData = function (formElementOrId) {
    const form = lart.forms.getElementByGreed(formElementOrId);
    if (!(form instanceof HTMLFormElement)) {
        booteel.logger.error("Attempted to obtain form data from non-HTMLFormElement:", formElementOrId);
        throw new TypeError(
            `Passed argument formElementOrId=${formElementOrId} does not refer to a HTMLFormElement, but ${form}.`
        );
    }
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
        if (field.getAttribute("type") === "checkbox") {
            // Use value of 'checked' property (boolean)
            data[ref] = field.checked
        } else if (field.getAttribute("type") === "radio") {
            // Only use checked value for radioboxes
            if (field.checked) {
                data[ref] = field.value
            }
        } else {
            data[ref] = field.value;
        }
    }
    return data;
}

//
// LART Translation Tools
//

/**
 * LART utilities for client-side content translation.
 * 
 * @namespace
 */
lart.tr = {};


/**
 * Associative array holding translation identifiers and translations.
 * 
 * @readonly
 * @type {Object<String,Object<String,Object<String,String>>>}
 */
lart.tr.strings = {};

/**
 * Associative array of trId's and innerHTML for missing translation items.
 * 
 * @readonly
 * @type {Object<String,Object<String,String>>}
 */
lart.tr.missing = {};

/**
 * Get the missing trId's and associated innerHTML for missing translation items.
 * 
 * @param {String} ns - The translation namespace to get missing strings for.
 * @returns {String} A JSON template of the missing trId's with their innerHTML.
 */
lart.tr.getMissing = function(ns) {
    buf = {};
    if (ns in lart.tr.missing) {
        for (trId in lart.tr.missing[ns]) {
            [key, subkey] = trId.split(".", 2);
            if (key in buf) {
                buf[key][subkey] = [lart.tr.missing[ns][trId]];
            } else {
                buf[key] = {};
                buf[key][subkey] = [lart.tr.missing[ns][trId]];
            }
        }
    }
    return JSON.stringify(buf, null, 4);
}

/**
 * Add a missing trId and associated innerHTML to the missing trId cache.
 * 
 * @param {String} ns - The translation namespace to add the missing trId to. 
 * @param {String} trId - The translation string identifier.
 * @param {String} [innerHTML='???'] - The associated innerHTML, default is `'???'`.
 */
lart.tr.addMissing = function(ns, trId, innerHTML = '???') {
    if (!(ns in lart.tr.missing)) {
        lart.tr.missing[ns] = {};
    }
    if (!(trId in lart.tr.missing[ns])) {
        lart.tr.missing[ns][trId] = innerHTML;
    } else if (lart.tr.missing[ns][trId] = '???') {
        lart.tr.missing[ns][trId] = innerHTML;
    }
}

/**
 * Get a translation string by its trId.
 * 
 * @param {String} ns - The translation namespace to get the translation string from.
 * @param {String} trId - The translation identifier string.
 * @returns {?String} - The translated string for the identifier, or null if no string for the
 *          *trId* could be found in *ns*.
 */
lart.tr.get = function(ns, trId) {
    const [key, subkey] = trId.split(".", 2);
    booteel.logger.debug(`Fetching translation string with trId '${ns}:${trId}' ['${key}', '${subkey}'].`);
    if (ns in lart.tr.strings) {
        if (key in lart.tr.strings[ns] && subkey in lart.tr.strings[ns][key]) {
            const tr = lart.tr.strings[ns][key][subkey];
            if (tr instanceof Array && tr.length < 3) {
                if (tr.length > 1) {
                    return tr[1];
                }
                return tr[0];
            }
            return tr;
        }
    }
    lart.tr.addMissing(ns, trId);
    booteel.logger.debug(`No translation with trId '${ns}:${trId}' found.`);
    return null;
}
/**
 * Load translation/adaptation strings into a translation namespace.
 * 
 * @example <caption>Loads the LSBQ-RML sections 'meta', 'base' and 'lsb' into the *lsbq* namespace:</caption>
 * const instanceId = lart.utils.searchParams.get('instance');
 * lart.tr.loadFromEel('lsbqrml', eel._lsbqrml_load_version, [instanceId, ['meta', 'base', 'lsb']]);
 * 
 * @param {String} ns - The translation namespace to be used.
 * @param {Function} eelLoader - The Python eel function (from eel.js) implementing the
 *          translation loader on the backend.
 * @param {Array} [loaderParams=[]] - The parameters that the *eelLoader* should be called with.
 */
lart.tr.loadFromEel = function(ns, eelLoader, loaderParams = null) {
    if (!loaderParams) {
        loaderParams = [];
    }
    booteel.logger.debug(`Loading translation strings for namespace '${ns}' from ${eelLoader} with arguments`, loaderParams);
    eelLoader(...loaderParams)(
        function (strings) {
            lart.tr._addStrings(ns, strings);
        }
    );
}

/**
 * Add translation strings from array to {@link lart.tr.strings}.
 * 
 * @private
 * @param {String} ns - The translation namespace to add the strings to.
 * @param {Object<String,String>} strings - An associative array with translation
 *          strings labelled by section. Each section contains an associative array
 *          with a translation-string id, and a list of [1] the original untranslated
 *          string, and [2] the version-specific translation/adaptation.
 */
lart.tr._addStrings = function(ns, strings) {
    booteel.logger.debug(`Adding strings to namespace ${ns}:`, strings);
    if (!(ns in lart.tr.strings)) {
        lart.tr.strings[ns] = {};
    }
    for (const key in strings) {
        if (key in lart.tr.strings[ns]) {
            for (const subkey in strings[key]) {
                booteel.logger.debug(
                    `Overwriting translation string '${ns}:${key}.${subkey}':`,
                    {
                        'before': lart.tr.strings[ns][key][subkey],
                        'after': strings[key][subkey]
                    }
                );
                lart.tr.strings[ns][key][subkey] = strings[key][subkey];
            }
        } else {
            lart.tr.strings[ns][key] = strings[key];
        }
    }
    booteel.logger.debug(`Loaded translation strings for namespace '${ns}':`, lart.tr.strings[ns]);
    lart.tr._activateObservers(ns);
    lart.tr._triggerCallbacks();
}

/**
 * Queue of callbacks waiting to be called once a certain translation namespace becomes available.
 * 
 * @private
 * @type {Object<String,Array<Function>>}
 */
lart.tr._callbackQueue = {};

/**
 * List of Node Id's that should be observed for string translation after loading strings for a namespace.
 * 
 * @private
 * @type {Object<String,Set<String>>}
 */
lart.tr._observerQueue = {};

/**
 * List of Node Id's that are being actively observed for string translation.
 * 
 * @private
 * @type {Object<String,Set<String>>}
 */
lart.tr._activeObservers = {};

/**
 * Register a Node for translation observation for a specific namespace by a Node's Id.
 *
 * This will add an observer running translation on any `HTMLElement` / `Node` that is a
 * child of the Node specified by *nodeId*. Any child node with a `data-*ns*-tr` attribute
 * specifying the *trId* will be subject to translation from its namespace where a string
 * with a matching *trId* is available.
 * 
 * Observers will automatically delay observation until the relevant namespace has been
 * loaded. There is no need to (or point in) registering them separately as a callback.
 * 
 * @param {String} ns - The namespace that should be observed for translation. 
 * @param {String} nodeId - The Id of the Node (and its children) to be observed.
 */
lart.tr.registerObserver = function(ns, nodeId) {
    booteel.logger.debug(`Registering translation observer for node with id '${nodeId}' in namespace '${ns}'.`);
    if (ns in lart.tr.strings) {
        lart.tr._observe(ns, nodeId);
    } else {
        if (!(ns in lart.tr._observerQueue)) {
            lart.tr._observerQueue[ns] = new Set();
        }
        if (!lart.tr._observerQueue[ns].has(nodeId)) {
            lart.tr._observerQueue[ns].add(nodeId);
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
 * @private
 * @param {String} ns - The namespace for which observers should be
 *          activated.
 */
lart.tr._activateObservers = function(ns) {
    booteel.logger.debug(`Activating queued translation observers for namespace '${ns}'`);
    if (!(ns in lart.tr._observerQueue)) {
        return;
    }
    if (!(ns in lart.tr.strings)) {
        booteel.logger.debug('Translation strings not loaded yet, trying again in 100ms.')
        setTimeout(
            function () {
                lart.tr._activateObservers(ns)
            },
            100   // Try again in 100ms
        );
        return;
    }
    for (const nodeId of lart.tr._observerQueue[ns]) {
        booteel.logger.debug(`Activating observer for namespace '${ns}' on Node with id '${nodeId}'.`);
        const node = document.getElementById(nodeId);
        if (!node) {
            booteel.logger.error(`Could not retreive node with id '${nodeId}'.`);
            continue;
        }
        lart.tr.translateNode(ns, node);
        if (!(ns in lart.tr._activeObservers)) {
            lart.tr._activeObservers[ns] = new Set();
        }
        if (!lart.tr._activeObservers[ns].has(nodeId)) {
            const observer = new MutationObserver(
                function (mutationList) {
                    for (const mutation of mutationList) {
                        if (mutation.target instanceof HTMLElement) {
                            lart.tr.translateNode(ns, mutation.target);
                        }
                    }
                }
            );
            observer.observe(
                node,
                {
                    subtree: true,
                    childList: true,
                    attributeFilter: [`data-${ns}-tr`]
                }
            );
            lart.tr._activeObservers[ns].add(nodeId);
        }
    }
}

/**
 * Traverse through a DOM Node and translate all applicable HTMLElements.
 * 
 * @param {String} ns - The translation namespace to be translated on the nodes.
 * @param {Node} node - A DOM Node to be traversed and translated. 
 */
lart.tr.translateNode = function(ns, node) {
    booteel.logger.debug('Translating node:', node);
    lart.tr._translateElement(ns, node);
    const translatables = node.querySelectorAll(`[data-${ns}-tr]`);
    for (const translatable of translatables) {
        lart.tr._translateElement(ns, translatable);
    }
}

/**
 * Check, and if applicable, substitute a HTMLElement's innerHTML with version-specific string.
 * 
 * @private
 * @param {String} ns - The translation namespace to be used.
 * @param {HTMLElement} element - the HTMLElement to apply translation to.
 */
lart.tr._translateElement = function(ns, element) {
    const attrName = `${ns}Tr`;
    if (element instanceof HTMLElement && attrName in element.dataset) {
        booteel.logger.debug('Translating element:', element);
        const trId = element.dataset[attrName];
        const trString = lart.tr.get(ns, trId);
        if (trString) {
            element.innerHTML = trString;
            element.dataset[`${attrName}Origin`] = trId;
            delete element.dataset[attrName]; // Avoid repeatedly targeting same string
        } else {
            lart.tr.addMissing(ns, trId, element.innerHTML);
        }
    } else {
        booteel.logger.debug('Skipping untranslatable element:', element);
    }
}

/**
 * Translate an attribute on one or more elements specified by their id.
 * 
 * If namespace *ns* has not been loaded yet, then translation will automatically
 * be postponed until it is loaded. There is no need to manually register a callback.
 * 
 * @param {String} ns - The translation namespace to be used.
 * @param {Object<String,Array<String,String>} attrs - An associative array
 * with Element Ids as key, and a two-member list as values, where the first
 * is the attribute name and the second the trId.
 */
lart.tr.translateAttrs = function(ns, attrs) {
    if(ns in lart.tr.strings) {
        for (const elementId in attrs) {
            const element = document.getElementById(elementId);
            if (!element) {
                booteel.logger.error(`Could not retreive element with id '${elementId}'.`);
                continue;
            }
            const [attrName, trId] = attrs[elementId];
            const trString = lart.tr.get(ns, trId);
            if (trString) {
                element.setAttribute(attrName, trString);
            }
        }
        return;
    }
    lart.tr.registerCallback(
        ns,
        function () {
            lart.tr.translateAttrs(ns, attrs);
        }
    );
}

lart.tr.registerCallback = function (ns, callback, callbackParams = null) {
    if (!callbackParams) {
        callbackParams = [];
    }
    if (!(ns in lart.tr._callbackQueue)) {
        lart.tr._callbackQueue[ns] = [];
    }
    lart.tr._callbackQueue[ns].push([callback, callbackParams]);
    if (ns in lart.tr.strings) {
        lart.tr._triggerCallbacks();
    }
}

lart.tr._triggerCallbacks = function () {
    for (const ns in lart.tr.strings) {
        if (ns in lart.tr._callbackQueue) {
            for (const [callback, callbackParams] of lart.tr._callbackQueue[ns]) {
                callback(...callbackParams);
            }
        }
    }
}

//
// LEGACY ALIASES FROM BEFORE REFACTOR OF LIBRARY
//

/** @deprecated */
lart.forms.searchParams = lart.utils.searchParams;
/** @deprecated */
lart.forms.util = {};
/** @deprecated */
lart.forms.util.patternForUUID = lart.utils.UUID.pattern;
/** @deprecated */
lart.forms.util.nilUUID = lart.utils.UUID.nilUUID;
/** @deprecated */
lart.forms.util.isUUID = lart.utils.UUID.isUUID;
/** @deprecated */
lart.forms.util.getSelectValues = lart.forms.getSelectValues;
/** @deprecated */
lart.forms.util.getFormFieldValue = lart.forms.getControlValue;
/** @deprecated */
lart.forms.util.inputConditionMatcher = lart.forms.conditionMatcherFactory;
/** @deprecated */
lart.forms.util.autofillForm = lart.forms.autoFill;
/** @deprecated */
lart.forms.monitorRangeInputs = lart.forms.validateRangeInputs;
/** @deprecated */
lart.forms.getData = lart.forms.getFormData