document.addEventListener('DOMContentLoaded', function() {
    const ibanDetails = document.getElementById('iban-details');
    const otherDetails = document.getElementById('other-details');
    const paymentTypeRadios = document.getElementsByName('payment_type');
    const form = document.querySelector('form');
    const donationPopup = document.getElementById('donationPopup');
    const donateButton = document.getElementById('donateButton');
    const skipButton = document.getElementById('skipButton');

    function togglePaymentDetails() {
        if (this.value === 'iban') {
            ibanDetails.style.display = 'grid';
            otherDetails.style.display = 'none';
            enableInputs(ibanDetails);
            disableInputs(otherDetails);
        } else {
            ibanDetails.style.display = 'none';
            otherDetails.style.display = 'grid';
            enableInputs(otherDetails);
            disableInputs(ibanDetails);
        }
    }

    function enableInputs(container) {
        container.querySelectorAll('input').forEach(input => input.disabled = false);
    }

    function disableInputs(container) {
        container.querySelectorAll('input').forEach(input => input.disabled = true);
    }

    paymentTypeRadios.forEach(radio => {
        radio.addEventListener('change', togglePaymentDetails);
    });

    // Initial state
    togglePaymentDetails.call(paymentTypeRadios[0]);

    // Show donation popup when form is submitted
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        donationPopup.classList.remove('hidden');
    });

    // Handle donate button click
    donateButton.addEventListener('click', function() {
        window.open('https://ko-fi.com/sammywriter', '_blank');
    });

    // Handle skip button click
    skipButton.addEventListener('click', function() {
        donationPopup.classList.add('hidden');
        form.submit();
    });
});
