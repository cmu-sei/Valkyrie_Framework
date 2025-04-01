function navDropList(nav_name){

    console.log("HERE")
    console.log(nav_name)

    document.getElementById(nav_name).classList.toggle("active");
    dropdownContent = document.getElementById(nav_name).nextElementSibling;

    if (dropdownContent.style.display === "block") {
        dropdownContent.style.display = "none";
        localStorage.setItem(nav_name, false);
    } 
    else {
        dropdownContent.style.display = "block";
        localStorage.setItem(nav_name, true);
    };
};

function keepDropList(nav_name){

    val = localStorage.getItem(nav_name);

    console.log(nav_name)
    console.log(val)

    if (val === "true") {
        document.getElementById(nav_name).classList.toggle("active");
        dropdownContent = document.getElementById(nav_name).nextElementSibling;
        dropdownContent.style.display = "block";
    }
}
