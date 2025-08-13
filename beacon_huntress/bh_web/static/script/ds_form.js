function buttonSelect() {
    // GET THE DROPDOWN AND BUTTON ELEMENTS
    var selectElement = document.getElementById('ds_droplist');
    var submitButton = document.getElementById('runcmd');

    console.log(submitButton)

    // ENABLE BUTTON IF DATASOURCE IS SELECT
    if (selectElement.value !== "") {
        submitButton.disabled = false;
    } else {
        submitButton.disabled = true;
    }
}

function addFieldsRun() {
    // GET THE DROPDOWN ELEMENTS
    var selectElement = document.getElementById('ds_droplist');
    var selectedOption = selectElement.options[selectElement.selectedIndex];
    var selectedType = selectedOption.getAttribute('data_type');
    var selectedDSName = selectedOption.getAttribute('ds_name')

    // GET THE CONTAINER WHERE ADDITIONAL FIELDS WILL BE ADDED
    var additionalFieldsContainer = document.getElementById('additional-fields');

    // CLEAR PREVIOUS FIELDS
    additionalFieldsContainer.innerHTML = '';

    // LOAD ADDITIONAL FORM FIELDS
    if (selectedType == "Elastic" || selectedType == "Security Onion") {  // For Elastic & Sec Onion
        additionalFieldsContainer.innerHTML = `
            <div class="mb-3">
                <label for="start_dte">Start Datetime</label><br>
                <input id="start_dte" name="start_dte" class="form-control" type="datetime-local" />
                <div id="textHelp" class="form-text">Start datetime (optional).</div>
            </div>
            <div class="mb-3">
                <label for="end_dte">End Datetime</label><br>
                <input id="end_dte" name="end_dte" class="form-control" type="datetime-local" />
                <div id="textHelp" class="form-text">End datetime (optional).</div>
            </div>
        `;
    } else if ((selectedType == "Zeek Connection Logs" && selectedDSName == "Zeek Connection Logs") || (selectedType == "Delta File" && selectedDSName == "Delta File") ||
        (selectedType == "HTTP File" && selectedDSName == "HTTP File") || (selectedType == "DNS File" && selectedDSName == "DNS File") ||
        (selectedType == "Custom File" && selectedDSName == "Custom File")) {
        additionalFieldsContainer.innerHTML = `
            <div class="form-group">
                <label for="raw_log_loc">Raw Log Location</label><br>
                <input type="text" id="raw_log_loc" name="raw_log_loc" class="form-control">
            </div>
            <div class="mb-3">
                <label for="start_dte">Start Datetime</label><br>
                <input id="start_dte" name="start_dte" class="form-control" type="datetime-local" />
                <div id="textHelp" class="form-text">Start datetime (optional).</div>
            </div>
            <div class="mb-3">
                <label for="end_dte">End Datetime</label><br>
                <input id="end_dte" name="end_dte" class="form-control" type="datetime-local" />
                <div id="textHelp" class="form-text">End datetime (optional).</div>
            </div>
        `;
    }
    else if ((selectedType == "Zeek Connection Logs" && selectedDSName != "Zeek Connection Logs") || (selectedType == "Delta File" && selectedDSName != "Delta File")
        (selectedType == "HTTP File" && selectedDSName != "HTTP File") || (selectedType == "DNS File" && selectedDSName != "DNS File") ||
        (selectedType == "Custom File" && selectedDSName != "Custom File")) {
        additionalFieldsContainer.innerHTML = `
            <div class="mb-3">
                <label for="start_dte">Start Datetime</label><br>
                <input id="start_dte" name="start_dte" class="form-control" type="datetime-local" />
                <div id="textHelp" class="form-text">Start datetime (optional).</div>
            </div>
            <div class="mb-3">
                <label for="end_dte">End Datetime</label><br>
                <input id="end_dte" name="end_dte" class="form-control" type="datetime-local" />
                <div id="textHelp" class="form-text">End datetime (optional).</div>
            </div>
        `;
    }

    //ADD THE DATA_TYPE TO THE REQUEST
    document.getElementById('data_type_field').value = selectedType;

    buttonSelect();
}

function addFieldsDS() {
    // GET THE DROPDOWN ELEMENTS
    var selectElement = document.getElementById('ds_droplist');
    var selectedOption = selectElement.options[selectElement.selectedIndex];
    var selectedType = selectedOption.getAttribute('data_type');

    // GET THE CONTAINER WHERE ADDITIONAL FIELDS WILL BE ADDED
    var additionalFieldsContainer = document.getElementById('additional-fields');

    // CLEAR PREVIOUS FIELDS
    additionalFieldsContainer.innerHTML = '';

    // LOAD ADDITIONAL FORM FIELDS
    if (selectedType == "Elastic") {  // For Elastic
        additionalFieldsContainer.innerHTML = `
        <div class="mb-3">
            <label for="ds_name" class="form-label">Data Source Name</label>
            <input type="text" class="form-control" id="ds_name" name="ds_name" required>
            <div id="textHelp" class="form-text">Give a unique name to your data source.</div>
        </div>
        <div class="mb-3">
            <label for="es_host" class="form-label">Host</label>
            <input type="text" class="form-control" id="es_host" name="es_host" required>
            <div id="textHelp" class="form-text">Elastic Host Name.</div>
        </div>
        <div class="mb-3">
            <label for="es_port" class="form-label">Port</label>
            <input type="text" class="form-control" id="es_port" name="es_port" required>
            <div id="textHelp" class="form-text">Elastic Port Number.</div>
        </div>
        <div class="mb-3">
            <label for="es_port" class="form-label">API Key</label>
            <div class="input-group">
                <input type="password" class="form-control" id="api_key" name="api_key" required>
                <button class="btn btn-secondary" type="button" id="togglePassword" onclick="toggleAPI()">
                    <i class="fa-solid fa-eye-slash"></i>
                </button>
            </div>
            <div id="textHelp" class="form-text">Elastic API Key.</div> 
        </div>
        <div class="mb-3">
            <label for="es_index" class="form-label">Index</label>
            <div class="d-flex align-items-center">
                <select id="es_index" name="es_index" class="form-select me-2" data-bs-toggle="dropdown" aria-expanded="false" required multiple>
                    <option value="">Use button to load indices</option>
                </select>
                <button class="btn btn-secondary ms-auto" type="button" id="esindex" onclick="loadElasticIndex()">
                    <i class="fa-solid fa-file-import"></i>
                </button>
            </div>
            <div id="textHelp" class="form-text">Elastic Index Name (Multi-Select).</div>
        </div>
        `;
    } else if (selectedType == "Security Onion") {
        additionalFieldsContainer.innerHTML = `
        <div class="mb-3">
            <label for="ds_name" class="form-label">Data Source Name</label>
            <input type="text" class="form-control" id="ds_name" name="ds_name" required>
            <div id="textHelp" class="form-text">Give a unique name to your data source.</div>
        </div>
        <div class="mb-3">
            <label for="es_host" class="form-label">Host</label>
            <input type="text" class="form-control" id="es_host" name="es_host" required>
            <div id="textHelp" class="form-text">Security Onion Elastic Host Name.</div>
        </div>
        <div class="mb-3">
            <label for="es_port" class="form-label">Port</label>
            <input type="text" class="form-control" id="es_port" name="es_port" required>
            <div id="textHelp" class="form-text">Security Onion Elastic Port Number.</div>
            </div>
        <div class="mb-3">
            <label for="es_port" class="form-label">API Key</label>
            <div class="input-group">
                <input type="password" class="form-control" id="api_key" name="api_key" required>
                <button class="btn btn-secondary" type="button" id="togglePassword" onclick="toggleAPI()">
                    <i class="fa-solid fa-eye-slash"></i>
                </button>
            </div>
            <div id="textHelp" class="form-text">Security Onion Elastic API Key.</div> 
        </div>
        `;

    }
    else if ((selectedType == "Zeek Connection Logs") || (selectedType == "Delta File") || (selectedType == "HTTP File") ||
    (selectedType == "DNS File") || (selectedType == "Custom File")) {
        additionalFieldsContainer.innerHTML = `
        <div class="mb-3">
            <label for="ds_name" class="form-label">Data Source Name</label>
            <input type="text" id="ds_name" name="ds_name" class="form-control" required>
            <div id="textHelp" class="form-text">Give a unique name to your data source.</div>
        </div>
        <div class="mb-3">
            <label for="raw_log_loc">Raw Log Location</label><br>
            <input type="text" id="raw_log_loc" name="raw_log_loc" class="form-control" required>
            <div id="textHelp" class="form-text">Raw Zeek file location.</div>
        </div>
        `;
    }

    //ADD THE DATA_TYPE TO THE REQUEST
    document.getElementById('data_type_field').value = selectedType;

    // Re-attach event listeners to the new input fields
    attachInputListeners();
    checkFields();  // Check fields immediately after updating

    getSelectedOptions();

}

function toggleAPI(){
    var selectElement = document.getElementById('api_key');
    var buttonValue = document.getElementById('togglePassword');

    console.log(selectElement)
    console.log(buttonValue)
    
    // TOGGLE THE TYPE ATTRIBUTE
    const type = selectElement.getAttribute("type") === "password" ? "text" : "password";
    selectElement.setAttribute("type", type);
    
    // TOGGLE THE ICON
    buttonValue.querySelector("i").classList.toggle("fa-eye");
    buttonValue.querySelector("i").classList.toggle("fa-eye-slash");
}

function loadElasticIndex(){

    //SET CURSOR
    document.body.style.cursor='wait';

    //GET INPUT VALUES
    const host = document.getElementById('es_host').value;
    const port = document.getElementById('es_port').value;
    const api = document.getElementById('api_key').value;
    const dt_val = "Elastic"

    $.ajax({
        url: "GetIndex",
        type: "GET",
        data: {
            host: host,
            port: port,
            api: api,
            data_type: dt_val
        },
        success: function(response) {
            document.body.style.cursor = 'default';
            $('#es_index').empty();

            // APPEND DEFAULT OPTION
            // POPULATE DROPDOWN WITH RECEIVED DATA
            $.each(response, function (index, item) {

                // ERROR HANDLING
                if (item.index_name==="beacon_huntress_error"){
                    console.log("BH Elastic Connection Error")
                    window.location.reload(true);
                } else {
                    // APPEND EACH INDEX TO THE DROP LIST
                    $('#es_index').append($('<option>', {
                        value: item.index_name,
                        text: item.index_name + '(' + item.cnt + ')'
                    })); 
                }
            });

            document.body.style.cursor = 'default';
        },
        //ADDITIONAL ERROR HANDLING
        error: function(error){
            try{
                console.log("Error:", error);

                document.body.style.cursor = 'default';
    
                window.location.reload(true);
            } catch (err) {
                console.error("Callback Error", err);
            }
        }
    })

}

function attachInputListeners() {
    const form = document.getElementById('new_ds');
    const inputs = form.querySelectorAll('input, select');

    inputs.forEach(input => {
        if (input.tagName === 'SELECT') {
            input.addEventListener('change', checkFields); // Use 'change' for select
        } else {
            input.addEventListener('input', checkFields); // Use 'input' for other fields
        }
    });
}

// Function to check if all required fields are filled
function checkFields() {
    const form = document.getElementById('new_ds');
    const allFilled = [...form.querySelectorAll('input, select')].every(input => {
        if (input.required) {
            if (input.tagName === "SELECT") {
                return input.value !== ""; // Check for non-empty selection
            }
            return input.value.trim() !== ""; // Check for non-empty text inputs
        }
        return true;
    });

    // Enable or disable the button based on whether all required fields are filled
    document.getElementById('btn_sub').disabled = !allFilled;
}

function getSelectedOptions() {
    const selectElement = document.getElementById("es_index");
    const selectedValues = Array.from(selectElement.selectedOptions).map(option => option.value);
    console.log("Selected options:", selectedValues);
}