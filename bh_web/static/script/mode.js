function changeTheme(keep) {
    val = localStorage.getItem('mode');

    if (keep === true) {
        if (val === "light") {
            $("body").toggleClass("dark-theme",false)
        }
        else {
            $("body").toggleClass("dark-theme",true);
        }

    }
    else {
        if (val === "light"){
            $("body").toggleClass("dark-theme",true);
            localStorage.setItem('mode', 'dark');
            //document.write(mode);
        }
        else {
            $("body").toggleClass("dark-theme",false);
            localStorage.setItem('mode', 'light');
            //document.write(mode);
        }
    }
}
