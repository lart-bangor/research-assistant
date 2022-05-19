//Funcions for MGT selection page
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
var fullDataset = {};
var meta = {
    "File ID": "",
    "version": "",
    "Researcher id": "",
    "Location": "",
    "participant id": "",
    "Date & Time": timeStamp
    
};
let presentationOrders = [];


//initialise labels for sliders, to be redefined within fetchMgt()
let agree = "";
let disagree = "";
let headerTxt = "";
let sliderWarn = "";
let sliderTxt = "";
let btnTxt = "";
let headerElement = "";
let sliderElement = "";
        
function showMgt() {
    //get values from researcher
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
        .then(data => fetchMgt(data));  //pass the contents of jsonFile to output_info()
    }
    

function fetchMgt(data) {
    //displays MGT component of page
    console.log("data is ", data);
    headerElement = document.getElementById("language_header");
    sliderElement = document.getElementById("slider_info");
    btnElement = document.getElementById("btnNext");
    document.getElementById("mgtBody").style.display = "block";     
    
    headerTxt = data.base.header;
    agree = data.base.agreement;            
    disagree = data.base.disagreement;
    sliderTxt = data.base.sliderInfo;
    sliderWarn = data.base.sliderWarn;
    btnTxt = data.base.nextBtn;

//    headerElement.innerHTML =  headerTxt;
  //  sliderElement.innerHTML =  " " + sliderTxt;
    //btnElement.innerHTML = btnTxt;
    
    mgtAdjectives = data.mgtItems;  //set mgtAdjectives
    mgtAudioList = data.mgtAudioList;   // set mgtAudioList;
    moveToNext();
}


function moveToNext() {
    currentAudioArray = mgtAudioList;
    audioLen = currentAudioArray.length;
    if(audioLen >0) {                       //if list of audio recs is not empty
        hidePrecedingDiv();
        loadHeaders();
        window.location.href = "#mgtTop";
        console.log("in moveToNext audio list is: ", currentAudioArray);
        playGuise(mgtAudioList[0]);  //play first item on guise list
        loadAdjectives(mgtAdjectives);
        console.log("Adjectives = ", mgtAdjectives);
        currentAudioArray.shift();
        mgtAudioList = currentAudioArray    //redefine mgtAudioList after first item is removed
        console.log("after popping array is ", mgtAudioList);
                
    } else {
        window.location.assign("mgtEnd.html");
        formdata = lart.forms.getFormData("mgtDataForm"); 
        data = presentationOrders.concat(formdata);
        console.log("data type is: ", typeof(data));
        eel.grab_mgt_ratings(data)();
        }     
     
}

function loadHeaders() {
        headerElement.innerHTML =  headerTxt;
        sliderElement.innerHTML =  " " + sliderTxt;
        btnElement.innerHTML = btnTxt;

}

function setMeta(metaData) {
    meta['version'] = metaData[0];
    meta['Researcher id'] = metaData[1];
    meta['Location'] = metaData[2];
    meta['participant id'] = metaData[3];
    idTime = timeStamp.getDate() + "-" + timeStamp.getMonth() + "-" + timeStamp.getFullYear() + "_" + timeStamp.getHours() + "-" + timeStamp.getMinutes() + "-" + timeStamp.getSeconds();
    meta['File ID'] = metaData[3] + "_" + idTime;
    }

function loadAdjectives() {
    //this displays a slider for each adjective on itemList
    let currentDiv = "mgtRatingScale_" + String(counter);
    const mgtElement = document.getElementById(currentDiv);
    let currentGuiseName = fetchAudioLabel(mgtAudioList[0]);
    console.log("current DIV's ID is ", currentDiv);
    let itemsLen = mgtAdjectives.length;
    let shuffledAdjectives = mgtAdjectives.sort(() => Math.random() - 0.5)   //randomise order of adjectives
    let presentationOrder = {
        "guise name": currentGuiseName,
        "order of presentation": shuffledAdjectives
    }
    presentationOrders.unshift(presentationOrder);
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


                
function showMgtBlock() {
    document.getElementById("mgtBody").style.display = "block";             
    }

function hideInitForm() {
    const form = document.getElementById('mgtToggleForm');
    const btn = document.getElementById('toggle-btn');
    form.style.display = 'none';
    btn.style.display = 'none';
    }

function playGuise(audio) {
    //console.log("Current audio path is ", audioFile);
    console.log("current audio supposed to play is...:", audio);
    //const audio = document.getElementById("guiseAudio");
    //audio.play();

}

function fetchAudioLabel(filename) {
    let guiseName = String(mgtAudioList[0]);
    let extBegin = filename.indexOf(".mp3");
    let currentGuiseName = guiseName.slice(0,extBegin);
    return currentGuiseName;
}

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

function fetchAudio() {
    currentFile = String(window.location.pathname);
    console.log("currentFile is: ", currentFile);
    ext = currentFile.search("index.html");
    console.log("ext is: " , ext);
    currentLocation = currentFile.slice(0, ext);
    console.log("current location is: ", currentLocation);
    audioFile = currentLocation + "audio files/" + mgtAudioList[0];
    console.log("audio file is: ", audioFile);
    return audioFile;
}
