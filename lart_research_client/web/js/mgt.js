//Funcions for MGT selection part of page
function loadSurveyVersions() {
    availableVersions = eel._lsbqrml_getversions()(populateSurveyVersions);     // this will probably need to be changed to a more generic "survey_rml_get_versions", 
                                                                                      // or hard-coded for each questionnaire.
    }
            
function populateSurveyVersions(versions) {
    select = document.getElementById('selectMgtVersion');
        for(version in versions) {
            option = document.createElement('option');
            option.setAttribute('value', version);
            option.appendChild(document.createTextNode(versions[version]))
            select.appendChild(option);
        }
    }


//#########################################################################################################//
//#                                                                                                       #// 
//#     Main section: grab MGT info in LANG from json, display, record responses, send to Python          #//
//#                                                                                                       #//
//#########################################################################################################//

// counter to keep track of DIV id's (each DIV is mgtRatingScale_ + a number)
counter = 0;
const timeStamp = new Date();

//initialise arrays for adjectives & for audio files to be played
let mgtAdjectives = [];     
let mgtAudioList = [];

const meta = {
    "File ID": "",
    "version": "",
    "Researcher id": "",
    "Location": "",
    "participant id": "",
    "Date & Time": timeStamp
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

//############################//
//#    secondary functions   #//
//############################//

//sets meta values as object
function setMeta(metaData) {
    meta['version'] = metaData[0];
    meta['Researcher id'] = metaData[1];
    meta['Location'] = metaData[2];
    meta['participant id'] = metaData[3];
    idTime = timeStamp.getDate() + "-" + timeStamp.getMonth() + "-" + timeStamp.getFullYear() + "_" + timeStamp.getHours() + "-" + timeStamp.getMinutes() + "-" + timeStamp.getSeconds();
    meta['File ID'] = metaData[3] + "_" + idTime;
    }

//hides user form before moving on to MGT proper
    function hideInitForm() {
    const form = document.getElementById('mgtToggleForm');
    const btn = document.getElementById('toggle-btn');
    form.style.display = 'none';
    btn.style.display = 'none';
    }

//returns language-specific data for MGT interface
    function setIntface(jsonObj) {
    interface = jsonObj;
    return interface;
    }


//hides sliders for which ratings have already been obtained
    function hidePrecedingDiv() {
    console.log("inside hide DIV counter is: ", counter);
    if(counter !== 0) {
        let previousId = "mgtRatingScale_" + String(counter-1);
        console.log("previous rat8ng id is: ", previousId);
        var x = document.getElementById(previousId);
        console.log("var x = ", x);
        x.style.display = "none";
    }
          
}


//sets headers to be kepth throughout test, based on language selected
function loadHeaders() {
    headerElement.innerHTML =  headerTxt;
    sliderElement.innerHTML =  " " + sliderTxt;
    btnElement.innerHTML = btnTxt;
}

//shuffles order of adjectives 
function shuffle(a) {       //shuffles members of array
    var j, x, i;
    for (i = a.length - 1; i > 0; i--) {
        j = Math.floor(Math.random() * (i + 1));
        x = a[i];
        a[i] = a[j];
        a[j] = x;
        }
    return a;
    }

//plays audio guise
function playGuise(audio) {
    //console.log("Current audio path is ", audioFile);
    console.log("current audio supposed to play is...:", audio);
    //const audio = document.getElementById("guiseAudio");
    //audio.play();

}

//derives label based on audiofile's name
function fetchAudioLabel(filename) {
    let guiseName = String(mgtAudioList[0]);
    let extBegin = filename.indexOf(".mp3");
    let currentGuiseName = guiseName.slice(0,extBegin);
    return currentGuiseName;
}

//###############################################//
//#             Primary functions               #//
//###############################################//

//loads results onto json-ready object for passing to Python
/*
for (const element of formArr) {
    console.log("array pair = ", element);
    console.log("object list is: ", responsesArr);
*/

function loadResults(formArr, responsesArr) {
    for(i = 0; i < responsesArr.length; i++) {  //for each response object on teh array 
        currentGuise = responsesArr[0];
        console.log("guise name is: ", currentGuise["guise name"]);
        if(element[0].includes(currentGuise['guise name']) ) {           //if first element of name-rating pair
            console.log("current element match: ", element[0])               
        } 
        else {
            console.log("current element MISmatch: ", element[0])

        }
    }
 }

 
//displays a slider for each adjective on itemList
function loadAdjectives() {
    let currentDiv = "mgtRatingScale_" + String(counter);
    const mgtElement = document.getElementById(currentDiv);
    currentGuiseName = fetchAudioLabel(mgtAudioList[0]);
    console.log("current DIV's ID is ", currentDiv);
    let itemsLen = mgtAdjectives.length;
    let shuffledAdjectives = shuffle(interface.mgtItems);   //randomise order of adjectives from original list
    console.log("shuffled adjectives: ", shuffledAdjectives);
    arrayCopy = shuffledAdjectives.slice();
    partResponses.push({"guise name": currentGuiseName, "Presentation order": arrayCopy});
    console.log("Part response array is ", partResponses);
    let code = "<ul>";
    for (let i = 0; i < itemsLen; i++) {
        code += "<div class='row mb-0'>" +
                    "<div class='col-2'></div>" +
                    "<div class='col-5 text-start'><div style = 'font-size: small'>" + agree + "</div></div>" +
                    "<div class='col-5 text-end'><div style = 'font-size: small'>" + disagree + "</div></div>" +
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


//loads rating interface as many times as there are recorded guises to rate
function moveToNext(words, audioFiles) {
    if((typeof words === 'undefined'  || typeof audioFiles === 'undefined')) {
        words = mgtAdjectives;
        audioFiles = mgtAudioList;
        }
    audioLen = audioFiles.length;
    if(audioLen >0) {                       //if list of audio recs is not empty
        hidePrecedingDiv();
        loadHeaders();
        window.location.href = "#mgtTop";
        console.log("in moveToNext audio list is: ", audioFiles);
        playGuise(audioFiles[0]);  //play first item on guise list
        console.log("Adjectives = ", words);
        loadAdjectives(words);        
        audioFiles.shift();
        mgtAudioList = audioFiles    //redefine mgtAudioList after first item is removed
        console.log("after popping array is ", mgtAudioList);
                
    } else {
        //window.location.assign("mgtEnd.html");
        formdata = lart.forms.getFormData("mgtDataForm"); 
        console.log("form data is ", formdata);
        const entries = Object.entries(formdata);
        console.log("inside else partResponses is :", partResponses);
        loadResults(entries, partResponses);
        
        //const entries = Object.entries(formdata);
        //console.log("formdata now is: ", entries);
        //console.log("full JSOn object is : ", JSON.stringify(partResponses, undefined, 2));
        //console.log();
        //loadResponses(entries);
        //const fullDataset = {meta, partResponses};
        //console.log("FINAL JSOn object is : ", JSON.stringify(fullDataset, undefined, 2));
        //console.log("full JSOn object after loading responses : ", JSON.stringify(partResponses, undefined, 2));
        eel.grab_mgt_ratings(fullDataset)();
        }     
     
}

//displays MGT component of page
function fetchMgt(data) {       
    console.log("data from json is ", data);
    headerElement = document.getElementById("language_header");
    sliderElement = document.getElementById("slider_info");
    btnElement = document.getElementById("btnNext");
    document.getElementById("mgtBody").style.display = "block";     
      
    headerTxt = interface.base.header;
    agree = interface.base.agreement;            
    disagree = interface.base.disagreement;
    sliderTxt = interface.base.sliderInfo;
    sliderWarn = interface.base.sliderWarn;
    btnTxt = interface.base.nextBtn;
      
    mgtAdjectives = interface.mgtItems;  //set mgtAdjectives
    mgtAudioList = interface.mgtAudioList;   // set mgtAudioList;
    moveToNext(mgtAdjectives, mgtAudioList);
    }
    

//gets values entered by researcher
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
    fetch(jsonFile)
        .then(response => response.json())
        .then(data => setIntface(data))
        .then(output => fetchMgt(output));  //pass the contents of jsonFile to output_info()
    }   
