//Funcions for MGT selection part of page
function loadSurveyVersions() {
    availableVersions = eel._lsbq_getversions()(populateSurveyVersions);     // this will probably need to be changed to a more generic "survey_mgt_get_versions", 
                                                                                // or hard-coded for each questionnaire.
}

function populateSurveyVersions(versions) {
    select = document.getElementById('selectMgtVersion');
    for (const version in versions) {
        option = document.createElement('option');
        option.setAttribute('value', version);
        option.appendChild(document.createTextNode(versions[version]))
        select.appendChild(option);
    }
}


// #########################################################################################################
// #                                                                                                       #
// #     Main section: grab MGT info in LANG from json, display, record responses, send to Python          #
// #                                                                                                       #
// #########################################################################################################

// counter to keep track of DIV id's (each DIV is mgtRatingScale_ + a number)
let counter = 0;
const timeStamp = new Date();

//initialise arrays for adjectives & for audio files to be played
let mgtAdjectives = [];
let mgtAudioList = [];

const meta = {
    "file_id": "",
    "version": "",
    "researcher_id": "",
    "location": "",
    "participant_id": "",
    "date_time": timeStamp
}

let interface = {};
let partResponses = [];
let currentGuiseName = "";


//initialise labels for sliders, to be redefined within fetchMgt()
let agree = "";
let disagree = "";
let headerTxt = "";
let sliderWarn = "";
let sliderTxt = "";
let btnTxt = "";
let headerElement = "";
let sliderElement = "";

// ############################
// #    secondary functions   #
// ############################

/**
 * Generate pseudo-random letter+number string to add to file names.
 * 
 * @returns {String} A pseudo-random combination of letters and numbers
 */
function setSubId() {
    let numSub = Math.floor(Math.random() * 1000000);
    const alphabet = "abcdefghijklmnopqrstuvwxyz"
    let res = "";
    for (let i = 0; i < 5; i++) {
        res += alphabet[Math.floor(Math.random() * alphabet.length)];
    }
    res = res + numSub;
    const resArr = shuffle(res.split(""));
    const res1 = resArr.toString();
    const finalRes = res1.replace(/,/g, "");
    return finalRes;
}

/**
 * Set the meta-data in the global *meta* object.
 * 
 * CAUTION: Modifies the global *meta* object as a side effect.
 * 
 * @param {Array<String>} metaData - An array containing the metadata,
 *      in the specific order:
 *      * Version
 *      * Researcher Id
 *      * Location
 *      * Participant Id
 */
function setMeta(metaData) {
    meta['version'] = metaData[0];
    meta['researcher_id'] = metaData[1];
    meta['location'] = metaData[2];
    meta['participant_id'] = metaData[3];
    month = timeStamp.getMonth() + 1;
    idTime = timeStamp.getDate() + "-" + month + "-" + timeStamp.getFullYear() + "_" + timeStamp.getHours() + "-" + timeStamp.getMinutes() + "-" + timeStamp.getSeconds();
    meta['file_id'] = metaData[3] + "_" + idTime + "_" + setSubId();
    console.log("file ID is: ", meta['file_id']);
}

/**
 * Hide the version selection form.
 */
function hideInitForm() {
    const form = document.getElementById('mgtToggleForm');
    const btn = document.getElementById('toggle-btn');
    form.style.display = 'none';
    btn.style.display = 'none';
}

/**
 * Return language-specific data for the MGT interface.
 * 
 * CAUTION: Sets the gloabl *interface* object as a side effect.
 * 
 * @param {object} jsonObj - The deJSONified version data
 * @returns {object} - Returns the same jsonObj that was passed in.
 */
function setIntface(jsonObj) {
    interface = jsonObj;
    return interface;
}

/**
 * Hide sliders for which ratins have already been obtained.
 */
function hidePrecedingDiv() {
    console.log("inside hide DIV counter is: ", counter);
    if (counter !== 0) {
        const previousId = "mgtRatingScale_" + String(counter - 1);
        console.log("previous rat8ng id is: ", previousId);
        const x = document.getElementById(previousId);
        console.log("var x = ", x);
        x.style.display = "none";
    }
}

/**
 * Set headers depending on the version selected.
 */
function loadHeaders() {
    headerElement.innerHTML = headerTxt;
    sliderElement.innerHTML = " " + sliderTxt;
    btnElement.innerHTML = btnTxt;
    btnSectElement.style.display = "none";  //hide button so that guise can play. It will the re-appear as "next" insated of "start"
}

/**
 * Shuffle the order of a list of strings
 * 
 * @param {Array<String>} a - An array of strings to be shuffled.
 * @returns {Array<String>} A copy of the array with the members shuffled randomly.
 */
function shuffle(a) {       //shuffles members of array
    let j, x, i;
    for (i = a.length - 1; i > 0; i--) {
        j = Math.floor(Math.random() * (i + 1));
        x = a[i];
        a[i] = a[j];
        a[j] = x;
    }
    return a;
}

/**
 * Derive a label based on an audio file's name.
 * 
 * @param {String} filename - The name of the audio file
 * @returns {String} The label to be used for this audio file
 */
function fetchAudioLabel(filename) {
    let guiseName = String(mgtAudioList[0]);
    let extBegin = filename.indexOf(".mp3");
    let currentGuiseName = guiseName.slice(0, extBegin);
    return currentGuiseName;
}


// ###############################################
// #             Primary functions               #
// ###############################################

/**
 * Match ratings to a guise instance and return them as an array.
 * 
 * @param {object} guiseObj -
 * @param {Array} ratingsArr 
 * @returns {Array} - An array of ratings. 
 */
function addRatings(guiseObj, ratingsArr) {
    const ratings = [];
    const guiseNameSuf = "_" + guiseObj['guise name'];
    for (const pair of ratingsArr) {          //for each pair on the array
        if (pair[0].includes(guiseObj['guise name'])) {           //if first element of name-rating pair includes current guise name
            const cleanLabel = pair[0].replace(guiseNameSuf, '');
            ratings.push([cleanLabel, pair[1]]);
        }
    }
    console.log("rating array is: ", ratings);
    return ratings;
}

/**
 * Prepare results ready for JSONifying and passing to the backend.
 * 
 * @param {Array} formArr - An array containing pairs of slider name and rating.
 * @param {Array} responsesArr - An array of guises as objects of the form `{'guise name': ..., 'presentation order': ...}`.
 */
function loadResults(formArr, responsesArr) {   //formArr contains arrays of pairs: [slider_name, rating] -- responseArr is an array of guises as objects: {guise name: + presentation order: }
    for (i = 0; i < responsesArr.length; i++) {  //for each response object on the array 
        const currentGuise = responsesArr[i];
        console.log("guise name is: ", currentGuise["guise name"]);
        const ratings = addRatings(currentGuise, formArr);
        const alpabetisedRatings = ratings.sort();
        currentGuise["ratings"] = alpabetisedRatings;
    }
}


/**
 * Display a slider for each adjective in list of items.
 * 
 * CAUTION: Affects globals *counter* and *partResponse* as side effect.
 */
function loadAdjectives() {
    const currentDivId = "mgtRatingScale_" + String(counter);
    const mgtElement = document.getElementById(currentDivId);
    const currentGuiseName = fetchAudioLabel(mgtAudioList[0]);
    console.log("current DIV's ID is ", currentDivId);
    const itemsLen = mgtAdjectives.length;
    const shuffledAdjectives = shuffle(interface.mgtItems);   //randomise order of adjectives from original list
    console.log("shuffled adjectives: ", shuffledAdjectives);
    const arrayCopy = shuffledAdjectives.slice();
    partResponses.push({ "guise name": currentGuiseName, "Presentation order": arrayCopy });
    console.log("Part response array is ", partResponses);
    console.log("location is: ", window.location.href);
    let code = "";
    for (let i = 0; i < itemsLen; i++) {
        code += "<div class='row mb-0'>" +
            "<div class='col-2'></div>" +
            "<div class='col-5 text-start'><div style = 'font-size: small'>" + disagree + "</div></div>" +
            "<div class='col-5 text-end'><div style = 'font-size: small'>" + agree + "</div></div>" +
            "</div>" +
            "<div class='row mb-1'>" +
            "<label for='" + shuffledAdjectives[i] + "_" + currentGuiseName + "' class='col-2 col-form-label'>" +  //s will pull from a variable once we have the info about which recording is being judged
            shuffledAdjectives[i] +
            "</label>" +
            "<div class='col-10 mt-2'>" +
            "<input type='range' class='form-range d-block' min='0' max='100' step='any' id='" + shuffledAdjectives[i] + "_" + currentGuiseName + "' required />" +
            "<div class='invalid-feedback invalid-range'>" + sliderWarn + "</div>" +
            "</div>" +
            "</div>" +
            "<div><p><br /><br /><br /><br /></p></div>";
    }
    counter++;
    mgtElement.insertAdjacentHTML('beforeend', code);

}

/**
 * Show the MGT practice task.
 * 
 * @TODO Needs proper documentation.
 */
function showPractice() {
    document.getElementById("instructions").style.display = "none"; //hide instructions part
    document.getElementById("practice").style.display = "block";
    practiceHeadElement = document.getElementById("practiceHeader");
    practiceHeadElement.innerHTML = "<h5>" + practiceHeader + "</h5>";
    practiceInfoElement = document.getElementById("practiceSlider_info");
    practiceInfoElement.style.display = "block";
    practiceInfoElement.innerHTML = practiceInfo;
    instrucTailElement = document.getElementById("practiceEnd");
    instructTail = interface.base.instructionsTail;
    let practiceElement = document.getElementById("practiceBody");
    let num = 0;        //to provide different id for each practice slider
    let listofAdj = interface.mgtItems;
    eel.playGuise(practiceGuise);
    console.log("Currently playing... ", practiceGuise);
    itemsLen = listofAdj.length;
    let code = "";

    for (let i = 0; i < itemsLen; i++) {
        code += "<div class='row mb-0'>" +
            "<div class='col-2'></div>" +
            "<div class='col-5 text-start'><div style = 'font-size: small'>" + disagree + "</div></div>" +
            "<div class='col-5 text-end'><div style = 'font-size: small'>" + agree + "</div></div>" +
            "</div>" +
            "<div class='row mb-1'>" +
            "<label for='" + listofAdj[i] + num + "' class='col-2 col-form-label'>" + listofAdj[i] +
            "</label>" +
            "<div class='col-10 mt-2'>" +
            "<input type='range' class='form-range d-block' min='0' max='100' step='any' id='" + listofAdj[i] + num + "' required />" +
            "<div class='invalid-feedback invalid-range'>" + sliderWarn + "</div>" +
            "</div>" +
            "</div>" +
            "<div><p><br /><br /><br /><br /></p></div>";
    }
    practiceElement.insertAdjacentHTML('beforeend', code);
    num++;
    instrucTailElement.innerHTML = "<br /><div class='row text-center'><h5 style='color: blue;'>" + interface.base.instructionsTail + "</h5></div><br /><br />";
    btnElement.innerHTML = startBtn;
    mgtBtn = document.getElementById("mgtBtn");
    setTimeout(() => { mgtBtn.style.display = "block"; }, 50000);   //wait till guise has finished playing, then show "next" button

}

/**
 * Show MGT Instructions.
 * 
 * @TODO Needs proper documentation.
 */
function showInstruct() {
    instrHeadElement = document.getElementById("instructionsHead");
    instrElement = document.getElementById("instructionsMain");
    instrElement.style.display = "block";
    instrHead = interface.base.instructionsHead;
    instrTxt = interface.base.instructionsTxt;
    instrHeadElement.innerHTML = "<br /><div class='row text-center'><h3>" + instrHead + "</h3></div>";
    instrElement.innerHTML = instrTxt;
    document.getElementById("practiceBtn").style.display = "block";

}

/**
 * Load rating interface as many times as there are recorded guises to rate.
 * 
 * @TODO Needs proper documentation
 * 
 * @param {*} words 
 * @param {*} audioFiles 
 */
function moveToNext(words, audioFiles) {
    let practiceiDiv = document.getElementById("practice");
    if (practiceiDiv.style.display === "block") {
        practiceiDiv.style.display = "none";
    }

    if ((typeof words === 'undefined' || typeof audioFiles === 'undefined')) {      //if moveToNext() is called after initialising, run MGT proper
        words = mgtAdjectives;
        audioFiles = mgtAudioList;

        audioLen = audioFiles.length;
        if (audioLen > 0) {                       //if list of audio recs is not empty
            hidePrecedingDiv();
            loadHeaders();
            document.getElementById("mgtBody").style.display = "block";
            window.location.href = "#mgtTop";
            eel.playGuise(audioFiles[0]);  //play first item on guise list
            console.log("Adjectives = ", words);
            loadAdjectives(words);
            audioFiles.shift();
            mgtAudioList = audioFiles    //redefine mgtAudioList after first item is removed
            console.log("after popping array is ", mgtAudioList);
            btn = document.getElementById("mgtBtn");
            setTimeout(() => { btn.style.display = "block"; }, 50000);   //wait till guise has finished playing, then show "start" button

        } else {
            window.location.assign("mgtEnd.html");
            formdata = lart.forms.getFormData("mgtDataForm");
            console.log("form data is ", formdata);
            const entries = Object.entries(formdata);
            console.log("inside else partResponses is :", partResponses);
            loadResults(entries, partResponses);
            const fullDataset = { meta, partResponses };
            console.log("FINAL JSOn object is : ", JSON.stringify(fullDataset, undefined, 2));
            eel.grab_mgt_ratings(fullDataset)();
        }
    } else {                //if it is the first (initialising) call to moveToNext(), show instrcutions and practice guise
        showInstruct();
    }

}

/**
 * Display the MGT component of the page.
 * 
 * @TODO Needs proper documentation.
 * 
 * @param {*} data 
 */
function fetchMgt(data) {
    console.log("data from json is ", data);
    headerElement = document.getElementById("language_header");
    sliderElement = document.getElementById("slider_info");
    btnElement = document.getElementById("btnNext");
    btnSectElement = document.getElementById("mgtBtn");

    headerTxt = interface.base.header;
    agree = interface.base.agreement;
    disagree = interface.base.disagreement;
    sliderTxt = interface.base.sliderInfo;
    sliderWarn = interface.base.sliderWarn;
    btnTxt = interface.base.nextBtn;
    practiceHeader = headerTxt;
    practiceInfo = sliderTxt;
    startBtn = interface.base.startBtn;
    practiceGuise = interface.practiceAudio;

    mgtAdjectives = interface.mgtItems;  //set mgtAdjectives
    mgtAudioList = interface.mgtAudioList;   // set mgtAudioList;
    moveToNext(mgtAdjectives, mgtAudioList);
}

/**
 * Get the version selection information and initial MGT.
 */
function showMgt() {
    const fetch_version = document.getElementById("selectMgtVersion");
    const fetch_resId = document.getElementById("researcherId");
    const fetch_location = document.getElementById("researchLocation");
    const fetch_partId = document.getElementById("participantId");
    const metaValues = [fetch_version.value, fetch_resId.value, fetch_location.value, fetch_partId.value];
    setMeta(metaValues);    //load value on meta{} object, to keep for later
    console.log("meta data is: ", meta);

    jsonFile = "versions/" + meta['version'] + ".json";  //set filename based on selected version
    console.log("json file is: ", jsonFile);
    hideInitForm();
    lart.forms.requireValidation(true);
    fetch(jsonFile)
        .then(response => response.json())
        .then(data => setIntface(data))
        .then(output => fetchMgt(output));  //pass the contents of jsonFile to output_info()
}
