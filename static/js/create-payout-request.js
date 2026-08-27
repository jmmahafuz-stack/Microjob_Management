// Extracted from templates/payments/create_payout_request.html
function updatePayoutFields(method) {
    const bankFields = document.getElementById('bank_fields');
    if (method === 'Bank Account') {
        bankFields.style.display = 'block';
    } else {
        bankFields.style.display = 'none';
    }
}
