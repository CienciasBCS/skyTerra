const validations = (() => {

    const isRequired = value => value === '' ? false : true;

    const isBetween = (length, min, max) => length < min || length > max ? false : true;

    const showErrorMap = (errorId) => {
        let errorDiv = document.getElementById(errorId);
        errorDiv.classList.remove('d-none');

        return false
    }

    const hideErrors = () => {
        let errors = document.querySelectorAll('.alert-danger')
        errors.forEach(error => {
            error.classList.add('d-none');
        });
    }

    const showError = (errorDiv) => {
        errorDiv.classList.remove('is-valid');
        errorDiv.classList.add('is-invalid');

        return false
    }

    const validateError = () => {
        let errors = document.querySelectorAll('.form-control, .custom-file-input')
        errors.forEach(error => {
            error.classList.remove('is-invalid');
            error.classList.add('is-valid');
        });

    }

    return {
        isRequired, isBetween,
        showErrorMap, hideErrors, showError, validateError
    }
})()