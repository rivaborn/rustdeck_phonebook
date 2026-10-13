function showCopyTooltip(message) {
    const toast = document.createElement('div');
    toast.className = message === 'Copied!' ? 'toast' : 'toast toast-error';
    toast.setAttribute('role', 'status');
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('is-leaving');
        setTimeout(() => {
            toast.remove();
        }, 200);
    }, 1200);
}

function legacyCopy(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    let ok = false;
    try {
        ok = document.execCommand('copy');
    } catch (err) {
        ok = false;
    }
    document.body.removeChild(textarea);
    return ok;
}

function copyToClipboard(text) {
    // navigator.clipboard only exists in secure contexts (HTTPS/localhost);
    // fall back to execCommand when serving over plain HTTP on the LAN.
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text)
            .then(() => showCopyTooltip('Copied!'))
            .catch(() => {
                showCopyTooltip(legacyCopy(text) ? 'Copied!' : 'Copy failed');
            });
    } else {
        showCopyTooltip(legacyCopy(text) ? 'Copied!' : 'Copy failed');
    }
}
