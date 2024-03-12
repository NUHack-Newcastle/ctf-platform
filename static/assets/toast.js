const Toast = Swal.mixin({
    toast: true,
    position: 'top-end',
    showConfirmButton: false,
    timer: 3000,
    timerProgressBar: true,
    didOpen: (toast) => {
        toast.addEventListener('mouseenter', Swal.stopTimer)
        toast.addEventListener('mouseleave', Swal.resumeTimer)
    }
});

function retrieveAndShowStoredToast() {
    // Retrieve stored toast information
    const storedIcon = localStorage.getItem('toastIcon');
    const storedTitle = localStorage.getItem('toastTitle');

    // Check if there is stored toast information
    if (storedIcon && storedTitle) {
        // Show the toast with the retrieved information
        Toast.fire({
            icon: storedIcon, title: storedTitle
        });

        // Clear stored toast information
        localStorage.removeItem('toastIcon');
        localStorage.removeItem('toastTitle');
    }
}

function deferToast(icon, title){
    localStorage.setItem('toastIcon', icon);
    localStorage.setItem('toastTitle', title);
    location.reload();
}

$(function () {
    retrieveAndShowStoredToast();
});