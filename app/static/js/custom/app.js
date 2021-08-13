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


const utilFunctions = (() => {

    const renderOfertasAgrupadasInfo = (data, tbBody) => {
        let status = ['Pre-dimensionamiento', 'Dimensionamiento']
        data.ofertas.forEach(oferta => {
            let row = document.createElement('tr');
            let entidadFed = document.createElement('td');
            let dateTime = document.createElement('td');
            let statusCompleted = document.createElement('td');

            entidadFed.innerText = oferta.cp.estado;
            dateTime.innerText = oferta.timestamp.split('T')[0];

            statusCompleted.innerText = status[oferta.status];

            row.appendChild(entidadFed)
            row.appendChild(dateTime)
            row.appendChild(statusCompleted)

            tbBody.appendChild(row)
        })
    }

    const updateInfoOfertasAgrupadas = async (btn, tbBody) => {
        tbBody.innerHTML = '';
        let licitacionId = btn.dataset.licitacion
        let resp = await fetch('../../../api/licitacion_info?' + new URLSearchParams({
            licitacionId
        }))
        let data = await resp.json()
        renderOfertasAgrupadasInfo(data, tbBody)
    }


    return { renderOfertasAgrupadasInfo, updateInfoOfertasAgrupadas }
})()