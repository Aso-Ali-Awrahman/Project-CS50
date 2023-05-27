

function log_out() {
    if (confirm("Do you want to Log out?"))
        window.location.href = "/logout";

}


function show_recent_table(show) {
    if (show) {
        document.getElementById("recent-button").style.display = "none"
        document.getElementById("recent-div").style.display = "block"
    }
    else {
        document.getElementById("recent-div").style.display = "none"
        document.getElementById("recent-button").style.display = "block"
    }
}


function check_text() {
    let fields = ["field1", "field2", "field3"];

    for (let field of fields) {
        if (document.getElementById(field).value != '') {
            document.getElementById("save-button").disabled = false;
            return;
        }
    }
    document.getElementById("save-button").disabled = true;
}


function erase_text(field) {
    document.getElementById(field).value = "";
    check_text();
}


function show_edit_form(show, text) {
    if (show) {
        document.getElementById("edit_form").style.display = "block";
        document.getElementById("old_note").value = text;
        return;
    }
    document.getElementById("edit_form").style.display = "none";
}


function show_form(show, show_this='d', hide_this='d') {
    if (show) {
        document.getElementById(show_this).style.display = "block"
        document.getElementById(hide_this).style.display = "none"
    }
    else {
        document.getElementById('password_form').style.display = "none"
        document.getElementById('delete_account_form').style.display = "none"
    }
}