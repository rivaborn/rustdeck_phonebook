function showCopyTooltip(message) {
    const tooltip = document.createElement('div');
    tooltip.textContent = message;
    tooltip.style.position = 'fixed';
    tooltip.style.bottom = '10px';
    tooltip.style.right = '10px';
    tooltip.style.backgroundColor = 'black';
    tooltip.style.color = 'white';
    tooltip.style.padding = '5px 10px';
    tooltip.style.borderRadius = '4px';
    tooltip.style.zIndex = '1000';
    tooltip.style.opacity = '1';
    tooltip.style.transition = 'opacity 0.5s';

    document.body.appendChild(tooltip);

    setTimeout(() => {
        tooltip.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(tooltip);
        }, 500);
    }, 1000);
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
